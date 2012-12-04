library(RMySQL)
library(ggplot2)
#library(reshape)
#library(data.table)
library(plyr)


#Setup Database Connection
drv <- dbDriver("MySQL")
#con <- dbConnect(drv,dbname="mainStore",user="chuser")
con <- dbConnect(drv,dbname="SampsonClose",user="root",password="adm3csva",host="127.0.0.1",port=3307)
#con <- dbConnect(drv,dbname="ch",user="chuser")
#con <- dbConnect(drv,dbname="transferTest",user="chuser")
#con <- dbConnect(drv,dbname="transferStore",user="root",password="Ex3lS4ga")


#args <- commandArgs(TRUE)
#THEHOUSE <- args[1]

#THEHOUSE <- "1 Avon Road"
#THEHOUSE <- "5 Elm Road"

allHouses <-  dbGetQuery(con,statement="SELECT * FROM House WHERE address != 'ERROR-DATA'")
summaryData <- dbReadTable(con,"SummaryType")
#15 Is Brays (KLeave for the moment)
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

## i <- 2

## allHouses <-  dbGetQuery(con,statement="SELECT * FROM House")

## for (i in 1:length(allHouses)){
## #for (i in 1:3){
##   THEHOUSE <- allHouses[i,]
##   print(THEHOUSE)
##   hseName <- THEHOUSE$address
##   houseData <- processhouse(hseName,houseData)
## }

i=1

THEHOUSE <- allHouses[i,]
hseName <- THEHOUSE$address
#hseName <- "5 Elm Road"
#houseData <- processhouse(hseName,houseData)

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


dataQry <- paste("SELECT nodeId,type,locationId,DATE(time) as date,count(*) as count, min(time) as minTime,max(time) as maxTime ",
                   "FROM Reading WHERE locationId IN (",
                   locationIds,") ",
                   "AND NOT type in (4,5, 6) ",
                   "GROUP BY nodeId,type,DATE(time)",
                   sep="")


houseSummary <- dbGetQuery(con,statement=dataQry)

#Add a time object so that makes sense toi R
  houseSummary$dt <- as.POSIXlt(houseSummary$date,tz="GMT")


# ------------------ GET A SUMMARY OF SAMPLE COUNT PER DAY ------------------

#Try to combine these in a more sensible way so the plot is a little cleaner
avgCount <- ddply(houseSummary,
                  .(dt,nodeId,locationId),
                  summarise,
                  min = min(count),
                  max = max(count),
                  avg = mean(count))


plt <- ggplot(avgCount)
#plt <- ggplot(subset(avgCount,dt<as.POSIXlt("2010-11-20",tz="GMT")))
plt <- plt +geom_point(aes(dt,avg,color=locationId))
plt <- plt + opts(title=paste("Tx Count by Node ",hseName))
plt <- plt + geom_vline(data=theHouse,aes(xintercept=sd))
plt <- plt + geom_vline(data=theHouse,aes(xintercept=ed))
#plt

dayCountId = summaryData[which(summaryData$name == "Day Count"),]$id

#Try to store the counts in the Database
 countInsert <- data.frame(time=avgCount$dt,
                           nodeId=avgCount$nodeId,
                           sensorTypeId=NA,
                           summaryTypeId=dayCountId,
                           locationId=avgCount$locationId,
                           value=avgCount$avg
                           )

dbWriteTable(con,"Summary",countInsert,append=TRUE,row.name=FALSE)

# ---------------------- DAILY COUNT DONE --------------------------------
 
#Minimum and Maximum Sensor Reading

#plt + facet_grid(locationId~.)
## # plt + facet_grid(nodeId~.)
#ggsave("TxByNodeSC26.png")

#-------------- CALCUATE YIELD --------------------------------

print("FIRST AND LAST SAMPLES")
#First and Last Samples
firstSample <- as.character(min(avgCount$dt))
lastSample <- as.character(max(avgCount$dt))
  houseData[rowNo,]$dataStart <- firstSample
  houseData[rowNo,]$dataEnd <- lastSample

#Plotting (As a Sanity Check)
#plt <- ggplot(houseSummary)
#plt <- plt + geom_point(aes(dt,count,color=factor(type)))
#plt <- plt+ opts(title="Sample count per Sensortype / Location")
#plt + facet_grid(locationId~.)
#plt + facet_grid(nodeId~.)

#And another
#sanity <- subset(houseSummary,count > 300)
#plt <- ggplot(sanity)
#plt <- plt + geom_point(aes(dt,count,color=factor(type)))
#plt + facet_grid(locationId~.)
###ggsave("Extras.png")

# Error check, if there is no start date / end date in the database, We use the date of the first and last sample
hSd <- as.POSIXlt(theHouse$sd,tz="GMT")
 if (is.na(hSd)) {
   hSd <- as.POSIXlt(firstSample,tz="GMT")
 }
hEd <- as.POSIXlt(theHouse$ed,tz="GMT")
 if (is.na(hEd)){
   hEd <- as.POSIXlt(lastSample,tz="GMT")
 }


#Dont Calculate Yield for the First or last Days (Strip this Data)
  houseSummary$ignoreYield <- TRUE
  #idxes <- which(houseSummary$dt > theHouse$sd & houseSummary$dt < theHouse$ed)
  idxes <- which(houseSummary$dt > hSd & houseSummary$dt < hEd)
  houseSummary$ignoreYield[idxes] <- FALSE
  houseSummary <- subset(houseSummary,ignoreYield == FALSE)

  print("CALCULATING YIELDS")
  #Calulate Yield Percentages per Day (Which at the moment we need to eyeball to get Elenas RLE)
  houseSummary$dayYield <- (houseSummary$count / 288) * 100
  
  
  

  #Summarise this so we just get a daily yield per Node
  yieldSum <- ddply(houseSummary,
                    .(dt),
                    summarise,
                    nodes=length(dt),
                    yield=mean(dayYield),
                    stYield = sd(dayYield)
                    )


   print("SUMMARISING DAYS")

#allDays <- data.frame(date=seq(as.POSIXlt(theHouse$startDate,tz="GMT"),as.POSIXlt(theHouse$endDate,tz="GMT"),by="day"))
  # ----- RUN LENGHT ENCODING OF THE DAILY YIELD ------
  allDays <- data.frame(date=seq(hSd,hEd,by="day")) #Get a new frame with all expected days (start-end)
  yieldSum$DT <- as.Date(yieldSum$dt) 
  allDays$DT <- as.Date(allDays$date)
  allYield <- merge(allDays,yieldSum,"DT") #Merge with the daily yield 
  allBins <- cut(allYield$yield,breaks=c(0,90,110),labels=c("<90","90+"),include.upper=TRUE) #Bin 
  runLength <- rle(as.character(allBins)) #Do Rle
  print(paste(runLength$lengths,collapse=","))
  print(paste(runLength$values,collapse=","))

  ninetyDays <- length(which(allBins == "90+")) #Count yield + 90
  houseData[rowNo,]$RLE <- ninetyDays
  print(paste("Days about 90+ Yield",ninetyDays))

  #We may need to Insert the Daily Yield (Per Node) in the Database Too.
  yieldSumNode <- ddply(houseSummary,
                        .(dt,nodeId,locationId),
                        summarise,
                        yield=mean(dayYield)
                        )


   yieldId = summaryData[which(summaryData$name == "Yield"),]$id
   yieldNodeInsert <- data.frame(time=yieldSumNode$dt,
                                 nodeId=yieldSumNode$nodeId,
                                 #sensorTypeId=NA,
                                 summaryTypeId=yieldId,
                                 locationId=yieldSumNode$locationId,
                                 value=yieldSumNode$yield
                                 )

   dbWriteTable(con,"Summary",yieldNodeInsert,append=TRUE,row.name=FALSE)
                                 
#strLength <- paste(runLength, collapse=",")
#print(runLength)
#houseData[rowNo,]$RLE <- strLength
 
#  allDays$value <- 25

 
  ## allDays$dt <- as.POSIXlt(allDays$date,tz="GMT")
  ## merge(allDays,yieldSum,by="dt")
 ## plt <- ggplot(yieldSum,aes(dt,yield))
 ## plt <- plt+geom_point(color="red")
 ## plt <- plt+geom_line(color="red")
 ## plt <- plt+geom_errorbar(aes(ymin=yield-stYield,ymax=yield+stYield))
 ## plt <- plt+opts(title="Average Daily Yield + SD")
 ## plt <- plt + geom_vline(data=theHouse,aes(xintercept=hSd,alpha=0.5))
 ## plt <- plt + geom_vline(data=theHouse,aes(xintercept=hEd))
 ## #plt <- plt+geom_linerange(data=allDays,aes(x=date,ymin=0,ymax=90),color="green")
 ## plt
 ## #ggsave("Avg_Day_Yield.png")

 ##  plt <- ggplot(houseSummary)
 ##  plt <- plt+geom_point(aes(x=dt,y=dayYield))
 ##  plt <- plt+geom_linerange(data=allDays,aes(x=date,ymin=0,ymax=90),color="red")
 ##  plt <- plt + opts(title=paste("Daily Yield for",theHouse$address))
 ##  plt <- plt + geom_vline(data=theHouse,aes(xintercept=hSd,alpha=0.5))
 ##  plt <- plt + geom_vline(data=theHouse,aes(xintercept=hEd))
 ##  plt + geom_hline(y=90)
  #ggsave("Dailyyield_All.png")

  #Now do some of the Magic Summarisation Function(TM) <thanks to Hadley>
  # Caluclate Yield for each node
  houseSum <- ddply(houseSummary,
#                    .(nodeId,type),
                    .(nodeId,type),
                    summarise,
                    days=length(dt),
                    count=sum(count),
                    avgDY = mean(dayYield),
                    firstSample = min(dt),
                    lastSample = max(dt)
                    )
  #houseSum$startDate <- min(houseSummary$dt)
  #houseSum$endDate <- max(houseSummary$dt)
  #houseSum$startDate <- theHouse$sd
  #houseSum$endDate <- theHouse$ed
  rs = nrow(houseSum)
  print(paste("Number of Rows ",nrow(houseSum)))
  if (rs == 0){
    print("No Data here")
    return(houseData)
  }

                                        #Create Calculate the Yield per sensor

  if (is.na(theHouse$ed)) duration <- hEd - hSd else duration <- theHouse$ed - theHouse$sd - 1 #Offset as Last day is included
  

  expected <- as.real(duration)  * 288
  houseSum$duration <- duration
  houseSum$expected <- expected
  houseSum$yield <- (houseSum$count / houseSum$expected) * 100.0

 #And where we actually have samples
  dataDuration <- max(houseSum$lastSample) - min(houseSum$firstSample) 
  dataExpected <- as.real(dataDuration) * 288
  houseSum$dataYield <- (houseSum$count / dataExpected) * 100
 
  summary(houseSum)

totExpected <- sum(houseSum$expected)
totSamples <- sum(houseSum$count)
totYield <- (totSamples / totExpected) * 100.0

#Node Counts
#CO2 Nodes
allNodes <- length(unique(houseSum$nodeId))
coNodes <- length(subset(houseSum,type==8)$nodeId)

houseData[rowNo,]$totalNodes <- allNodes
houseData[rowNo,]$coNodes <- coNodes
houseData[rowNo,]$yield <- totYield
houseData[rowNo,]$yieldMin <- min(houseSum$yield)
houseData[rowNo,]$yieldMax <- max(houseSum$yield)
houseData[rowNo,]$yieldSD <- sd(houseSum$yield)
 houseData[rowNo,]$yieldDays <- mean(houseSum$dataYield)

print (paste("Total Yield Is ",totYield))

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

