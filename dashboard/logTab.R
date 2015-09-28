library(shinydashboard)

logTab <- tabItem(
  tabName = "log",
  fluidRow(
    column(width = 12,
           box(width = NULL, solidHeader = TRUE,
               dataTableOutput("deploymentLog")
           )
    )
  )
)
