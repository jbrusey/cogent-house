library(shinydashboard)

systemTab <- tabItem(
  tabName = "system",
  fluidRow(
    column(width = 9,
           box(width = NULL, solidHeader = TRUE,
               plotOutput("systemPlot"),
               downloadButton('downloadSystem', 'Download Plot')
           )
    ),
    column(width = 3,
           box(width = NULL, status = "warning",
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
  ),
  fluidRow(
    box(width = NULL, collapsed = TRUE, collapsible = TRUE, title = "Deployment Map",
        tabBox(
          side = "left",
          width = 800,
          selected = "Solar Dryer (PULP 1)",
          tabPanel("Solar Dryer (PULP 1)",
                   div(tags$img(src = "images/SolarDryingFacility.jpg", width = 900))
          ),
          tabPanel("Tunnel Dryer (PULP 2)",
                   div(tags$img(src = "images/TunnelDeployment.jpg", width = 800))
          )
        )
    )
  )
)
