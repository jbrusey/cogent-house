library(shinydashboard)

statusTab <- tabItem(
  tabName = "status",
  fluidRow(
    column(width = 12,
           box(width = NULL, solidHeader = TRUE,
               dataTableOutput("readingTable")
           )
    )
  )
)
