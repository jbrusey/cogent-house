library(shinydashboard)

logTab <- tabItem(
  tabName = "log",
  fluidRow(
    column(width = 12,
           box(width = NULL, solidHeader = TRUE,
               h3("PULP-SEED Deployment Log"),p(),
               "The deployment log indicates the
               dates when PULP1 and PULP2 were deployed. It
               also indicates the changes done on each deployment.",p(),
               dataTableOutput("deploymentLog")
           )
    )
  )

)
