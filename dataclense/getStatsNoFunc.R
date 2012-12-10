library(RMySQL)
library(ggplot2)
#library(reshape)
#library(data.table)
library(plyr)


#Setup Database Connection
drv <- dbDriver("MySQL")
con <- dbConnect(drv,dbname="mainStore",user="chuser")
#con <- dbConnect(drv,dbname="SampsonClose",user="root",password="adm3csva",host="127.0.0.1",port=3307)
#con <- dbConnect(drv,dbname="ch",user="chuser")
#con <- dbConnect(drv,dbname="transferTest",user="chuser")
#con <- dbConnect(drv,dbname="transferStore",user="root",password="Ex3lS4ga")

allHouses <-  dbGetQuery(con,statement="SELECT * FROM House WHERE address != 'ERROR-DATA'")
summaryData <- dbReadTable(con,"SummaryType")
calibrationData <- dbReadTable(con,"Sensor")
sensorType <- dbReadTable(con,"SensorType")

##Sensors we are interested in (For Yield Calculateions)
sensorTypeList <- subset(sensorType,
                         name=="Temperature" |
                         name=="Humidity" |
                         name=="Light PAR" |
                         name=="Light TSR" |
                         name=="CO2" |
                         name=="Air Quality" |
                         name=="VOC" |
                         name=="Battery Voltage" |
                         name=="Power")
#As Power Min / Max fit with Power (AVG) We are just repeating stuff here
#                         name=="Power Min" |
#                         name=="Power Max")

houseData <- data.frame(address = allHouses$address,
                        dbStart = NA,
                        dbEnd = NA,
                        dataStart = NA,
                        dataEnd = NA,
                        totalNodes = NA,
                        coNodes = NA,
                        yield = NA,
                        yieldSD = NA,
                        yieldMin = NA,
                        yieldMax = NA,
                        yieldDays = NA,
                        RLE = NA
                        )


i=16
THEHOUSE <- allHouses[i,]
hseName <- THEHOUSE$address

#processhouse <- function(hseName,houseData) {
 print("-------------------------------------------------------")
  print(paste("Processing House ",hseName))
  rowNo <- which(houseData$address == hseName)
  print(paste("Row Number is ",rowNo))
                                        #Get House
  houseQry <- paste("SELECT * FROM House WHERE address = '",hseName,"'",sep="")
  theHouse <- dbGetQuery(con,statement=houseQry)

  
  theHouse$sd <- as.POSIXlt(theHouse$startDate,tz="GMT")
  theHouse$ed <- as.POSIXlt(theHouse$endDate,tz="GMT")
  #theHouse$sd <- as.POSIXlt("2011-03-18",tz="GMT")
  #Locations
  locQry <- paste("SELECT * FROM Location as Loc ",
                  "LEFT OUTER JOIN Room as Room ",
                  "ON Loc.roomId = Room.id ",
                  "WHERE houseId =",theHouse$id,
                  " AND Room.name NOT LIKE 'PhyNet%' ",
                  " AND Room.name NOT IN ('Hot Water','Cold Water','Flow','Return','Hot','Cold','HotWater','ColdWater') ",
                  sep="")
  locations <- dbGetQuery(con,statement=locQry)
  locationIds <- paste(locations$id,collapse=",")
                                        #This Loc
                                        #thisLoc = locations[1,]

  print(paste("Expected Start ",theHouse$startDate,"Expected End",theHouse$endDate))
 
  houseData[rowNo,]$dbStart <- theHouse$startDate
  houseData[rowNo,]$dbEnd <- theHouse$endDate


dataQry <- paste("SELECT nodeId,type,locationId,DATE(time) as date,count(*) as count, min(time) as minTime,max(time) as maxTime, min(value) as minVal, max(value) as maxVal ",
                   "FROM Reading WHERE locationId IN (",
                   locationIds,") ",
                   " AND type IN (",paste(sensorTypeList$id,collapse=","),") ",
                   "GROUP BY nodeId,type,DATE(time)",
                   sep="")
#Fetch the data
houseSummary <- dbGetQuery(con,statement=dataQry)
#Add a time object so that makes sense to R
houseSummary$dt <- as.POSIXlt(houseSummary$date,tz="GMT")
houseSummary$DT <- as.Date(houseSummary$dt)
#And add some extra cols to hold summary information
houseSummary$countWithBad <- houseSummary$count

# ---- CALIBRATION SANITY PLOT ----
#Sanity check (Daily Plot)
## plt <- ggplot(subset(houseSummary,type==0))
## plt <- plt + geom_errorbar(aes(dt,ymin=minVal,ymax=maxVal))
## plt + facet_grid(nodeId~.)
## ggsave("SUMMARY_RAW_117.png")

#Merge with Calibration Data
tmp <- merge(houseSummary,calibrationData,by.x=c("nodeId","type"),by.y=c("nodeId","sensorTypeId"),all.x=TRUE)
#foo <- is.na(tmp$id)

#Add a dafualt calibration for nodes that have none
noCalibIdx <- which(is.na(tmp$id)==TRUE)
tmp[noCalibIdx,]$calibrationSlope <- 1
tmp[noCalibIdx,]$calibrationOffset <- 0

#Calibrate
tmp$calibMin <- (tmp$minVal * tmp$calibrationSlope) + tmp$calibrationOffset
tmp$calibMax <- (tmp$maxVal * tmp$calibrationSlope) + tmp$calibrationOffset

#Remove Data outside of given bands
tmp$badValue <- NA
#Temperatre
badRows <- which(tmp$type==0 & (tmp$calibMin < -10 | tmp$calibMax>50 ))
if (length(badRows) > 0){
  tmp[badRows,]$badValue <- TRUE
}
#Humidity
badRows <- which(tmp$type==2 & (tmp$calibMin < 0 | tmp$calibMax>100 ))
if (length(badRows) > 0){
  tmp[badRows,]$badValue <- TRUE
}
#Co2
badRows <- which(tmp$type==8 & (tmp$calibMin < 0 | tmp$calibMax>6000 ))
if (length(badRows) > 0){
  tmp[badRows,]$badValue <- TRUE
}
#TODO
#Rather than threshold by anything else, Threshold Electricity by something sensible
badRows <- which(tmp$type==6 & (tmp$calibMin< 0 | tmp$calibMax>5))
if (length(badRows) > 0){
  tmp[badRows,]$badValue <- TRUE
}

#Work out the correct SQL statement
sqlValues <- subset(tmp, badValue==TRUE)

if (nrow(sqlValues)>0){
  print("FETCHING BAD DATA")
  uniqueNode <- paste(unique(sqlValues$nodeId),collapse=",")
  uniqueDate <- paste(shQuote(unique(sqlValues$dt)),collapse=",")
  theQry = paste("SELECT * FROM Reading WHERE",
    " NodeId IN (",uniqueNode,")",
    " AND Date(time) IN (",uniqueDate,")",
    " AND type IN (",
    paste(sensorTypeList$id,collapse=","),
    ")",
    sep="")

  #Fetch all that data
  fixData <- dbGetQuery(con,statement=theQry)

  #Merge with Calibration Stuff
  fixCalib <- merge(fixData,calibrationData,by.x=c("nodeId","type"),by.y=c("nodeId","sensorTypeId"),all.x=TRUE)
  noCalibIdx <- which(is.na(fixCalib$id)==TRUE)
  fixCalib[noCalibIdx,]$calibrationSlope <- 1
  fixCalib[noCalibIdx,]$calibrationOffset <- 0

  #Calibrate
  fixCalib$calibValue <- (fixCalib$value * fixCalib$calibrationSlope) + fixCalib$calibrationOffset
  fixCalib$ts <- as.POSIXlt(fixCalib$time,tz="GMT")
  fixCalib$dt <- as.Date(fixCalib$ts)

  #For Debugging
  #tmpData <- fixCalib  
  ## plt <- ggplot(fixCalib)
  ## plt <- plt+geom_line(aes(ts,value,color="Uncalib"))
  ## #plt <- plt+geom_point(aes(ts,calibValue,color="Calib"))
  ## plt + facet_grid(type~nodeId,scales="free_y")
  ## ggsave("PRESTRIP.png")
  
  #Remove all the bad data
  fixCalib$badValue <- FALSE
  badRows <- which(fixCalib$type==0 & (fixCalib$calibValue < -10 | fixCalib$calibValue>50 ))
  if (length(badRows) > 0){
    fixCalib[badRows,]$badValue <- TRUE
    fixCalib[badRows,]$value = NA
  }
  badRows <- which(fixCalib$type==2 & (fixCalib$calibValue < 0 | fixCalib$calibValue>100 ))
  if (length(badRows) > 0){
    fixCalib[badRows,]$badValue <- TRUE
    fixCalib[badRows,]$value = NA
  }
  badRows <- which(fixCalib$type==8 & (fixCalib$calibValue < 0 | fixCalib$calibValue>6000 ))
  if (length(badRows) > 0){
    fixCalib[badRows,]$badValue <- TRUE
    fixCalib[badRows,]$value = NA
  }
  #We could do with removing any temperture / humidity data where the battery level is below XXX
  badRows <- which(fixCalib$type==6 & (fixCalib$calibValue < 0 | fixCalib$calibValue>5))
  if (length(badRows) > 0){
    fixCalib[badRows,]$badValue <- TRUE
    fixCalib[badRows,]$value = NA
  }

  ## -- SANITY CHECK ON STRIPPED DATA --
  ## #plt <- ggplot(subset(fixCalib,type==6))
  ## plt <- ggplot(fixCalib)
  ## plt <- plt+geom_line(aes(ts,value,color="Uncalib"))
  ## #plt <- plt+geom_point(aes(ts,calibValue,color="Calib"))
  ##   plt + facet_grid(type~nodeId,scales="free_y")
  ## #plt + facet_grid(type~.)
  ## ggsave("POSTSTRIP.png")

  #Summarise so its in the same format as the overall data
  fixSummary <- ddply(fixCalib,
                      .(nodeId,locationId,type,dt),
                      summarise,
                      minVal = min(value,na.rm=TRUE),
                      maxVal = max(value,na.rm=TRUE),
                      minTime = min(ts),
                      maxTime = max(ts),
                      count = length(value),
                      naCount =sum(is.na(value)),
                      tCount = length(value)-sum(is.na(value))
                      )

  #Remove the Infs put in by sumary functions where there is no data.
  fixSummary[which(is.infinite(fixSummary$minVal)==TRUE),]$minVal <- NA
  fixSummary[which(is.infinite(fixSummary$maxVal)== TRUE),]$maxVal <- NA
  
  #And Replace the original Values
  for (i in 1:nrow(fixSummary)){
    thisRow <- fixSummary[i,]
    rowIdx <- which(houseSummary$nodeId == thisRow$nodeId & houseSummary$locationId ==thisRow$locationId & houseSummary$type == thisRow$type & houseSummary$DT == thisRow$dt)
    houseSummary[rowIdx,]$count <- thisRow$tCount
    houseSummary[rowIdx,]$countWithBad <- thisRow$count
    houseSummary[rowIdx,]$minVal <- thisRow$minVal
    houseSummary[rowIdx,]$maxVal <- thisRow$maxVal
    #houseSummary[rowIdx,]$minTime <- as.POSIXlt(thisRow$minTime,tz="GMT")
    #houseSummary[rowIdx,]$maxTime <- thisRow$maxTime
  }
  print("Data Cleaned")
} #End of IF Statement

# --------- EOF NEW STUFF ---------

#Work out the first and last samples so we can get yields for each node / Day
#print("FIRST AND LAST SAMPLES")
#First and Last Samples
firstSample <- as.character(min(houseSummary$dt))
lastSample <- as.character(max(houseSummary$dt))
  houseData[rowNo,]$dataStart <- firstSample
  houseData[rowNo,]$dataEnd <- lastSample

# Error check, if there is no start date / end date in the database, We use the date of the first and last sample
hSd <- as.POSIXlt(theHouse$sd,tz="GMT")
 if (is.na(hSd)) {
   hSd <- as.POSIXlt(firstSample,tz="GMT")
 }
hEd <- as.POSIXlt(theHouse$ed,tz="GMT")
 if (is.na(hEd)){
   hEd <- as.POSIXlt(lastSample,tz="GMT")
 }

#  -- SANITY CHECK, WHAT THE CLEAN DTA LOOKS LIKELets take a look at the values
## plt <- ggplot(houseSummary)
## plt <- plt+geom_step(aes(dt,count,color=factor(type)))
## plt <- plt+geom_point(aes(dt,count,color=factor(type)))
## plt <- plt + opts(title="Sample Count By Node / Sensor")
## plt <- plt + ylab("Readings")
## plt <- plt + xlab("Date")
## plt + facet_grid(nodeId~.)
## ggsave("CleanCount.png")

#Calculate the Yield per Node / Sensor / Day
houseSummary$dayYield <- (houseSummary$count / 288)*100.0   #This is important

#So we can now drop all this inforamtion into the database
dayCountId <-  summaryData[which(summaryData$name == "Day Count"),]$id
tmpInsert <- data.frame(time=houseSummary$dt,
                        nodeId=houseSummary$nodeId,
                        sensorTypeId=houseSummary$type,
                        summaryTypeId=dayCountId,
                        locationId=houseSummary$locationId,
                        value=houseSummary$count
                        )
# --==--== DONE TO HERE --==--==--=
dbWriteTable(con,"Summary",tmpInsert,append=TRUE,row.name=FALSE)
#Averge out the Yields by Node / Location / Date (IE Combine all Sensors together)
avgYield <- ddply(houseSummary,
                  .(dt,nodeId,locationId),
                  summarise,
                  min = min(dayYield),
                  max = max(dayYield),
                  dayYield=mean(dayYield))

plt <- ggplot(houseSummary,aes(dt,dayYield))
#plt <- plt+geom_step(data=avgCount)
plt <- plt+geom_point(data=avgYield)
plt <- plt+geom_step(aes(color=factor(type)))
plt <- plt+geom_point(aes(color=factor(type)))
plt <- plt + opts(title=paste("Yield by Node / Sensor ",hseName))
plt <- plt + ylab("% Yield (All sensors)")
plt <- plt+xlab("Date")
plt <- plt + geom_vline(data=theHouse,aes(xintercept=hSd))
plt <- plt + geom_vline(data=theHouse,aes(xintercept=hEd))
plt + facet_grid(nodeId~.)
ggsave("YieldDayNode.png")


# ---- Store The summary Data for these in the DB ---------------

## --- TODO  FIX How to store thiss stuff
dayCountId = summaryData[which(summaryData$name == "Day Count"),]$id
dayCountCleanId = summaryData[which(summaryData$name == "Day Count (Clean)"),]$id
# Raw Counts
countInsert <- data.frame(time=houseSummary$dt,
                          nodeId=houseSummary$nodeId,
                          sensorTypeId=houseSummary$type,
                          summaryTypeId=NA,
                          locationId=houseSummary$locationId,
                          value=houseSummary$countWithBad
                          )

countInsert$summaryTypeId <- dayCountId
dbWriteTable(con,"Summary",countInsert,append=TRUE,row.name=FALSE)

#Clean counts
countInsert <- data.frame(time=houseSummary$dt,
                          nodeId=houseSummary$nodeId,
                          sensorTypeId=houseSummary$type,
                          summaryTypeId=dayCountCleanId,
                          locationId=houseSummary$locationId,
                          value=houseSummary$count
                          )

dbWriteTable(con,"Summary",countInsert,append=TRUE,row.name=FALSE)

#-------------- CALCUATE YIELD --------------------------------

#We want to remove the first and last days from the dataset
stripped <- subset(houseSummary,dt>hSd & dt <hEd)

#plotThis (SANITY)
#Start and End Dates for Yield
ySd <- hSd + 60*60*24
yEd <- hEd #- 60*60*24
#Non Inclusive of the last date Ie Sd >= dT < Ed
yieldDuration <- as.real(yEd - ySd) 
yieldExpected <- yieldDuration * 288

plt <- ggplot(stripped,aes(dt,dayYield,color=type))
plt <- plt + geom_point()
plt <- plt + geom_step()
plt <- plt + geom_vline(data=theHouse,aes(xintercept=hSd))
plt <- plt + geom_vline(data=theHouse,aes(xintercept=hEd))
plt + facet_grid(nodeId~.)



#Summarise the lot
yieldSummary <- ddply(stripped,
                      .(nodeId,type),
                      summarise,
                      count=sum(count),
                      countBad=sum(countWithBad),
                      ninetyCount = length(which(dayYield >= 90))
                      )
yieldSummary$expected <-  yieldExpected
yieldSummary$sensorYield <- (yieldSummary$count / yieldExpected) * 100.0

#And Yield per Node
allSensors <- ddply(stripped,
                    .(nodeId),
                    summarise,
                    count=sum(count),
                    sensorCount = length(unique(type)),
                    ninetyCount = length(which(dayYield >= 90))
                    )
allSensors$expected <- yieldExpected * allSensors$sensorCount
allSensors$yield <- (allSensors$count / allSensors$expected) * 100.0

plt <- ggplot(yieldSummary)
plt <- plt+geom_bar(aes(factor(nodeId),
                        count,
                        color=factor(type)),
                    position="dodge")
plt <- plt + geom_hline(aes(yintercept=expected))
plt

plt <- ggplot(yieldSummary)
plt <- plt+geom_bar(aes(factor(nodeId),
                        sensorYield,
                        color=factor(type)),
                    position="dodge")
plt <- plt + geom_hline(aes(yintercept=90,color="red"))
plt

#And we can work out the final Expected Yield Here
totalSensors <- sum(allSensors$sensorCount) #No of Sensors
totalSamples <- sum(allSensors$count)
deployExpected <- yieldExpected * totalSensors #Daily Expcted * No Sensors
finalYield <- (totalSamples / deployExpected) * 100

##   ## nodeSum <- ddply(houseSummary,
##   ##                   .(nodeId,type),
##   ##                   summarise,
##   ##                   #days=length(dt),
##   ##                   count=sum(count),
##   ##                   avgDY = mean(dayYield),
##   ##                   firstSample = min(dt),
##   ##                   lastSample = max(dt)
##   ##                   )

## #Plotting (As a Sanity Check)
## #plt <- ggplot(houseSummary)
## #plt <- plt + geom_point(aes(dt,count,color=factor(type)))
## #plt <- plt+ opts(title="Sample count per Sensortype / Location")
## #plt + facet_grid(locationId~.)
## #plt + facet_grid(nodeId~.)

## #And another
## #sanity <- subset(houseSummary,count > 300)
## #plt <- ggplot(sanity)
## #plt <- plt + geom_point(aes(dt,count,color=factor(type)))
## #plt + facet_grid(locationId~.)
## ###ggsave("Extras.png")

## ## # Error check, if there is no start date / end date in the database, We use the date of the first and last sample
## ## hSd <- as.POSIXlt(theHouse$sd,tz="GMT")
## ##  if (is.na(hSd)) {
## ##    hSd <- as.POSIXlt(firstSample,tz="GMT")
## ##  }
## ## hEd <- as.POSIXlt(theHouse$ed,tz="GMT")
## ##  if (is.na(hEd)){
## ##    hEd <- as.POSIXlt(lastSample,tz="GMT")
## ##  }



## #---- FORGET IGNORING THIS FOR A MOMENT ----------

## ## #Dont Calculate Yield for the First or last Days (Strip this Data)
## ##   houseSummary$ignoreYield <- TRUE
## ##   #idxes <- which(houseSummary$dt > theHouse$sd & houseSummary$dt < theHouse$ed)
## ##   idxes <- which(houseSummary$dt > hSd & houseSummary$dt < hEd)
## ##   houseSummary$ignoreYield[idxes] <- FALSE
## ##   houseSummary <- subset(houseSummary,ignoreYield == FALSE)

##   #print("CALCULATING YIELDS")
##   #Calulate Yield Percentages per Day (Which at the moment we need to eyeball to get Elenas RLE)
##   #houseSummary$dayYield <- (houseSummary$count / 288) * 100


  
##   ## yieldCount <- ddply(houseSummary,
##   ##                     .(dt,nodeId,locationId),
##   ##                     summarise,
##   ##                     count = mean(count),
##   ##                     min = min(dayYield),
##   ##                     max = max(dayYield),
##   ##                     avg = mean(dayYield)
##   ##                     )

##   ## plt <- ggplot(yieldCount)                                        
##   ## #plt <- plt +geom_point(aes(dt,count,fill="count"))
##   ## plt <- plt +geom_point(aes(dt,avg,color=factor(locationId)))
##   ## plt <- plt + geom_errorbar(aes(dt,ymin=min,ymax=max))
##   ## #plt + facet_grid(nodeId~.)
##   ## plt <- plt + opts(title=paste("Daily Yield by Node ",hseName))
##   ## plt <- plt + ylab("Daily Yield (Avg of All Sensors)")
##   ## plt <- plt+xlab("Date")
##   ## plt <- plt + geom_vline(data=theHouse,aes(xintercept=hSd))
##   ## plt <- plt + geom_vline(data=theHouse,aes(xintercept=hEd))
##   ## plt + facet_grid(nodeId~.)
##   ## ggsave("DailyYield.png")

##   ## #A bit of an explore here as node 5636 looks a bit wierd
##   ## plt <- ggplot(subset(houseSummary,nodeId==5636))
##   ## plt <- plt+geom_point(aes(dt,count,color=type))
##   ## plt + facet_grid(type~.)


##   ## #Summarise this so we just get a daily yield per Node
##   ## yieldSum <- ddply(houseSummary,
##   ##                   .(dt),
##   ##                   summarise,
##   ##                   sensors=length(dt),
##   ##                   yield=mean(dayYield),
##   ##                   stYield = sd(dayYield)
##   ##                   )

##    #plt <- ggplot(yieldSum)
##    #plt <- plt+geom_point(aes(dt,yield))
##    #plt 
##    #plt + facet_grid(nodeId~.)

##    print("SUMMARISING DAYS")

## #allDays <- data.frame(date=seq(as.POSIXlt(theHouse$startDate,tz="GMT"),as.POSIXlt(theHouse$endDate,tz="GMT"),by="day"))
##   # ----- RUN LENGHT ENCODING OF THE DAILY YIELD ------
##   allDays <- data.frame(date=seq(hSd,hEd,by="day")) #Get a new frame with all expected days (start-end)
##   yieldSum$DT <- as.Date(yieldSum$dt) 
##   allDays$DT <- as.Date(allDays$date)
##   allYield <- merge(allDays,yieldSum,"DT") #Merge with the daily yield 
##   allBins <- cut(allYield$yield,breaks=c(0,90,110),labels=c("<90","90+"),include.upper=TRUE) #Bin 
##   runLength <- rle(as.character(allBins)) #Do Rle
##   print(paste(runLength$lengths,collapse=","))
##   print(paste(runLength$values,collapse=","))

##   ninetyDays <- length(which(allBins == "90+")) #Count yield + 90
##   houseData[rowNo,]$RLE <- ninetyDays
##   print(paste("Days about 90+ Yield",ninetyDays))

##   #We may need to Insert the Daily Yield (Per Node) in the Database Too.
##   yieldSumNode <- ddply(houseSummary,
##                         .(dt,nodeId,locationId),
##                         summarise,
##                         yield=mean(dayYield)
##                         )


##    yieldId = summaryData[which(summaryData$name == "Yield"),]$id
##    yieldNodeInsert <- data.frame(time=yieldSumNode$dt,
##                                  nodeId=yieldSumNode$nodeId,
##                                  #sensorTypeId=NA,
##                                  summaryTypeId=yieldId,
##                                  locationId=yieldSumNode$locationId,
##                                  value=yieldSumNode$yield
##                                  )

##    dbWriteTable(con,"Summary",yieldNodeInsert,append=TRUE,row.name=FALSE)
                                 
## #strLength <- paste(runLength, collapse=",")
## #print(runLength)
## #houseData[rowNo,]$RLE <- strLength
 
## #  allDays$value <- 25

 
##   ## allDays$dt <- as.POSIXlt(allDays$date,tz="GMT")
##   ## merge(allDays,yieldSum,by="dt")
##  ## plt <- ggplot(yieldSum,aes(dt,yield))
##  ## plt <- plt+geom_point(color="red")
##  ## plt <- plt+geom_line(color="red")
##  ## plt <- plt+geom_errorbar(aes(ymin=yield-stYield,ymax=yield+stYield))
##  ## plt <- plt+opts(title="Average Daily Yield + SD")
##  ## plt <- plt + geom_vline(data=theHouse,aes(xintercept=hSd,alpha=0.5))
##  ## plt <- plt + geom_vline(data=theHouse,aes(xintercept=hEd))
##  ## #plt <- plt+geom_linerange(data=allDays,aes(x=date,ymin=0,ymax=90),color="green")
##  ## plt
##  ## #ggsave("Avg_Day_Yield.png")

##  ##  plt <- ggplot(houseSummary)
##  ##  plt <- plt+geom_point(aes(x=dt,y=dayYield))
##  ##  plt <- plt+geom_linerange(data=allDays,aes(x=date,ymin=0,ymax=90),color="red")
##  ##  plt <- plt + opts(title=paste("Daily Yield for",theHouse$address))
##  ##  plt <- plt + geom_vline(data=theHouse,aes(xintercept=hSd,alpha=0.5))
##  ##  plt <- plt + geom_vline(data=theHouse,aes(xintercept=hEd))
##  ##  plt + geom_hline(y=90)
##   #ggsave("Dailyyield_All.png")

##   #Now do some of the Magic Summarisation Function(TM) <thanks to Hadley>
##   # Caluclate Yield for each node
##   nodeSum <- ddply(houseSummary,
##                     .(nodeId,type),
##                     summarise,
##                     #days=length(dt),
##                     count=sum(count),
##                     avgDY = mean(dayYield),
##                     firstSample = min(dt),
##                     lastSample = max(dt)
##                     )

## #Plot this
## plt <- ggplot(nodeSum)
## plt <- plt + geom_bar(aes(factor(nodeId),count,fill=factor(type)),position="dodge")
## plt <- plt + opts(title="Total Deployment Samples by Node / Sensor")
## plt

##   #houseSum$startDate <- min(houseSummary$dt)
##   #houseSum$endDate <- max(houseSummary$dt)
##   #houseSum$startDate <- theHouse$sd
##   #houseSum$endDate <- theHouse$ed
##   rs = nrow(houseSum)
##   print(paste("Number of Rows ",nrow(houseSum)))
##   if (rs == 0){
##     print("No Data here")
##     return(houseData)
##   }

##                                         #Create Calculate the Yield per sensor


##   #if (is.na(theHouse$ed)) duration <- hEd - hSd else duration <- theHouse$ed - theHouse$sd - 1 #Offset as Last day is included

##   duration <- hEd - hSd 
##   expected <- as.real(duration)  * 288 
##   houseSum$duration <- duration
##   houseSum$expected <- expected
##   houseSum$yield <- (houseSum$count / houseSum$expected) * 100.0


##   plt <- ggplot(houseSum)
## plt <- plt + geom_bar(aes(factor(nodeId),yield,fill=factor(type)),position="dodge")
## plt <- plt + opts(title="Total Deployment Yield by Node / Sensor")
## plt

##  #And where we actually have samples
##   dataDuration <- max(houseSum$lastSample) - min(houseSum$firstSample) 
##   dataExpected <- as.real(dataDuration) * 288
##   houseSum$dataYield <- (houseSum$count / dataExpected) * 100
 
##   summary(houseSum)

## totExpected <- sum(houseSum$expected)
## totSamples <- sum(houseSum$count)
## totYield <- (totSamples / totExpected) * 100.0

## #Node Counts
## #CO2 Nodes
## allNodes <- length(unique(houseSum$nodeId))
## coNodes <- length(subset(houseSum,type==8)$nodeId)

## houseData[rowNo,]$totalNodes <- allNodes
## houseData[rowNo,]$coNodes <- coNodes
## houseData[rowNo,]$yield <- totYield
## houseData[rowNo,]$yieldMin <- min(houseSum$yield)
## houseData[rowNo,]$yieldMax <- max(houseSum$yield)
## houseData[rowNo,]$yieldSD <- sd(houseSum$yield)
##  houseData[rowNo,]$yieldDays <- mean(houseSum$dataYield)

## print (paste("Total Yield Is ",totYield))

#plt <- ggplot(houseSum)
#plt <- plt + geom_point(aes(factor(nodeId),yield,color=factor(type)))
#plt +  coord_flip()
##ggsave("AllYields.png")
#return(houseData)
#}



#Battery Check
## theQry <- "SELECT * FROM Reading WHERE nodeId=197 AND type=6 AND time>'2011-12-01' AND time < '2012-04-01'" 
## batData <- dbGetQuery(con,statement=theQry)
## batData$dt <- as.POSIXlt(batData$time)

## plt <- ggplot(batData)
## plt <- plt + geom_point(aes(dt,value))
## plt

##Temporoary Query
#theQry = paste("SELECT * FROM Reading WHERE locationId IN (",locationIds,") AND type = 0",sep="")
## theQry = "SELECT * FROM Reading WHERE nodeId = 249028604 AND locationId IS NOT NULL"
## tmpData <- dbGetQuery(con,theQry)
## tmpData$ts <- as.POSIXlt(tmpData$time)

## plt <- ggplot(tmpData)
## plt <- plt+geom_point(aes(ts,value,color=factor(type)))
## plt + facet_grid(locationId~nodeId)

## summary(tmpData)


## i <- 17

## print(allHouses)

##   THEHOUSE <- allHouses[i,]
##   print(THEHOUSE)
##   hseName <- THEHOUSE$address
##     houseData <- processhouse(hseName,houseData)

## print(houseData)


#for (i in 17:17){


## for (i in 2:nrow(allHouses)){
##   THEHOUSE <- allHouses[i,]
##   print(THEHOUSE)
##   hseName <- THEHOUSE$address
##   print(paste("Deaing with ",hseName))
##   #if (i != 14){ #Main Data (Brays)
##   if (i!= 15){ # Seocond Data Brays
##     print(paste("--> Processing Data with ",hseName))
##     houseData <- processhouse(hseName,houseData)
##   }
##   write.table(houseData, "allSummary.csv", sep=",")
## }

## #print(houseData)

## write.table(houseData, "allSummary.csv", sep=",")
