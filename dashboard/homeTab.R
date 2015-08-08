library(shinydashboard)

homeTab <- tabItem(
  tabName = "home",
  fluidRow(
    column(width = 9,
           box(width = NULL, solidHeader = TRUE,
               h3("PULP-SEED: Philippines UK coLlaborative Partnership-System for
                  Environmental and Efficient Drying"),
               "The aim of this projectis to make use of Wireless Sensor Network (WSN)
               technology to improve and make more efficient existing mango waste
               processing thus leading to improved viability and increased scale of
               operation.",
               p(),
               "This dashboard provides access to the data collected from a
               live WSN deployment in mango waste processing factory located
               in Lapu-Lapu, Cebu, Philippines"
           )
    )
  )
)
