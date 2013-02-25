#Flatten a dataset into XLS format

library(RMySQL)
library(ggplot2)
library(reshape)
#library(data.table)
#library(plyr)

drv <- dbDriver("MySQL")
con <- dbConnect(drv,dbname="mainStore",user="root",password="Ex3lS4ga")


houses <- dbReadTable(con,"House")

#This House
thisHouse <- houses[8,]

calibrationData <- dbReadTable(con,"Sensor")

sensorType <- dbReadTable(con,"SensorType")
sensorType <- subset(sensorType,select=c(id,name,units))

##Sensors we are interested in (For Yield Calculateions)
sensorTypeList <- subset(sensorType,
                         name=="Temperature" |
                         name=="Humidity" |
                         name=="Light PAR" |
                         name=="Light TSR" |
                         name=="CO2" |
                         name=="Air Quality" |
                         name=="VOC" |
                         name=="Power",
                         )

               
#Fetch Locations Associated with this house
locQry <- paste(" SELECT * FROM Location as L ",
                " LEFT OUTER JOIN Room as R ",
                " ON L.roomId = R.id ",
                " WHERE houseId = ",
                thisHouse$id,
                sep="")

locations <- dbGetQuery(con,statement=locQry)

locIds <-  paste(locations$id,collapse=",")

dataQry <- paste("SELECT * from Reading ",
                 " WHERE locationId IN (",
                 locIds,
                 ")",
                 " AND type IN (",
                 paste(sensorTypeList$id,collapse=","),
                 ")",
                 sep="")

theData <- dbGetQuery(con,statement=dataQry)
theData$ts <- as.POSIXlt(theData$time,tz="GMT")

#Merge to get the sensors types
tmp <- merge(theData,sensorType,by.x=c("type"),by.y=c("id"),all.x=TRUE)

#And Locations
locList <- subset(locations,select=c(id,name))
names(locList) <- c("id","location")

tmp <- merge(tmp,locList,by.x=c("locationId"),by.y=c("id"),all.x=TRUE)

#and calibrate
calib <- merge(tmp,calibrationData,by.x=c("nodeId","type"),by.y=c("nodeId","sensorTypeId"),all.x=TRUE)

noCalibIdx <- which(is.na(calib$id)==TRUE)
calib[noCalibIdx,]$calibrationSlope <- 1
calib[noCalibIdx,]$calibrationOffset <- 0

calib$calibValue <- (calib$value * calib$calibrationSlope) + calib$calibrationOffset

calib <- subset(calib,ts<as.POSIXlt("2012-02-27"))

## #Plot all of this Data
## #plt <- ggplot(theData)
## plt <- plt +geom_line(aes(ts,value,color=factor(nodeId)))
## plt + facet_grid(type~.,scale="free_y")

#plt <- ggplot(tmp)
plt <- ggplot(calib)
plt <- plt +geom_line(aes(ts,calibValue,color=factor(location)))
plt + facet_grid(name~.,scale="free_y")
ggsave("preMelt.png")

#preMelt <- subset(calib,select=c("nodeId","type","locationId","date","calibValue"))

preMelt <- subset(calib,select=c("nodeId","name","location","ts","calibValue"))
#preMelt <-  preMelt[1:50,]
#Flatten this Down
#melted <- melt(preMelt,id=c("nodeId","type","locationId","ts"))
#melted <- melt(exportData,id=c("locationId","nodeId","Date","Address","LocName"),na.rm=TRUE)
#exportReady <- cast(melted)



preMelt$ts <- as.character(preMelt$ts)
melted <- melt(preMelt,id=c("nodeId","location","name","ts"))
#newexport <- cast(melted,ts~nodeId+location+name)
newexport <- cast(melted,ts~nodeId+location+name)
#newexport <- reshape(melted,
write.csv(newexport,"flatExport.csv",row.names=FALSE)
#Brailes EXPORT
#melted <- melt(exportData,id=c("locationId","nodeId","Date","Address","LocName"),na.rm=TRUE)
#exportReady <- cast(melted)

#Daily Averages
calib$date <- as.Date(calib$ts)
#Summarise
dailySummary <-  ddply(calib,
                      .(nodeId,location,name,date),
                      summarise,
                      #minVal = min(value),
                      #maxVal = max(value),
                      avgVal = mean(calibValue)
                      )

#Test
#ds <- dailySummary[1:20,]
melted <- melt(dailySummary,id=c("date","nodeId","location","name"))
export <- cast(melted,date~nodeId+location+name)
write.csv(export,"hourlyAvg.csv",row.names=FALSE)
#melted <- melt(dailySummary,id=c("nodeId","locationId","date"))
#flat <- cast(melted)

plt <- ggplot(melted)
plt <- plt + geom_line(aes(ts,value,color=factor(type)))
plt + facet_grid(nodeId~.)


#TEST FOR RRD
subData <- subset(theData,nodeId==197 & type == 0)
plt <- ggplot(subData)
plt <- plt+geom_line(aes(ts,value))
plt
ggsave("Beryfields197.png")

subData <- subset(subData,select=c(unix,value))
write.csv(subData,"berryfields.csv",row.names=FALSE)


foo <- calib[1:10,]



foo$date <- as.Date(foo$ts)
foo$hour <- format(foo$ts, "%H")
foo$fifteen <- floor(as.numeric(format(foo$ts, "%M")) / 15) * 15
foo$fDate <- paste(foo$date,paste(foo$hour,foo$fifteen,"00",sep=":"))
foo$sumtime <- as.POSIXlt(foo$fDate)


#Lets try that in one
foo$summtime <- as.POSIXlt(paste(as.Date(foo$ts),
                                 paste(format(foo$ts,"%H"),
                                       floor(as.numeric(format(foo$ts,"%M"))/15)*15,
                                       "00",
                                       sep=":")
                                 )
                           )
