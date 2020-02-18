library(RMySQL)
library(ggplot2)

drv <- dbDriver("MySQL")
#con <- dbConnect(drv,dbname="SampsonClose",user="root",password="adm3csva",host="127.0.0.1",port=3307)
con <- dbConnect(drv,dbname="mainStore",user="root",password="Ex3lS4ga")

calibrationData <- dbReadTable(con,"Sensor")

allHouses <-  dbGetQuery(con,statement="SELECT * FROM House WHERE address != 'ERROR-DATA'")

i = 7
THEHOUSE <- allHouses[i,]
hseName <- THEHOUSE$address

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

  #houseData[rowNo,]$dbStart <- theHouse$startDate
  #houseData[rowNo,]$dbEnd <- theHouse$endDate


dataQry <- paste("SELECT nodeId,type,locationId,DATE(time) as date,count(*) as count, min(time) as minTime,max(time) as maxTime ",
                   "FROM Reading WHERE locationId IN (",
                   locationIds,") ",
                   "AND NOT type in (4,5, 6,14) ",
                   "GROUP BY nodeId,type,DATE(time)",
                   sep="")


houseSummary <- dbGetQuery(con,statement=dataQry)


allQry <- paste("SELECT * FROM Reading WHERE locationId IN (",
                locationIds,
                ") ",
                "AND NOT type in (14) ",
                sep=""
                )


theData <- dbGetQuery(con,statement=allQry)
#theData$calib <- NA

tmp <- merge(theData,calibrationData,by.x=c("nodeId","type"),by.y=c("nodeId","sensorTypeId"),all)
tmp$calib <- tmp$value*tmp$calibrationSlope + tmp$calibrationOffset
tmp$ts <- as.POSIXlt(tmp$time,tz="GMT")
tmp$dt <- as.Date(tmp$ts)



plt <- ggplot(subset(tmp,type==0))
plt <- plt+geom_point(aes(ts,value,color=factor(nodeId)))
plt <- plt+geom_line(aes(ts,calib,color=factor(nodeId)))
#plt <- plt+goem_point
plt + facet_grid(locationId~.)
