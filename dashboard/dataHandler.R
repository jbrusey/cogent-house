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
           #ADC_0, ADC_1, ADC_2,
           Voltage, parent, rssi, seq)
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
    rename(Time = X1, temperature = X2, humidity = X3,
           adc0 = X4, adc1 = X5, adc2 = X6,
           voltage = X7, parent = X8, rssi = X9, seq = X10) %>%
    #Cast time to correct value, and align to the nearest 5 mins
    mutate(Time = align.time(
      as.POSIXct(Time, n = 300, tz = "Asia/Manila",origin = "1970-01-01"),
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



