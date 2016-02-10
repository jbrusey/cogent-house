library(shinydashboard)

yieldTab <- tabItem(
  tabName = "dataYield",
  fluidRow(
    column(width = 9,
           box(width = NULL, solidHeader = TRUE, height = 700,
               downloadButton('downloadYield', 'Download Plot'),
               h3("Data Yield for PULP1 (Green house)
                  and PULP2 (Tunnel dryer) Sensor Deployments"),
               plotOutput("dataYieldPlot"))
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
    box(width = NULL, collapsed = FALSE, collapsible = TRUE, title = "Instructions",
        "This plot shows the data yield of the deployed sensors for PULP 1 (greenhouse dryer) and PULP 2 (tunnel dryer).
        It shows the individual node yield over time. Please refer to Deployment Map to find location of
        a particular node in the system.",
        "To display data:",
        tags$ol(
          tags$li("Select the corresponding Date range."),
          tags$li("Select which server(s) you'd like to view.")
        )
    ),
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
