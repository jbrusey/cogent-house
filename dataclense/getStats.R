library(RMySQL)
library(ggplot2)
library(plyr)


#Setup Database Connection
drv <- dbDriver("MySQL")
con <- dbConnect(drv,dbname="mainStore",user="root",password="Ex3lS4ga")
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

print ("ALL HOUSES")
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
                        totalSamples = NA,
                        yieldDays = NA
                        )


i=3
THEHOUSE <- allHouses[i,]
hseName <- THEHOUSE$address

processhouse <- function(hseName,houseData) {
 print("-------------------------------------------------------")
  print(paste("Processing House ",hseName))
  rowNo <- which(houseData$address == hseName)
  print(paste("Row Number is ",rowNo))
                                        #Get House
  houseQry <- paste("SELECT * FROM House WHERE address = '",hseName,"'",sep="")
  theHouse <- dbGetQuery(con,statement=houseQry)

  theHouse$sd <- as.POSIXlt(theHouse$startDate,tz="GMT")
  theHouse$ed <- as.POSIXlt(theHouse$endDate,tz="GMT")
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

  print("BAD DATA FETCHED-- CALIBRATING")
  #Merge with Calibration Stuff
  fixCalib <- merge(fixData,calibrationData,by.x=c("nodeId","type"),by.y=c("nodeId","sensorTypeId"),all.x=TRUE)
  noCalibIdx <- which(is.na(fixCalib$id)==TRUE)
  rowcount <- length(noCalibIdx)
  if (rowcount >0){
    fixCalib[noCalibIdx,]$calibrationSlope <- 1
    fixCalib[noCalibIdx,]$calibrationOffset <- 0
  }
  
  #Calibrate
  fixCalib$calibValue <- (fixCalib$value * fixCalib$calibrationSlope) + fixCalib$calibrationOffset
  fixCalib$ts <- as.POSIXlt(fixCalib$time,tz="GMT")
  fixCalib$dt <- as.Date(fixCalib$ts)

  print("Removing Bad Values")
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
  print("Removing Infintae Dates")
  #Remove the Infs put in by sumary functions where there is no data.
  infDates <- which(is.infinite(fixSummary$minVal)==TRUE)
  if (length(infDates)>0){
    fixSummary[which(is.infinite(fixSummary$minVal)==TRUE),]$minVal <- NA
    fixSummary[which(is.infinite(fixSummary$maxVal)== TRUE),]$maxVal <- NA
  }
  print("Replaing Values")
  #And Replace the original Values
  for (i in 1:nrow(fixSummary)){
    thisRow <- fixSummary[i,]
    rowIdx <- which(houseSummary$nodeId == thisRow$nodeId & houseSummary$locationId ==thisRow$locationId & houseSummary$type == thisRow$type & houseSummary$DT == thisRow$dt)
    houseSummary[rowIdx,]$count <- thisRow$tCount
    houseSummary[rowIdx,]$countWithBad <- thisRow$count
    houseSummary[rowIdx,]$minVal <- thisRow$minVal
    houseSummary[rowIdx,]$maxVal <- thisRow$maxVal
  }
  print("Data Cleaned")
} #End of IF Statement

# --------- EOF NEW STUFF ---------
print("Calculating Yields")
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

#Calculate the Yield per Node / Sensor / Day
houseSummary$dayYield <- (houseSummary$count / 288)*100.0   #This is important
 
print("Averaging by Node / Location")
#Averge out the Yields by Node / Location / Date (IE Combine all Sensors together)
avgYield <- ddply(houseSummary,
                  .(dt,nodeId,locationId),
                  summarise,
                  min = min(dayYield),
                  max = max(dayYield),
                  dayYield=mean(dayYield))

dayCountId = summaryData[which(summaryData$name == "Day Count"),]$id
dayCountCleanId = summaryData[which(summaryData$name == "Day Count (Clean)"),]$id
 print(paste("Day Count Id ",dayCountId))
  print(paste("Day Count Clean Id ",dayCountCleanId))
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

 print("Counting Clean Samples")
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
 print ("Stripping Ends of Deployment")
stripped <- subset(houseSummary,dt>hSd & dt <hEd)

if (nrow(stripped) == 0){
  print("NO ROWS IN STRIPPED DATA")
  return(houseData)
}
 
#Start and End Dates for Yield
ySd <- hSd + 60*60*24
yEd <- hEd #- 60*60*24
#Non Inclusive of the last date Ie Sd >= dT < Ed
yieldDuration <- as.real(yEd - ySd) 
yieldExpected <- yieldDuration * 288

 print ("Summarising Yields (node/type)")
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
  print ("Summarising Yields (node)")
allSensors <- ddply(stripped,
                    .(nodeId),
                    summarise,
                    count=sum(count),
                    sensorCount = length(unique(type)),
                    ninetyCount = length(which(dayYield >= 90))
                    )
allSensors$expected <- yieldExpected * allSensors$sensorCount
allSensors$yield <- (allSensors$count / allSensors$expected) * 100.0

dailySummary <- ddply(stripped,
                     .(dt,nodeId),
                      summarise,
                      count=sum(count),
                      sensorCount=length(unique(type)),
                      sensorCounts=length(type)
                      )

dailySummary <- ddply(stripped,
                      .(dt),
                      summarise,
                      count=sum(count),
                      nodes=length(nodeId),
                      sensors=length(type)
                      )

dailySummary$expected <-  288 * dailySummary$sensors
dailySummary$yield <- dailySummary$count / dailySummary$expected * 100
ninetyDays <- length(which(dailySummary$yield > 90))
 
 
totalNodes <- length(unique(yieldSummary$nodeId))
co2Nodes <- length(unique(subset(yieldSummary,type==8)$nodeId))

houseData[rowNo,]$totalNodes <- totalNodes
houseData[rowNo,]$coNodes <- co2Nodes
houseData[rowNo,]$yieldMin <- min(allSensors$yield)
houseData[rowNo,]$yieldMax <- max(allSensors$yield)
houseData[rowNo,]$yieldSD <- sd(allSensors$yield)

print("Calculating Final Yield")
#And we can work out the final Expected Yield Here
totalSensors <- sum(allSensors$sensorCount) #No of Sensors
totalSamples <- sum(allSensors$count)
deployExpected <- yieldExpected * totalSensors #Daily Expcted * No Sensors
finalYield <- (totalSamples / deployExpected) * 100
print(paste("Final Yield for Deployment ",finalYield,"%"))

houseData[rowNo,]$yieldDays <- ninetyDays
houseData[rowNo,]$totalSamples <- totalSamples
houseData[rowNo,]$yield <- finalYield
return(houseData)
}

print ("House List")
print(allHouses)


for (i in 2:nrow(allHouses)){
#for (i in 1:2){
  THEHOUSE <- allHouses[i,]
  print(THEHOUSE)
  hseName <- THEHOUSE$address
  print(paste("Deaing with ",hseName))
  #if (i != 14){ #Main Data (Brays)
  if (i!= 15){ # Seocond Data Brays
    print(paste("--> Processing Data with ",hseName))
    houseData <- processhouse(hseName,houseData)
  }
  write.table(houseData, "allSummary.csv", sep=",")
}

print(houseData)

write.table(houseData, "allSummary.csv", sep=",")
