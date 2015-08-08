library(shinydashboard)

networkTab <- tabItem(
  tabName = "network",
  fluidRow(
    column(width = 9,
           box(width = NULL, solidHeader = TRUE,
               "plot"
           )
    )
  )
)
