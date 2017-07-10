library(shinydashboard)


deploymentMapTab <- tabItem(
  tabName = "deploymentMap",
  fluidRow(
    column(width = 12,
           tabBox(
             side = "left",
             width = 800,
             selected = "Solar Dryer (PULP 1)",
             tabPanel("Solar Dryer (PULP 1)",
                      div(
                        tags$img(src = "images/SolarDryingFacility.jpg", width = 900)
                        )
                      ),
             tabPanel("Tunnel Dryer (PULP 2)",
                      div(
                        tags$img(src = "images/TunnelDeployment.jpg", width = 800)
                        )
             )
           )
    )
  )
)
