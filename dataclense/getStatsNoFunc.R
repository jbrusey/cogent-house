library(RMySQL)
library(ggplot2)
library(reshape)
library(data.table)
library(plyr)

#Setup Database Connection
drv <- dbDriver("MySQL")
#con <- dbConnect(drv,dbname="mainStore",user="chuser")
#con <- dbConnect(drv,dbname="ch",user="chuser")
con <- dbConnect(drv,dbname="transferTest",user="chuser")


#args <- commandArgs(TRUE)
#THEHOUSE <- args[1]

#THEHOUSE <- "1 Avon Road"
#THEHOUSE <- "5 Elm Road"

#15 Is Brays (KLeave for the moment)

i <- 7

allHouses <-  dbGetQuery(con,statement="SELECT * FROM House")
THEHOUSE <- allHouses[i,]
THEHOUSE
hseName <- THEHOUSE$address

#hseName <- "5 Elm Road"


 print("-------------------------------------------------------")
  print(paste("Processing House ",hseName))

                                        #Get House
  houseQry <- paste("SELECT * FROM House WHERE address = '",hseName,"'",sep="")
  theHouse <- dbGetQuery(con,statement=houseQry)
  theHouse$sd <- as.POSIXlt(theHouse$startDate,tz="GMT")
  theHouse$ed <- as.POSIXlt(theHouse$endDate,tz="GMT")

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



dataQry <- paste("SELECT nodeId,type,locationId,DATE(time) as date,count(*) as count, min(time) as minTime,max(time) as maxTime ",
                   "FROM Reading WHERE locationId IN (",
                   locationIds,") ",
                   "AND NOT type in (4,5, 6) ",
                   "GROUP BY nodeId,type,DATE(time)",
                   sep="")


houseSummary <- dbGetQuery(con,statement=dataQry)

                                        #Add a time object so that makes sense toi R
  houseSummary$dt <- as.POSIXlt(houseSummary$date,tz="GMT")

#Plotting (As a Sanity Check)
plt <- ggplot(houseSummary)
plt <- plt + geom_point(aes(dt,count))
#plt + facet_grid(locationId~.)
plt + facet_grid(nodeId~.)
#And another
sanity <- subset(houseSummary,count > 300)
plt <- ggplot(sanity)
plt <- plt + geom_point(aes(dt,count,color=factor(type)))
#plt + facet_grid(locationId~.)
plt + facet_grid(locationId~.)

#Dont Calculate Yield for the First or last Days
  houseSummary$ignoreYield <- TRUE
  idxes <- which(houseSummary$dt > theHouse$sd & houseSummary$dt <= theHouse$ed)
  houseSummary$ignoreYield[idxes] <- FALSE
  houseSummary <- subset(houseSummary,ignoreYield == FALSE)



                                        #Calulate Yield Percentages per Day (Which at the moment we need to eyeball to get Elenas RLE)
  houseSummary$dayYield <- (houseSummary$count / 288) * 100
                                        #Not Used at the Moment
                                        #houseSummary$dayYield90[which(houseSummary$dayYield >= 90)] <- TRUE

                                        #Summarise this so we just get a daily yield
  yieldSum <- ddply(houseSummary,
                    .(dt),
                    summarise,
                    nodes=length(dt),
                    yield=mean(dayYield)
                    )

                                        #Aggregate Days
  #allDays <- data.frame(date=seq(as.POSIXlt(min(houseSummary$dt),tx="GMT"),as.POSIXlt(max(houseSummary$dt),tx="GMT"),by="day"))
allDays <- data.frame(date=seq(as.POSIXlt(theHouse$startDate,tz="GMT"),as.POSIXlt(theHouse$endDate,tz="GMT"),by="day"))
  allDays$value <- 25
  ## allDays$dt <- as.POSIXlt(allDays$date,tz="GMT")
  ## merge(allDays,yieldSum,by="dt")


  plt <- ggplot(houseSummary)
  plt <- plt+geom_point(aes(x=dt,y=dayYield))
  plt <- plt+geom_linerange(data=allDays,aes(x=date,ymin=0,ymax=90),color="red")
  plt <- plt + opts(title=paste("Daily Yield for",theHouse$address))
  plt + geom_hline(y=90)

                                        #Now do some of the Magic Summarisation Function(TM) <thanks to Hadley>
  houseSum <- ddply(houseSummary,
                    .(nodeId,type),
                    summarise,
                    days=length(dt),
                    count=sum(count),
                    avgDY = mean(dayYield)#,
                                        #startDate = min(dt),
                                        #endDate = max(dt)
                    )
  #houseSum$startDate <- min(houseSummary$dt)
  #houseSum$endDate <- max(houseSummary$dt)
  houseSum$startDate <- theHouse$sd
  houseSum$endDate <- theHouse$ed


                                        #Create Calculate the Yield per sensor
  houseSum$duration <- houseSum$endDate - houseSum$startDate
  houseSum$expected <- as.real(houseSum$duration) * 288 
  houseSum$yield <- (houseSum$count / houseSum$expected) * 100.0
  summary(houseSum)

totExpected <- sum(houseSum$expected)
totSamples <- sum(houseSum$count)
totYield <- (totSamples / totExpected) * 100.0

print (paste("Total Yield Is ",totYield))


#Battery Check
## theQry <- "SELECT * FROM Reading WHERE nodeId=197 AND type=6 AND time>'2011-12-01' AND time < '2012-04-01'" 
## batData <- dbGetQuery(con,statement=theQry)
## batData$dt <- as.POSIXlt(batData$time)

## plt <- ggplot(batData)
## plt <- plt + geom_point(aes(dt,value))
## plt

##Temporoary Query
#theQry = paste("SELECT * FROM Reading WHERE locationId IN (",locationIds,") AND type = 0",sep="")
theQry = "SELECT * FROM Reading WHERE nodeId = 249028604 AND locationId IS NOT NULL"
tmpData <- dbGetQuery(con,theQry)
tmpData$ts <- as.POSIXlt(tmpData$time)

plt <- ggplot(tmpData)
plt <- plt+geom_point(aes(ts,value,color=factor(type)))
plt + facet_grid(locationId~nodeId)

summary(tmpData)
