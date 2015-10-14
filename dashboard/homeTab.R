library(shinydashboard)

homeTab <- tabItem(
  tabName = "home",
  fluidRow(
    column(width = 9,
           box(width = NULL, solidHeader = TRUE,
               h3("PULP-SEED: Philippines UK coLlaborative Partnership-System for
                  Environmental and Efficient Drying"),
               "PULP-SEED is a British Council Newton Fund Institutional Link between Coventry University, UK
                and the University of San Carlos, Philippines.",
               p(),
               "The institutional link focuses on three areas:",
               tags$ul(
                 tags$li("Technological advances in factory monitoring systems to
                enable creation of new process models and support follow-on automation;"),
                 tags$li("Developmental activities to
                result in staff training for research skills at USC and lessons to be applied to CU"),
                 tags$li("Scoping industry-academia links and link-forming know-how at USC")
               ),
               "All three areas will lead to social and economic impact either
                directly (factory workplaces and promotion of economic model to other factories) or indirectly
                (empowering the Filipino academics to create wealth and social benefit through high standard research).",
               p(),
               "This website presents the PULP-SEED project and provides access to 'live' data from a Wireless Sensor Network (WSN),
                deployed in a mango waste processing factory in Cebu, Phillipines. This WSN is a key component of the first focus
                area 'technological advances in factory monitoring systems to enable creation of new process models and
               support follow-on automation'"
           )
    )
  )
)



