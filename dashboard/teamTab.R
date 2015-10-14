library(shinydashboard)

teamTab <- tabItem(
  tabName = "team",
  fluidRow(
    column(width = 9,
           box(width = NULL, solidHeader = TRUE,
               h3("PULP-SEED: Project Team"),
               "The team working on this project is a multi-disciplinary group consisting of electrical engineers,
               computer scientists, and chemical engineers from both Coventry University and the University of San Carlos.
               The following table lists the members of this project.",
               p(),
               dataTableOutput("peopleTable")
           )
    )
  )
)



