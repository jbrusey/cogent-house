library(shinydashboard)

pushTab <- tabItem(
  tabName = "pushYield",
  fluidRow(
    column(width = 9,
           box(width = NULL, solidHeader = TRUE,
               plotOutput("pushYieldPlot"),
               downloadButton('downloadPush', 'Download Plot')
           )
    ),
    column(width = 3,
           box(width = NULL, status = "warning",
               dateRangeInput("pushDates", label = h3("Date range"), start = "2015-08-04")
           )
    )
  )
)
