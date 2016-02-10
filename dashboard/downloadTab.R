library(shinydashboard)

downloadTab <- tabItem(
  tabName = "download",
  fluidRow(
    column(width = 9,
           box(width = NULL, solidHeader = TRUE,
               h3("PULP-SEED Data Download Page"),
               dateRangeInput("downloadDates", label = h3("Select Date range"), start = "2015-08-04"),
               uiOutput("downloadNodeSelect"),
               downloadButton('downloadData', 'Download')
           )
    )
  ),
  box(width = NULL, collapsed = FALSE, collapsible = TRUE, title = "Instructions",
      "This page lets you download data from the PULP-SEED Project in CSV format.
      You may specify the inclusive dates, and nodes from the contraols above.
      The downloaded file has 11 columns:",p(),
      tags$ul(
        tags$li("Time-the timestamp when the data was collected (unix timestamp)"),
        tags$li("NodeId - the node name as specified in the deployment map for PULP1 and PULP2."),
        tags$li("Temperature-the air temperature in degrees Celsius."),
        tags$li("Humidity - the % relative humidity."),
        tags$li("Solar - the solar sensor analog voltage value."),
        tags$li("AirFlow - the airflow analog voltage value."),
        tags$li("Blackbulb - the blackbulb analog voltage value."),
        tags$li("Voltage - this is the battery voltage a sensor node has.")
      )
  ),
  box(width = NULL, collapsed = TRUE, collapsible = TRUE, title = "Deployment Map",
      tabBox(
        side = "left",
        width = 800,
        selected = "Solar Dryer (PULP 1)",
        tabPanel("Solar Dryer (PULP 1)",
                 div(tags$img(src = "images/SolarDryingFacility.jpg", width = 900))
        ),
        tabPanel("Tunnel Dryer (PULP 2)",
                 div(tags$img(src = "images/TunnelDeployment.jpg", width = 800))
        )
      )
  )
)
