library(shinydashboard)

dataTab <- tabItem(
  tabName = "data",
  fluidRow(
    column(width = 9,
           box(width = NULL, solidHeader = TRUE,
               plotOutput("measurementPlot"),
               downloadButton('downloadMeasurement', 'Download Plot')
           )
    ),
    column(width = 3,
           box(width = NULL, status = "warning",
               dateRangeInput("dates", label = h3("Date range"), start = "2015-08-04"),
               checkboxGroupInput("sensorSelect", "Select Sensor",
                                  choices = c(
                                    "Temperature" = "temperature",
                                    "Humidity" = "humidity"
                                  ),
                                  selected = "temperature"
               ),
               uiOutput("nodeSelect")
           )
    )
  )
)
