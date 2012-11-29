library(RMySQL)
library(ggplot2)
library(reshape)
library(data.table)
library(plyr)

#Setup Database Connection
drv <- dbDriver("MySQL")
con <- dbConnect(drv,dbname="mainStore",user="chuser")


#args <- commandArgs(TRUE)
#THEHOUSE <- args[1]

#THEHOUSE <- "1 Avon Road"
THEHOUSE <- "5 Elm Road"
THEHOUSE <- "10 Southam Gardens"

processHouse <- function(hseName) {
  print("-------------------------------------------------------")
  print(paste("Processing House ",hseName))

                                        #Get House
  houseQry <- paste("SELECT * FROM House WHERE address = '",hseName,"'",sep="")
  theHouse <- dbGetQuery(con,statement=houseQry)
  theHouse$sd <- as.POSIXlt(theHouse$startDate,tz="GMT")
  theHouse$ed <- as.POSIXlt(theHouse$endDate,tz="GMT")

                                        #Locations
  locQry <- paste("SELECT * FROM Location WHERE houseId =",theHouse$id,sep="")
  locations <- dbGetQuery(con,statement=locQry)
  locationIds <- paste(locations$id,collapse=",")
                                        #This Loc
                                        #thisLoc = locations[1,]

  print(paste("Expected Start ",theHouse$startDate,"Expected End",theHouse$endDate))



  ## dataQry <- paste("SELECT *,DATE(time),count(*) FROM Reading WHERE locationId IN (",
  ##                  locationIds,") ",
  ##                  "GROUP BY nodeId,type,DATE(time)",
  ##                  sep="")

  dataQry <- paste("SELECT nodeId,type,locationId,DATE(time) as date,count(*) as count, min(time) as minTime,max(time) as maxTime ",
                   "FROM Reading WHERE locationId IN (",
                   locationIds,") ",
                   "GROUP BY nodeId,type,DATE(time)",
                   sep="")


  houseSummary <- dbGetQuery(con,statement=dataQry)

                                        #Add a time object so that makes sense toi R
  houseSummary$dt <- as.POSIXlt(houseSummary$date,tz="GMT")

                                        #Dont Calculate Yield for the First of last Days
  houseSummary$ignoreYield <- TRUE
  idxes <- which(houseSummary$dt > theHouse$sd & houseSummary$dt < theHouse$ed)
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
  allDays <- data.frame(date=seq(as.POSIXlt(theHouse$startDate,tz="GMT"),as.POSIXlt(theHouse$endDate,tz="GMT"),by="day"))
  #allDays <- data.frame(date=seq(as.POSIXlt(min(houseSummary$dt),tx="GMT"),as.POSIXlt(max(houseSummary$dt),tx="GMT"),by="day"))
  allDays$value <- 25
  ## allDays$dt <- as.POSIXlt(allDays$date,tz="GMT")
  ## merge(allDays,yieldSum,by="dt")


  plt <- ggplot(houseSummary)
  plt <- plt+geom_point(aes(x=dt,y=dayYield))
  plt <- plt+geom_linerange(data=allDays,aes(x=date,ymin=0,ymax=90),color="red")
  plt <- plt + opts(title=paste("Daily Yield for",theHouse$address))
  plt + geom_hline(y=90)


  print(paste("Number of Rows",nrow(houseSummary)))
  if(nrow(houseSummary) >= 1){
  #Now do some of the Magic Summarisation Function(TM) <thanks to Hadley>
  houseSum <- ddply(houseSummary,
                    .(nodeId,type),
                    summarise,
                    days=length(dt),
                    count=sum(count),
                    avgDY = mean(dayYield)
                    )
  
  houseSum$startDate <- min(houseSummary$dt)
  houseSum$endDate <- max(houseSummary$dt)

                                        #Create Calculate the Yield per sensor
  houseSum$duration <- houseSum$endDate - houseSum$startDate
  houseSum$expected <- as.real(houseSum$duration) * 288 
  houseSum$yield <- (houseSum$count / houseSum$expected) * 100.0
  print(summary(houseSum))
}
  else
    {
      print("No Data for this deployment")
    }
}

#try(processHouse(THEHOUSE))


allHouses <-  dbGetQuery(con,statement="SELECT * FROM House")

#for (i in 1:nrow(allHouses)){
for (i in 1:5){
  thisHouse <- allHouses[i,]
  try(processHouse(thisHouse$address))
}
