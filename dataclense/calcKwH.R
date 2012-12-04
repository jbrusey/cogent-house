library(RMySQL)
library(ggplot2)
#library(reshape)
#library(data.table)
library(plyr)


#Setup Database Connection
drv <- dbDriver("MySQL")
#con <- dbConnect(drv,dbname="mainStore",user="chuser")
#con <- dbConnect(drv,dbname="SampsonClose",user="root",password="adm3csva",host="127.0.0.1",port=3307)
#con <- dbConnect(drv,dbname="ch",user="chuser")
#con <- dbConnect(drv,dbname="transferTest",user="chuser")
con <- dbConnect(drv,dbname="transferStore",user="root",password="Ex3lS4ga")


#args <- commandArgs(TRUE)
#THEHOUSE <- args[1]

#THEHOUSE <- "1 Avon Road"
#THEHOUSE <- "5 Elm Road"

allHouses <-  dbGetQuery(con,statement="SELECT * FROM House WHERE address != 'ERROR-DATA'")
summaryData <- dbReadTable(con,"SummaryType")
sensorType <- dbReadTable(con,"SensorType")
i=1

THEHOUSE <- allHouses[i,]
hseName <- THEHOUSE$address

rowNo <- which(houseData$address == hseName)

houseQry <- paste("SELECT * FROM House WHERE address = '",hseName,"'",sep="")
theHouse <- dbGetQuery(con,statement=houseQry)
  
theHouse$sd <- as.POSIXlt(theHouse$startDate,tz="GMT")
theHouse$ed <- as.POSIXlt(theHouse$endDate,tz="GMT")

locQry <- paste("SELECT * FROM Location as Loc ",
                "LEFT OUTER JOIN Room as Room ",
                "ON Loc.roomId = Room.id ",
                "WHERE houseId =",theHouse$id,
                " AND Room.name NOT LIKE 'PhyNet%' ",
                " AND Room.name NOT IN ('Hot Water','Cold Water','Flow','Return','Hot','Cold','HotWater','ColdWater') ",
                sep="")
locations <- dbGetQuery(con,statement=locQry)
locationIds <- paste(locations$id,collapse=",")

#We need to get the Electricty Sensor
elecSensorId <- sensorType[which(sensorType$name == "Power"),]$id

#Fetch the Electricty Data
theQry <- paste("SELECT * FROM Reading ",
                "WHERE locationId IN (",
                locationIds,")",
                "AND type = ",
                elecSensorId,
                sep="")
#Fetch the data
theData <- dbGetQuery(con,statement=theQry)


#Work out difference between timestamps
theData$ts <- as.POSIXlt(theData$time,tz="GMT")
#Time Delta
theData$tDelta <- c(NA,diff(theData$ts))

#theData[2,]$tDelta <- 61
#theData[714,]$tDelta <- 61

#Remove any day where there is more than an hour between readings
badSamples <- theData[which(theData$tDelta >= 60),]
badDays <- unique(badSamples$dt)


#Plot the Data
plt <- ggplot(theData)
plt <- plt + geom_step(aes(ts,value))
#plt

#Now convert that to KWH
theData$kWh <- ((theData$tDelta / (60))* theData$value) / 1000
theData$dt <- as.Date(theData$ts)

#Daily Summary
dailySummary <- ddply(theData,
                      .(dt,nodeId,locationId),
                      summarise,
                      min = min(value),
                      max = max(value),
                      avg = mean(value),
                      kWh = sum(kWh)                   
                      )

for (item in badDays){
  #print(item)
  #print(as.Date(item))
  print(which(dailySummary$dt == item))
  dailySummary[which(dailySummary$dt == item),]$kWh = NA
}
                      

plt <- ggplot(dailySummary)
plt <- plt + geom_step(aes(dt,kWh))
#plt

dayCountId = summaryData[which(summaryData$name == "Daily KwH"),]$id

#Try to store the counts in the Database
countInsert <- data.frame(time=dailySummary$dt,
                          nodeId=dailySummary$nodeId,
                          sensorTypeId=elecSensorId,
                          summaryTypeId=dayCountId,
                          locationId=dailySummary$locationId,
                          value=dailySummary$kWh
                          )

dbWriteTable(con,"Summary",countInsert,append=TRUE,row.name=FALSE)`

