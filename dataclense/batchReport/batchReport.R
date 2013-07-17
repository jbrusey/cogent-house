require(RMySQL)
require(knitr)

#Setup Database Connection
THEDB <- "transferTest"
drv <- dbDriver("MySQL")
#con <- dbConnect(drv,dbname="mainStore",user="chuser")
con <- dbConnect(drv,dbname=THEDB,user="chuser")
houses <- dbReadTable(con,"House")
#Remove the Error Data
houses <- subset(houses,address != "ERROR-DATA")

# ========================
#
#  FETCH CALIBRATION STUFF
#
# ========================

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



#for (i in 1:nrow(houses)){
for (i in 10:16){
  thisHouse <- houses[i,]
  houseStr <- gsub("\\s","",thisHouse$address)
  print(houseStr)
  knit("deploymentReport.Rnw", output = paste(houseStr,".tex",sep=""))
}


thisHouse = houses[7,]
houseStr <- gsub("\\s","",thisHouse$address)
knit("deploymentReport.Rnw", output = paste(houseStr,".tex",sep=""))
