source("dataHandler.R")
source("config.R")
library(dplyr)
library(lubridate)
library(ggplot2)
library(RColorBrewer)

function(input, output, session) {

  #-------------------------------- PREP DATA ------------------------------------------
  #Ideally needs to be reactive to new data
  nData <- readNodeData(basedir)
  aNodes <- unique(nData$NodeId)
  aLong <- gather(nData, measure, value, temperature:seq)

  #-------------------------------- DATA TAB -------------------------------------------
  measuremntData <- reactive({
    shiny::validate(
      need(expr = (length(input$sensorSelect) > 0), 'Please select at least one sensor'),
      need(expr = (length(input$nodeSel) > 0), 'Please select at least one node')
    )
     out <- aLong %>%
       filter(NodeId %in% c(input$nodeSel),
              measure %in% input$sensorSelect,
              Time >= as.POSIXct(input$dates[1], tz = "Asia/Manila", origin = "1970-01-01"),
              Time <= as.POSIXct(input$dates[2] + 1, tz = "Asia/Manila", origin = "1970-01-01")
              )

     shiny::validate(
       need(!is.null(out),  'Sorry, no data available for the selection')
       )
     return(out)
   })

  output$measurementPlot <- renderPlot({
    # Load data
    data <- measuremntData()

    #myColors <- brewer.pal(length(aNodes),"Set1")
    #names(myColors) <- aNodes
    #colScale <- scale_colour_manual(name = "grp",values = myColors)

    data$measure <- gsub("Temperature", "Temperature (C)", data$measure)
    data$measure <- gsub("Humidity", "Relative Humidity (%)", data$measure)

    g <- ggplot(data, aes(x = Time, y = value, group = NodeId, colour = NodeId)) +
      geom_line() +
      facet_grid(measure ~ .,scales = "free_y") +
      ylab("") +
      xlab("") +
      #colScale +
      theme(legend.title = element_blank())
    print(g)
    })

  #-------------------------------- SYSTEM TAB ----------------------------------------
  systemData <- reactive({
    shiny::validate(
      need(expr = (length(input$systemSelect) > 0), 'Please select at least one sensor'),
      need(expr = (length(input$sysNodeSel) > 0), 'Please select at least one node')
      )

    #If a new sensor doesn't appear try changing this, need to find a work around
    sout <- aLong %>%
      filter(NodeId %in% input$sysNodeSel,
             measure %in% input$systemSelect,
             Time >= as.POSIXct(input$sysDates[1], tz = "Asia/Manila", origin = "1970-01-01"),
             Time <= as.POSIXct(input$sysDates[2] + 1, tz = "Asia/Manila", origin = "1970-01-01")
             )

    shiny::validate(
      need(!is.null(sout),  'Sorry, no data available for the selection')
      )
    return(sout)
    })

  output$systemPlot <- renderPlot({
    data <- systemData()

    data$measure <- gsub("seq", "Sequence Number", data$measure)
    data$measure <- gsub("parent", "Parent Id", data$measure)
    data$measure <- gsub("voltage", "Battery Voltage (V)", data$measure)
    data$measure <- gsub("rssi", "RSSI", data$measure)

    g <- ggplot(data, aes(x = Time, y = value, group = NodeId, colour = NodeId)) +
      geom_point() +
      facet_grid(measure ~ .,scales = "free_y") +
      ylab("") +
      xlab("") +
      theme(legend.title = element_blank())

    print(g)

    })

  #-------------------------------- NETWORK TAB ---------------------------------------

  #-------------------------------- STATUS TAB -------------------------------------------
  jData <- reactive({
    readings <- readJSONLog(tmpdir)
    sorted_readings <- arrange(.data = readings, sender)
    return(sorted_readings)
  })

  output$readingTable <- renderDataTable({
    out <- jData()
  }, options = list(searching = FALSE))

  #-------------------------------- LOG TAB -------------------------------------------
  deploymentData <- reactive({#To-Do: Don't think this needs to be reactive
    #Horrible needs simplifying (read log file and ouput)
    log <- read_csv(deployment_log_file)
    log$Date <- as.Date(log$Date)
    log <- arrange(.data = log, Date)
    return(log)
  })

  output$deploymentLog <- renderDataTable({
    out <- deploymentData()
    },options = list(searching = FALSE))

  #-------------------------------- DOWNLOAD TAB -------------------------------------------
  downloadData <- reactive({
    out <- nData %>%
      filter(NodeId %in% c(input$downloadNodeSelect),
             Time >= as.POSIXct(input$downloadDates[1], tz = "Asia/Manila", origin = "1970-01-01"),
             Time <= as.POSIXct(input$downloadDates[2] + 1, tz = "Asia/Manila", origin = "1970-01-01")
      )

    return(out)
  })

  output$downloadData <- downloadHandler(
    filename = function() { paste('PULP-Data.csv', sep = '') },
    content = function(file) {
      write.csv(downloadData(), file, row.names = FALSE)
    }
  )

  #-------------------------------- SIDEBAR -------------------------------------------

   #Node select checkbox group box
   output$nodeSelect <- renderUI({
     nodes <- unique(nData$NodeId)
     selectizeInput("nodeSel", "Node(s):",
                    choices = nodes, multiple = TRUE, selected = NULL)
   })

   #repeat node select (must be a better way to do this)
   output$systemNodeSelect <- renderUI({
     nodes <- unique(nData$NodeId)
     selectizeInput("sysNodeSel", "Node(s):",
                    choices = nodes, multiple = TRUE, selected = NULL)
   })

   #repeat node select (must be a better way to do this)
   output$downloadNodeSelect <- renderUI({
     nodes <- unique(nData$NodeId)
     selectizeInput("downloadNodeSelect", "Select Node(s):",
                    choices = nodes, multiple = TRUE, selected = NULL)
   })
}
