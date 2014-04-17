
## @knitr init
require(ggplot2)
require(lubridate)
require(reshape)
require(plyr)
require(ggplot2)
require(RColorBrewer)
require(scales) 
require(xtable)
require(knitr)
require(pander)

df <- read.csv("rawdata.csv")
df$ts <- as.POSIXlt(df$time,tz="GMT")
df$date <- as.Date(df$ts)
df$descstr <- paste(df$locationStr,
                    " (Node ",
                    df$nodeId,
                    ")",
                    sep="")
## @knitr summary

dataStart <- min(df$ts)
dataEnd <- max(df$ts)
dateRange <- interval(dataStart,dataEnd)
expectedSamples <- dateRange %/% minutes(5)

#Summary by node
nodeSum <- ddply(df,
                 .(nodeId,locationId,locationStr),
                 summarise,
                 count = length(unique(typeId)))

names(nodeSum) <- c("Node Id","Location Id","Location","Sensors")


## ===========================
## DEAL WITH YIELD
## ===========================

## @knitr yieldCalcs

nodeSum <- ddply(df,
                 .(nodeId,typeId,locationStr),
                 summarise,
                 count = length(nodeId)
                 )

nodeSum$yield = (nodeSum$count / expectedSamples) * 100.0
#nodeSum$yield = (nodeSum$count / 288.0) * 100.0
avgYield = mean(nodeSum$yield)

#Format for Outputting
yieldTable <- ddply(nodeSum,
                    .(nodeId,locationStr),
                    summarise,
                    Yield=mean(yield))

#yieldTable$nodeStr <- paste("Node: ",yieldTable$nodeId,yieldTable$locationStr)

#Yield Heatmaps
yieldHeatmap <-  ddply(df,
                       .(nodeId,locationStr,typeId,date),
                       summarise,
                       count = length(nodeId)
                       )
                       
yieldHeatmap$yield <- (yieldHeatmap$count / 288) * 100
yieldHeatmap$descstr <- paste(yieldHeatmap$locationStr,
                              " (Node ",
                              yieldHeatmap$nodeId,
                              ")",
                              sep="")
#Condense so it is per node
yieldNodes <- ddply(yieldHeatmap,
                    .(descstr,date),
                    summarise,
                    yield = mean(yield))


############################
## TEMPERATURE DATA
############################

## @knitr tempData

ss <- subset(df,typeId == 0)

summary <- ddply(ss,
                 .(nodeId,locationStr),
                 summarise,
                 average=mean(value),
                 minimum=min(value),
                 maximum=max(value)
                 )


#And Calculate Comfort
ss$comfort <- cut(ss$value,breaks=c(0,16,18,22,27,100),
           labels=c("Health Risk <16","Cold 16-18","Comfortable 18-22","Warm 22-27","Overheating 27+"))

## #Give PlyR a go.
## #Count Values
expose <- count(ss,vars=c('descstr','comfort'))
#Calc Percentages
expose <- ddply(expose,.(descstr),transform,p=freq/sum(freq))
expose<- ddply(expose,.(descstr),transform,tpos = cumsum(p) - 0.5*p)

exposeLab <- subset(expose,comfort=="Comfortable 18-22")
exposeLab$label <- paste(round(exposeLab$p * 100 ,digits=2),"%",sep="")

#Flatten to be in a table
melted <- subset(melt(expose,id=c("descstr","comfort")),variable=="p")
melted$value <- melted$value * 100.0
exposeFlat <- cast(melted,descstr~comfort)

############################
## EXPOSURE DATA
############################

## @knitr exposeData

ss <- subset(df,typeId == 2)

summary <- ddply(ss,
                 .(nodeId,locationStr),
                 summarise,
                 average=mean(value),
                 minimum=min(value),
                 maximum=max(value)
                 )


#And Calculate Comfort

ss$comfort <- cut(ss$value,breaks=c(0,45,65,85,100),
                  labels=c("Dry","Comfortable","Damp","Risk"))
## #Give PlyR a go.
## #Count Values
expose <- count(ss,vars=c('descstr','comfort'))
#Calc Percentages
expose <- ddply(expose,.(descstr),transform,p=freq/sum(freq))
expose<- ddply(expose,.(descstr),transform,tpos = cumsum(p) - 0.5*p)

exposeLab <- subset(expose,comfort=="Comfortable")
exposeLab$label <- paste(round(exposeLab$p * 100 ,digits=2),"%",sep="")

#Flatten to be in a table
melted <- subset(melt(expose,id=c("descstr","comfort")),variable=="p")
melted$value <- melted$value * 100.0
exposeFlat <- cast(melted,descstr~comfort)


#=========================
# Other Data
#=========================

## @knitr otherData

ss <- subset(df,typeId>=8 & typeId <= 10)

if (nrow(ss) > 0){
  summary <-  ddply(subset(ss),
                    .(nodeId,location),
                    summarise,
                    avgvalue = mean(value),
                    minvalue = min(value),
                    maxvalue = max(value)
                    )

  names(summary) <- c("Node Id","Location","Average","Minimum","Maximum")
}
