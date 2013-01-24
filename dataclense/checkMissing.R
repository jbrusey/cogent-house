library(RMySQL)
library(ggplot2)
library(reshape)
library(data.table)

#Setup Database Connection
drv <- dbDriver("MySQL")
con <- dbConnect(drv,dbname="mainStore",user="chuser")


#Query
theQry = "
SELECT *, DATE(time) FROM mainStore.Reading
WHERE locationId is null
GROUP BY DATE(time),nodeId
"

theData <- dbGetQuery(con,statement=theQry)
names(theData) <- c("time","nodeId","type","locationId","value","date")
theData$dt <- as.Date(theData$date)

plt <- ggplot(theData)
plt <- plt + geom_point(aes(dt,type,color=factor(nodeId)))
plt


plt <- ggplot(theData)
plt <- plt + geom_point(aes(dt,factor(nodeId),color=factor(nodeId)))
plt 


theQry = "SELECT * FROM House"
houseData <- dbGetQuery(con,statement=theQry)
houseData$sd <- as.Date(houseData$startDate)
houseData$ed <- as.Date(houseData$endDate)


plt <- ggplot(houseData)
plt <- plt + geom_segment(aes(x=sd,xend=ed,y=address,yend=address),size=3)
plt

#Try Combining the Two
plt <- ggplot(theData)
plt <- plt + geom_point(aes(dt,factor(nodeId),color=factor(nodeId)))
plt <- plt + geom_segment(data=houseData,aes(x=sd,xend=ed,y=address,yend=address),size=3)
plt 
