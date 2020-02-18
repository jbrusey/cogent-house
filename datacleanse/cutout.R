library(RMySQL)
library(ggplot2)
library(reshape)
library(data.table)
library(plyr)

#Setup Database Connection
drv <- dbDriver("MySQL")
con <- dbConnect(drv,dbname="mainStore",user="chuser")

THEHOUSE <- "5 Elm Road"

#Get House
houseQry <- paste("SELECT * FROM House WHERE address = '",THEHOUSE,"'",sep="")
theHouse <- dbGetQuery(con,statement=houseQry)
theHouse$sd <- as.POSIXlt(theHouse$startDate,tz="GMT")
theHouse$ed <- as.POSIXlt(theHouse$endDate,tz="GMT")

#Locations
locQry <- paste("SELECT * FROM Location WHERE houseId =",theHouse$id,sep="")
locations <- dbGetQuery(con,statement=locQry)
locationIds <- paste(locations$id,collapse=",")



## #--- FULL DATA -----
dataQry <- paste("SELECT * FROM Reading WHERE locationId IN (",locationIds,")",sep="")

houseData <- dbGetQuery(con,statement=dataQry)
## #Add timestamps
houseData$dt <- as.POSIXlt(houseData$time,tz="GMT")

#Summaryise House data to get min / Max timestamps per location etc.
summary(houseData$dt)

houseSum <- ddply(houseData,
                  .(nodeId,locationId,type),
                  summarise,
                  count=length(dt),
                  start=min(dt),
                  end=max(dt)
                  )
#Duration in Days
houseSum$duration <- houseSum$end - houseSum$start
houseSum$expected <- as.real(houseSum$duration) * 288 
houseSum$yield <- (houseSum$count / houseSum$expected) * 100.0

#-------------- PLOT HOUSE DATA (FOR INTEREST)

#Plot (for Interest)
plt <- ggplot(houseData,aes(dt,value))
plt <- plt + geom_point(aes(color=type))
#plt <- plt + geom_segment(data=theHouse,aes(x=sd,xend=ed,y=40,yend=40),size=3)
plt + facet_grid(locationId~.)


## Work out what nodes we are expecting
nodeIds <- ddply(houseData, .(nodeId),summarize, Count = length(nodeId),locId=mean(locationId))


#Search for Nodes 

## # ------------ MISSING VALUES SANITY CHECK -----------------------------------
nodeStr <- paste(nodeIds$nodeId,collapse=",")

missingQry <- paste("SELECT * FROM Reading WHERE nodeId IN (",
                    nodeStr,
                    ") AND locationId is null AND time >='",
                    theHouse$sd,
                    "' AND time <= '",
                    theHouse$ed+(60*80*24),"'",
                    sep="")


missingData <- dbGetQuery(con,statement=missingQry)
missingData$dt <- as.POSIXlt(missingData$time,tz="GMT")


#Plot (for Interest)
plt <- ggplot(missingData,aes(dt,value))
plt <- plt + geom_point(aes(color=type))
plt <- plt + geom_point(data=houseData,aes(dt,value))
plt + facet_grid(nodeId~locationId)
#plt <- plt + geom_point(data=missingData,aes(color=type))
#plt <- plt + geom_segment(data=theHouse,aes(x=sd,xend=ed,y=40,yend=40),size=3)
#plt + facet_grid(locationId~.)
#plt <- ggplot(missingData,aes(dt,value))
#plt <- plt + geom_point(aes(color=factor(nodeId)))
#plt <- plt + geom_segment(data=theHouse,aes(x=sd,xend=ed,y=40,yend=40),size=3)
#plt + facet_grid(locationId~.)

## missingSum <- ddply(missingData, .(nodeId,locationId), summarise, Count=length(dt),start=min(dt),end=max(dt))
## #Can we check if there is any missing data between these points


## #geom_segment(aes(x=sd,xend=ed,y=address,yend=address),size=3)

