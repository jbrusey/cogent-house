source("dataHandler.R")
source("config.R")
library(dplyr)
library(lubridate)
library(ggplot2)
library(RColorBrewer)

function(input, output, session) {

#-------------------------------- PREP DATA ------------------------------------------
  #Ideally needs to be reactive to new data
  DAILY_TX = 288
  nData <- readNodeData(basedir)
  aNodes <- as.numeric(unique(nData$NodeId))
  aNodes <- sort(aNodes)
  aLong <- gather(nData, measure, value, Temperature:Seq)
  pushData <- readPushLog(basedir)
  peopleData <- read_csv(file = "./config/team.csv")

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

  plotMeasurement <- reactive({
    # Load data
    data <- measuremntData()

    data$measure <- gsub("Temperature", "Temperature (C)", data$measure)
    data$measure <- gsub("Humidity", "Relative Humidity (%)", data$measure)


    g <- ggplot(data, aes(x = Time, y = value, group = NodeId, colour = NodeId)) +
      geom_line() +
      facet_grid(measure ~ .,scales = "free_y") +
      ylab("") +
      xlab("") +
      #colScale +
      theme(legend.title = element_blank())
  })

  output$measurementPlot <- renderPlot({
    print(plotMeasurement())
    })

  output$downloadMeasurement <- downloadHandler(
    filename = function() { paste('Plot.pdf', sep = '') },
    content = function(file) {
      ggsave(file, plot = plotMeasurement(), width = 6, height = 3.5)
    }
  )

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

  plotSystem <- reactive({
    data <- systemData()

    data$measure <- gsub("Seq", "Sequence Number", data$measure)
    data$measure <- gsub("Parent", "Parent Id", data$measure)
    data$measure <- gsub("Voltage", "Battery Voltage (V)", data$measure)

    g <- ggplot(data, aes(x = Time, y = value, group = NodeId, colour = NodeId)) +
      geom_point() +
      facet_grid(measure ~ .,scales = "free_y") +
      ylab("") +
      xlab("") +
      theme(legend.title = element_blank())
    })

  output$systemPlot <- renderPlot({
    print(plotSystem())
    })

  output$downloadSystem <- downloadHandler(
    filename = function() { paste('Plot.pdf', sep = '') },
    content = function(file) {
      ggsave(file, plot = plotSystem(), width = 6, height = 3.5)
    }
  )

  #-------------------------------- CONTACTS TAB -----------------------------------------

  output$peopleTable <- renderDataTable({
    out <- peopleData
  }, options = list(searching = FALSE, paging = FALSE, pageLength = 10))

  #-------------------------------- STATUS TAB -------------------------------------------
  jData <- reactive({
    readings <- readJSONLog(tmpdir)
    sorted_readings <- arrange(.data = readings, sender)
    return(sorted_readings)
  })

  output$readingTable <- renderDataTable({
    out <- jData()
  }, options = list(searching = FALSE, pageLength = 50))

  #-------------------------------- PUSH YIELD TAB ------------------------------------

  pushYield <- reactive({
    out <- pushData %>%
      filter(
        Time >= as.POSIXct(input$pushDates[1], tz = "Asia/Manila", origin = "1970-01-01"),
        Time <= as.POSIXct(input$pushDates[2] + 1, tz = "Asia/Manila", origin = "1970-01-01")
      ) %>%
      mutate(Date = as.Date(Time)) %>%
      group_by(Server, Date) %>%
      summarise(Pushes = n())

    shiny::validate(
      need(!is.null(out),  'Sorry, no data available for the selection')
    )
    return(out)
  })

  plotPush <- reactive({
    daily_pushes <- pushYield()

    g <- ggplot(daily_pushes, aes(x = Date, y = Server, fill = Pushes)) +
      geom_tile(colour="White") +
      labs(x = "", y = "Server") +
      scale_fill_gradient2(low = "firebrick", mid="lightgreen", high = "darkgreen", midpoint=12) +
      facet_grid(Server ~ ., scales = "free_y")
  })

  output$pushYieldPlot <- renderPlot({
    print(plotPush())
  })

  output$downloadPush <- downloadHandler(
    filename = function() { paste('Plot.pdf', sep = '') },
    content = function(file) {
      ggsave(file, plot = plotPush(), width = 6, height = 3.5)
    }
  )

  #-------------------------------- DATA YIELD TAB ------------------------------------

  dataYield <- reactive({
    shiny::validate(
      need(expr = (length(input$serverSelect) > 0), 'Please select at least one sensor')
    )

    out <- nData %>%
      filter(
        Time >= as.POSIXct(input$yieldDates[1], tz = "Asia/Manila", origin = "1970-01-01"),
        Time <= as.POSIXct(input$yieldDates[2] + 1, tz = "Asia/Manila", origin = "1970-01-01")
      ) %>%
      mutate(Date = as.Date(Time),
             val = ifelse(is.na(Temperature), 0, 1),
             NodeId = as.numeric(NodeId),
             Server = ifelse(NodeId <= 30, "PULP1", "PULP2")
      ) %>%
      select(NodeId, Server, Date, val) %>%
      group_by(NodeId, Server, Date) %>%
      summarise(
        pkts = sum(val)
      ) %>%
      mutate(
        yield = (pkts / DAILY_TX) * 100.0,
        yield = ifelse(yield > 100 ,100, yield)
      ) %>%
      filter(
        Server %in% input$serverSelect
      )

    shiny::validate(
      need(!is.null(out),  'Sorry, no data available for the selection')
    )
    return(out)
  })

  plotYield <- reactive({
    daily_node_yield <- dataYield()

    g <- ggplot(daily_node_yield, aes(x = Date, y = NodeId, fill = yield)) +
      geom_tile(colour = "white") +
      labs(x = "", y = "Node Id") +
      scale_y_continuous(breaks =
                           min(daily_node_yield$NodeId):max(daily_node_yield$NodeId)
      ) +
      scale_fill_gradient2(low = "firebrick", mid="lightgreen", high = "darkgreen", midpoint=50) +
      facet_grid(Server ~ ., scales = "free_y")

  })

  output$dataYieldPlot <- renderPlot({
    print(plotYield())
  }, height = 600)

  output$downloadYield <- downloadHandler(
    filename = function() { paste('Plot.pdf', sep = '') },
    content = function(file) {
      ggsave(file, plot = plotYield(), width = 6, height = 7)
    }
  )

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
     selectizeInput("nodeSel", "Node(s):",
                    choices = aNodes, multiple = TRUE, selected = NULL)
   })

   #repeat node select (must be a better way to do this)
   output$systemNodeSelect <- renderUI({
     selectizeInput("sysNodeSel", "Node(s):",
                    choices = aNodes, multiple = TRUE, selected = NULL)
   })

   #repeat node select (must be a better way to do this)
   output$downloadNodeSelect <- renderUI({
     selectizeInput("downloadNodeSelect", "Select Node(s):",
                    choices = aNodes, multiple = TRUE, selected = NULL)
   })
}
