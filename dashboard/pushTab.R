library(shinydashboard)

pushTab <- tabItem(
  tabName = "pushYield",
  fluidRow(
    column(width = 9,
           box(width = NULL, solidHeader = TRUE,
               h3("Plot for the number of data
               pushes from the remote to the central server."),
               plotOutput("pushYieldPlot"),
               downloadButton('downloadPush', 'Download Plot')
           )
    ),
    column(width = 3,
           box(width = NULL, status = "warning",
               dateRangeInput("pushDates", label = h3("Date range"), start = "2015-08-04")
           )
    )
  ),
  box(width = NULL, collapsed = FALSE, collapsible = TRUE, title = "Instructions",
      "This plot shows server status for PULP 1 (greenhouse dryer) and PULP 2 (tunnel dryer). We expect 24 pushes per day (one data push per hour).",
      "To display data:",
      tags$ol(
        tags$li("Select the corresponding Date range."),
        tags$li("Select which server(s) you'd like to view.")
      )
  )
)
