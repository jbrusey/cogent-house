library(dplyr)
library(rjson)
library(readxl)
library(tidyr)
library(xts)
library(readr)
library(ggplot2)
library(scales)

theme_set(theme_gray(base_size=14))
tname <- expression(paste("Temperature (",degree,"C)"))

############## PROCESS NODE DATA FILES ###########################

readNodeFile <- function(fname) {
  #Read in csv file (readr)
  data <- read_csv(fname,col_names = FALSE)
  #Extract node Id from the file name
  nid <- (strsplit(fname, "_")[[1]])[2]
  data$NodeId <- nid


  data <- data %>%
    #Rename the fields to something meaningful
    rename(Time = X1, temperature = X2, humidity = X3,
           adc0 = X4, adc1 = X5, adc2 = X6,
           voltage = X7, parent = X8, rssi = X9, seq = X10) %>%
    #Cast time to correct value, and align to the nearest 5 mins
    mutate(Time = align.time(
      as.POSIXct(Time, n = 300, origin = "1970-01-01"),
      5*60))

  #This section of code finds all the times that could have
  # occured between the start and end of the data stream. Missing
  # times are added to the dataframe, this is done to stop ggplot
  # using linear interpolation
  time.max <- max(data$Time)
  time.min <- min(data$Time)
  all.dates <- seq(time.min, time.max, by = "5 mins")
  all.dates.frame <- data.frame(list(Time = all.dates))
  all.dates.frame$NodeId <- nid
  data <- merge(all.dates.frame, data, all = T)

  #return processed data
  return(data)
}


fname <- commandArgs(TRUE)[1]
nodeData <- readNodeFile(fname)

nid <- unlist(strsplit(fname,"_"))[2]

pname <- paste("pulp_",nid,"_temperature.png", sep = "")
png(file = pname, width = 860, height = 480, units = 'px')
ggplot(nodeData, aes(x = Time, y = temperature)) +
  geom_line() +
  xlab("") +
  ylab(tname) +
  scale_x_datetime(breaks = "7 day", labels = date_format("%m-%d\n%H:%M"))
dev.off()

pname <- paste("pulp_",nid,"_humidity.png", sep = "")
png(file = pname, width = 860, height = 480, units = 'px')
ggplot(nodeData, aes(x = Time, y = humidity)) +
  geom_line() +
  xlab("") +
  ylab("Humidity (%)") +
  scale_x_datetime(breaks = "7 day", labels = date_format("%m-%d\n%H:%M"))
dev.off()

pname <- paste("pulp_",nid,"_adc0.png", sep = "")
png(file = pname, width = 860, height = 480, units = 'px')
ggplot(nodeData, aes(x = Time, y = adc0)) +
  geom_line() +
  xlab("") +
  ylab("ADC0") +
  scale_x_datetime(breaks = "7 day", labels = date_format("%m-%d\n%H:%M"))
dev.off()

pname <- paste("pulp_",nid,"_adc1.png", sep = "")
png(file = pname, width = 860, height = 480, units = 'px')
ggplot(nodeData, aes(x = Time, y = adc1)) +
  geom_line() +
  xlab("") +
  ylab("ADC1") +
  scale_x_datetime(breaks = "7 day", labels = date_format("%m-%d\n%H:%M"))
dev.off()

pname <- paste("pulp_",nid,"_adc2.png", sep = "")
png(file = pname, width = 860, height = 480, units = 'px')
ggplot(nodeData, aes(x = Time, y = adc2)) +
  geom_line() +
  xlab("") +
  ylab("ADC2") +
  scale_x_datetime(breaks = "7 day", labels = date_format("%m-%d\n%H:%M"))
dev.off()

pname <- paste("pulp_",nid,"_parent.png", sep = "")
png(file = pname, width = 860, height = 480, units = 'px')
ggplot(nodeData, aes(x = Time, y = parent)) +
  geom_line() +
  xlab("") +
  ylab("Parent") +
  scale_x_datetime(breaks = "7 day", labels = date_format("%m-%d\n%H:%M"))
dev.off()

pname <- paste("pulp_",nid,"_seq.png", sep = "")
png(file = pname, width = 860, height = 480, units = 'px')
ggplot(nodeData, aes(x = Time, y = seq)) +
  geom_line() +
  xlab("") +
  ylab("Seq") +
  scale_x_datetime(breaks = "7 day", labels = date_format("%m-%d\n%H:%M"))
dev.off()

pname <- paste("pulp_",nid,"_rssi.png", sep = "")
png(file = pname, width = 860, height = 480, units = 'px')
ggplot(nodeData, aes(x = Time, y = rssi)) +
  geom_line() +
  xlab("") +
  ylab("RSSI") +
  scale_x_datetime(breaks = "7 day", labels = date_format("%m-%d\n%H:%M"))
dev.off()

pname <- paste("pulp_",nid,"_volt.png", sep = "")
png(file = pname, width = 860, height = 480, units = 'px')
ggplot(nodeData, aes(x = Time, y = voltage)) +
  geom_line() +
  xlab("") +
  ylab("Battery (V)") +
  scale_x_datetime(breaks = "7 day", labels = date_format("%m-%d\n%H:%M"))
dev.off()


