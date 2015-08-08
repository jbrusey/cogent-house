library(shinydashboard)

systemTab <- tabItem(
  tabName = "system",
  fluidRow(
    column(width = 9,
           box(width = NULL, solidHeader = TRUE,
               plotOutput("systemPlot")
           )
    ),
    column(width = 3,
           box(width = NULL, solidHeader = TRUE, status = "warning",
               dateRangeInput("sysDates", label = h3("Date range"), start = "2015-08-04"),
               checkboxGroupInput("systemSelect", "Select Parameters:",
                                  choices = c(
                                    "Battery Voltage" = "voltage",
                                    "Sequence Number" = "seq",
                                    "RSSI" = "rssi",
                                    "Parent Id" = "parent"
                                  ),
                                  selected = "seq"
               ),
               uiOutput("systemNodeSelect")
           )
    )
  )
)
