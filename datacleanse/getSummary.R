library(RMySQL)
library(ggplot2)

#Setup Database Connection
THEDB <- "transferTest"


drv <- dbDriver("MySQL")
#con <- dbConnect(drv,dbname="mainStore",user="chuser")
con <- dbConnect(drv,dbname=THEDB,user="chuser")

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

  #Query to Fetch the Summary Data
  summaryQry <- paste("SELECT * FROM Summary ",
                      "WHERE LocationId IN (",locationIds,")",
                      "AND summaryTypeId = 1")

  summaryData <- dbGetQuery(con,statement=summaryQry)
  summaryData$dt <- as.POSIXlt(summaryData$time,tz="GMT")

  plt <- ggplot(summaryData,aes(dt,value,color=factor(sensorTypeId)))
  plt <- plt+geom_point()
  plt <- plt+geom_step()
plt + facet_grid(nodeId~.)
                        
