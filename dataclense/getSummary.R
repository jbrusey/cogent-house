library(RMySQL)
library(ggplot2)

#Setup Database Connection
drv <- dbDriver("MySQL")
con <- dbConnect(drv,dbname="mainStore",user="chuser")

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
