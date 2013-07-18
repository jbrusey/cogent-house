#knit("depBatch.Rrst")

## @knitr loaddeps

require(lubridate)
require(reshape)
require(plyr)
require(RMySQL)
require(ggplot2)
require(RColorBrewer)
require(scales) 
require(xtable)
require(knitr)
require(ascii)

THEDB <- "transferTest"
drv <- dbDriver("MySQL")
#con <- dbConnect(drv,dbname="mainStore",user="chuser")
con <- dbConnect(drv,dbname=THEDB,user="chuser")
houses <- dbReadTable(con,"House")
#Remove the Error Data
houses <- subset(houses,address != "ERROR-DATA")
#thisHouse <- houses[hid,]

##Get Calibration and other such stuff
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
                         name=="Power" |
                         name=="Power pulses" |
                         name=="Battery Voltage"
                         )


## @knitr fetchData

## =========================
## Load the House
## =========================
thisHouse <- houses[hId,]

thisHouse$sd <- tryCatch({as.POSIXlt(thisHouse$startDate,tz="GMT")},
                        error=function(e){
                          NA
                        }
                        )

thisHouse$ed <- tryCatch({as.POSIXlt(thisHouse$endDate,tz="GMT")},
                        error=function(e){                         
                          NA
                        }
                        )

# ====================
#Fetch Locations Associated with this house
# ====================

locQry <- paste(" SELECT * FROM Location as L ",
                " LEFT OUTER JOIN Room as R ",
                " ON L.roomId = R.id ",
                " WHERE houseId = ",
                thisHouse$id,
                sep="")

locations <- dbGetQuery(con,statement=locQry)

#And Remove any locations where the location is not specifed
locations <- locations[!is.na(locations$name),]

locIds <-  paste(locations$id,collapse=",")

# ============================================
# Data
# =============================================

dataQry <- paste("SELECT * from Reading ",
                 " WHERE locationId IN (",
                 locIds,
                 ")",
                 " AND type IN (",
                 paste(sensorTypeList$id,collapse=","),
                 ")",
                 " ORDER BY time",
                 sep="")

# Uncomment this to actaully fetch data
#theData <- dbGetQuery(con,statement=dataQry)
theData$ts <- as.POSIXct(theData$time,tz="GMT")
theData$Date <- as.Date(theData$ts)

# ===============================================
# Calibrate and Remove Error Data
# ===============================================

#Merge to get the sensors types
tmp <- merge(theData,sensorType,by.x=c("type"),by.y=c("id"),all.x=TRUE)

#And Locations
locList <- subset(locations,select=c(id,name))
names(locList) <- c("id","location")

tmp <- merge(tmp,locList,by.x=c("locationId"),by.y=c("id"),all.x=TRUE)

#and calibrate
calib <- merge(tmp,calibrationData,by.x=c("nodeId","type"),by.y=c("nodeId","sensorTypeId"),all.x=TRUE)


noCalibIdx <- which(is.na(calib$id)==TRUE)
if(length(noCalibIdx) > 0){
  calib[noCalibIdx,]$calibrationSlope <- 1
  calib[noCalibIdx,]$calibrationOffset <- 0
}

calib$calibValue <- (calib$value * calib$calibrationSlope) + calib$calibrationOffset

badRows <- which(calib$type==0 & (calib$calibValue < -10 | calib$calibValue>50 ))
if (length(badRows) > 0){
  calib[badRows,]$calibValue <- TRUE
}
#Humidity
badRows <- which(calib$type==2 & (calib$calibValue < 0 | calib$calibValue>100 ))
if (length(badRows) > 0){
  calib[badRows,]$calibValue <- TRUE
}
#Co2
badRows <- which(calib$type==8 & (calib$calibValue < 0 | calib$calibValue>6000 ))
if (length(badRows) > 0){
  calib[badRows,]$calibValue <- TRUE
}

#And Try to remove Temperature and Humidity where the battery level is < 2.5
#TODO
#badRows <- which(calib$type==6 & calib$value < 2.3)


# ===========================================
# Build the initial Summary
# ===========================================

## @knitr houseSummary

dataStart <- min(theData$ts)
dataEnd <- max(theData$ts)
deployRange <- interval(thisHouse$st,thisHouse$ed)
dateRange <- interval(dataStart,dataEnd)
expectedSamples <- dateRange %/% minutes(5)

nodeSum <- ddply(calib,
                 .(nodeId,location,locationId),
                 summarise,
                 count = length(unique(type)))

numNodes <- nrow(nodeSum)
numLocs <- length(unique(nodeSum$location))

#And format colums  for printing
names(nodeSum) <- c("Node Id","Location","Location Id","Sensors")


