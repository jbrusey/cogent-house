library(dplyr)
library(rjson)
library(readxl)
library(tidyr)
library(xts)
library(readr)

############## PROCESS JSON LOG FILES ###########################

readJSONFile <- function(fname){
  #Open file and cast to a data frame
  JSONData <- as.data.frame(fromJSON(file = fname)) %>%
    #Select the required fields
    select(sender, server_time, Temperature, Humidity,
           ADC_1, ADC_2,
           Voltage, parent, rssi, seq) %>%
    rename(AirFlow = ADC_1,
           BlackBulb = ADC_2) %>%
    mutate(
      AirFlow = ifelse(sender < fullSensors, "NA", AirFlow),
      BlackBulb = ifelse(sender < fullSensors, "NA", BlackBulb)
    )
  #return data
  return(JSONData)
}

readJSONLog <- function(dir){
  #Find all JSON log files in the tmp directory
  files <- list.files(dir, full.names = TRUE, pattern = "node_.*\\.log$")
  #for all files run readJSONFile fuction
  json_list <- lapply(files, readJSONFile)
  #Flatten the data list into a single data frame
  json_data  <- do.call(rbind , json_list)

  json_data  <- json_data %>%
    #Cast all data the correct types
    mutate(server_time =
      as.character(
        as.POSIXct(server_time, tz = "Asia/Manila", origin = "1970-01-01")
       ),
      sender = as.integer(sender),
      seq = as.integer(seq),
      parent = as.integer(parent),
      rssi = as.integer(rssi)
    )
  #Return the data
  return(json_data)
}

############## PROCESS NODE DATA FILES ###########################

readNodeFile <- function(fname) {
  #Read in csv file (readr)
  data <- read_csv(fname,col_names = FALSE)
  #Extract node Id from the file name
  nid <- (strsplit(fname, "_")[[1]])[2]
  data$NodeId <- as.numeric(nid)


  data <- data %>%
    #Rename the fields to something meaningful
    rename(Time = X1, Temperature = X2, Humidity = X3,
           Solar = X4, AirFlow = X5, BlackBulb = X6,
           Voltage = X7, Parent = X8, RSSI = X9, Seq = X10) %>%
    # filter
      filter(Temperature >= 15, Temperature < 100,
             Humidity >= 0, Humidity < 100,
	     Solar >= 0, Solar < 3.5,
             AirFlow >= 0, AirFlow < 3.5,
             BlackBulb>= 0, BlackBulb < 3.5,
      	     Voltage >= 0, Voltage < 5,
             RSSI >= -150, RSSI < 0) %>%
    #Cast time to correct value, and align to the nearest 5 mins
    mutate(Time = align.time(
      as.POSIXct(Time, n = 300, tz = "Asia/Manila",origin = "1970-01-01"),
      5*60)) %>%
    mutate(
      AirFlow = ifelse(NodeId < fullSensors, 0, AirFlow),
      BlackBulb = ifelse(NodeId < fullSensors, 0, BlackBulb)
    )

  #This section of code finds all the times that could have
  # occured between the start and end of the data stream. Missing
  # times are added to the dataframe, this is done to stop ggplot
  # using linear interpolation
  time.max <- max(data$Time, na.rm=TRUE)
  time.min <- min(data$Time, na.rm=TRUE)
  all.dates <- seq(time.min, Sys.time(), by = "5 mins")
  all.dates.frame <- data.frame(list(Time = all.dates))
  all.dates.frame$NodeId <- nid
  data <- merge(all.dates.frame, data, all = T)

  #return processed data
  return(data)
}

readNodeData <- function(dir){
  #Find a list of all node files they are in the format node_<id>_gnu.csv
  files <- list.files(dir, full.names = TRUE, pattern = "node_.*\\_gnu.csv$")
  #apply the readNodeFile function to each file name
  csv_list <- lapply(files, readNodeFile)
  #Bind all data together to form one data frame
  csv_data  <- do.call(rbind, csv_list)
  #return processed data
  return(csv_data)
}

############## PROCESS PUSH LOG ###########################

readPushLog <- function(dir){
  fname <- paste(basedir, "push.log", sep = "")
  data <- read_csv(fname, col_names = c("Time","Server"), col_types = list(
    Time = col_datetime(),
    Server = col_character()
  ))
  return(data)
}



