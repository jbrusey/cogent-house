#
# Check Data Script,  Modified for the old sampson close table
#


library(RMySQL)
library(ggplot2)

#Setup Database Connection
drv <- dbDriver("MySQL")
#Connection to the source DB
#sourceDb <- dbConnect(drv,dbname="mainStore",user="root",pass="Ex3lS4ga")
sourceDb <- dbConnect(drv,dbname="faraday",user="root",pass="Ex3lS4ga")
#Connection to the Destination DB
#destDb <- dbConnect(drv,dbname="SampsonClose",user="root",pass="Ex3lS4ga")
destDb <- dbConnect(drv,dbname="SampsonClose",user="root",password="adm3csva",host="127.0.0.1",port=3307)



sourceHouses <-  dbGetQuery(sourceDb,statement="SELECT * FROM House WHERE address != 'ERROR-DATA'")
destHouses <- dbGetQuery(destDb,statement="SELECT * FROM House WHERE address != 'ERROR-DATA'")
#summaryData <- dbReadTable(con,"SummaryType")
#calibrationData <- dbReadTable(con,"Sensor")
#sensorType <- dbReadTable(con,"SensorType")


thisHouse = sourceHouses[18,]
hseName = thisHouse$address

houseQry <- paste("SELECT * FROM House WHERE address = '",hseName,"'",sep="")


#Get Data from the Source DB
sourceHouse <- dbGetQuery(sourceDb,statement=houseQry)

#Work out locations attached to this house
#sourceLocQry <- paste("SELECT * FROM Location as Loc ",
#                  "LEFT OUTER JOIN Room as Room ",
#                  "ON Loc.roomId = Room.id ",
#                  "WHERE houseId =",sourceHouse$id,
#                  " AND Room.name NOT LIKE 'PhyNet%' ",
#                  " AND Room.name NOT IN ('Hot Water','Cold Water','Flow','Return','Hot','Cold','HotWater','ColdWater') ",
#                  sep="")
sourceLocQry <- paste("SELECT * FROM Node WHERE houseId = ",
                      sourceHouse$id)

sourceNodes <- dbGetQuery(sourceDb,statement=sourceLocQry)
sourceNodeIds <- paste(sourceNodes$id,collapse=",")

sourceDataQry <- paste("SELECT nodeId,type,DATE(time) as date,count(*) as count, min(time) as minTime,max(time) as maxTime, min(value) as minVal, max(value) as maxVal, avg(value) as meanVal",
                   " FROM Reading WHERE nodeId IN (",
                   sourceNodeIds,") ",
                   " AND type = 0 ",
                   " GROUP BY nodeId,type,DATE(time)",
                   sep="")

sourceData <- dbGetQuery(sourceDb,sourceDataQry)
sourceData$ts <- as.POSIXlt(sourceData$date,tz="gmt")
sourceData$dset <-  "SOURCE"
#Try to merge the Locations Table
#sourceData <- merge(sourceData,sourceLocations,by.x=c("locationId"),by.y=c("id"),all.x=TRUE)

#----------------------------------------------------

#Get Data from the Dest DB
destHouse <- dbGetQuery(destDb,statement=houseQry)

#Work out locations attached to this house
destLocQry <- paste("SELECT * FROM Location as Loc ",
                  "LEFT OUTER JOIN Room as Room ",
                  "ON Loc.roomId = Room.id ",
                  "WHERE houseId =",destHouse$id,
                  " AND Room.name NOT LIKE 'PhyNet%' ",
                  " AND Room.name NOT IN ('Hot Water','Cold Water','Flow','Return','Hot','Cold','HotWater','ColdWater') ",
                  sep="")

destLocations <- dbGetQuery(destDb,statement=destLocQry)
destLocationIds <- paste(destLocations$id,collapse=",")

destDataQry <- paste("SELECT nodeId,type,locationId,DATE(time) as date,count(*) as count, min(time) as minTime,max(time) as maxTime, min(value) as minVal, max(value) as maxVal, avg(value) as meanVal",
                   " FROM Reading WHERE locationId IN (",
                   destLocationIds,") ",
                   " AND type = 0 ",
                   " GROUP BY nodeId,type,DATE(time)",
                   sep="")

destData <- dbGetQuery(destDb,destDataQry)
destData$ts <- as.POSIXlt(destData$date,tz="gmt")
destData$dset <- "DEST"
#Try to merge the Locations Table
#destData <- merge(destData,destLocations,by.x=c("locationId"),by.y=c("id"),all.x=TRUE)


## #Plot Source Data
## plt <- ggplot(sourceData,aes(ts,meanVal))
## plt <- plt+geom_point()
## plt + facet_grid(nodeId~.)


## plt <- ggplot(destData,aes(ts,meanVal,color=factor(locationId)))
## plt <- plt+geom_point()
## plt + facet_grid(nodeId~.)

#And Both Together
plt <- ggplot(sourceData,aes(ts,meanVal,color=dset))
plt <- plt+geom_line()
plt <- plt+geom_point(data=destData)
plt + facet_grid(nodeId~.)


plt <- ggplot(sourceData,aes(ts,meanVal,color=dset))
plt <- plt+geom_point(shape=0)
plt <- plt+geom_point(data=destData,shape=4)
plt + facet_grid(nodeId~.)

#Both together with Location names rtather than Ids
#And Both Together
plt <- ggplot(sourceData,aes(ts,meanVal,color=factor(name)))
plt <- plt+geom_point()
plt <- plt+geom_line(data=destData)
plt + facet_grid(nodeId~.)

#Or Alternately
plt <- ggplot(sourceData,aes(ts,meanVal,color=factor(locationId)))
plt <- plt+geom_point()
plt <- plt+geom_line(data=destData)
plt + facet_grid(name~.)
