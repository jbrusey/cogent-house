library(shinydashboard)

documentTab <- tabItem(
  tabName = "documents",
  fluidRow(
    column(width = 9,
           box(width = NULL, solidHeader = TRUE,
               h3("PULP-SEED: Project Document Repository"),
               "All public documents are listed below",
               p(),
               h4("Technical Reports"),
               h5(tags$a(href = "files/PULP-SEED-P1.pdf", "PULP-SEED Factory WSN Deployment")),
               "This report presents initial monitoring results, forming part of the
                focus area: “technological advances in factory monitoring systems to
               enable creation of new process models and support follow-on
               automation”. The aim of this focus area is to make use of Wireless
               Sensor Network (WSN) technology to improve the yield and efficiency of
               existing mango waste processing, thus leading to increased viability
               and scale of operation. This report describes the motivation for the
               project, the development of the WSN system, and the performance of the
               first 60 days of deployment"
           )
    )
  )
)



