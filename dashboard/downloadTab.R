library(shinydashboard)

downloadTab <- tabItem(
  tabName = "download",
  fluidRow(
    column(width = 9,
           box(width = NULL, solidHeader = TRUE,
               dateRangeInput("downloadDates", label = h3("Select Date range"), start = "2015-08-04"),
               uiOutput("downloadNodeSelect"),
               downloadButton('downloadData', 'Download')
           )
    )
  )
)
