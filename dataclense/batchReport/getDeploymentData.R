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
require(pander)

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
                         name=="Power pulses"                        
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
theData <- dbGetQuery(con,statement=dataQry)
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


## ===================================
## Yield Calculations
## ===================================

## @knitr yieldCalcs


#Strip out flow and return shizzle from the yield table
yieldData <- subset(calib,location!="Flow" & location!="Return" & location!="HotWater" & location!="ColdWater" & location!="Hot Water" & location!= "Cold Water" & location!="Cold" & location!="Hot")

#nodeSum <- ddply(calib,
nodeSum <- ddply(yieldData,
                 .(nodeId,location,type),
                 summarise,
                 count = length(ts),
                 numsensors = length(unique(type)))

#Yield
nodeSum$yield = (nodeSum$count / expectedSamples) * 100.0
avgYield = mean(nodeSum$yield)

#Table of outputs
yieldTable <- ddply(nodeSum,
                    .(nodeId,location),
                    summarise,
                    Yield = mean(yield))

#Heatmap
yieldHeatmap <- ddply(yieldData,
                    .(nodeId,location,Date),
                    summarise,
                    count = length(ts),
                    numsensors = length(unique(type)))

yieldHeatmap$yield <- yieldHeatmap$count / (288 * yieldHeatmap$numsensors) * 100

#Days with > 90% yield
yieldDays <- ddply(yieldHeatmap,
                   .(Date),
                   summarise,
                   count = sum(count),
                   numsensors = sum(numsensors),
                   avgYield = mean(yield))

yieldDays$yield <- yieldDays$count / (288* yieldDays$numsensors) * 100
totDays <- nrow(yieldDays)
yldDays <- nrow(subset(yieldDays,yield>=90))

