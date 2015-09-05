library(shinydashboard)

yieldTab <- tabItem(
  tabName = "dataYield",
  fluidRow(
    column(width = 9,
           box(width = NULL, solidHeader = TRUE,
               plotOutput("dataYieldPlot")
           )
    ),
    column(width = 3,
           box(width = NULL, status = "warning",
               dateRangeInput("yieldDates", label = h3("Date range"), start = "2015-08-04")
           )
    )
  )
)
