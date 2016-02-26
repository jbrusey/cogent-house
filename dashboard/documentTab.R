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
               box(width = 15, solidHeader = TRUE,
               h5("Title:", tags$a(href = "files/PULP-SEED-P1.pdf", "PULP-SEED Factory WSN Deployment")),
               h5("Author(s): Ross Wilkins, Elena Gaura, James Brusey, John Kemp"),
               h5("Publication date: January 2016"),
               h5("Abstract:"),
               "This report presents initial monitoring results, forming part of the
               focus area: 'technological advances in factory monitoring systems to
               enable creation of new process models and support follow-on
               automation'. The aim of this focus area is to make use of Wireless
               Sensor Network (WSN) technology to improve the yield and efficiency of
               existing mango waste processing, thus leading to increased viability
               and scale of operation. This report describes the motivation for the
               project, the development of the WSN system, and the performance of the
               first 60 days of deployment."),
               box(width = 15, solidHeader = TRUE,
                   h5("Title:", tags$a(href = "http://blogs.coventry.ac.uk/researchblog/philippines-first-wirelessly-instrumented-factory-through-collaboration-between-cu-and-university-of-san-carlos/", "Philippines' First Wirelessly Instrumented Factory through Collaboration between CU and University of San Carlos")),
                   h5("Author(s): Coventry University"),
                   h5("Publication date: November 2015"),
                   h5("Abstract:"),
                   "The Philippines-UK collaborative Partnership-System for
                   Environmental and Efficient Drying (PULP-SEED) is a
                   British Council Newton Fund Institutional
                   Link between Coventry University (CU),
                   UK and the University of San Carlos (USC), Philippines.
                   As part of this project, CU's Cogent Labs,
                   in collaboration with the USC, have developed
                   the Philippines' first wirelessly instrumented factory.
                   This wireless system aims to improve the efficiency
                   and capacity of a mango by-product processing factory.")
           )
    )
  )
)





