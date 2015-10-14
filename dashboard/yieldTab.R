library(shinydashboard)

yieldTab <- tabItem(
  tabName = "dataYield",
  fluidRow(
    column(width = 9,
           box(width = NULL, solidHeader = TRUE, height = 700,
               downloadButton('downloadYield', 'Download Plot'),
               plotOutput("dataYieldPlot")
           )
    ),
    column(width = 3,
           box(width = NULL, status = "warning",
               dateRangeInput("yieldDates", label = h3("Date range"), start = "2015-08-04"),
               checkboxGroupInput("serverSelect", "Select Server:",
                                  choices = c(
                                    "PULP1" = "PULP1",
                                    "PULP2" = "PULP2"
                                  ),
                                  selected = "PULP1"
               )
           )
    ),height = 800, width = 980
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
