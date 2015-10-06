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
  )
)
