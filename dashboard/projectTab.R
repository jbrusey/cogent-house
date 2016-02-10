library(shinydashboard)

projectTab <- tabItem(
  tabName = "project",
  fluidRow(
    column(
      width = 9,
      box(
        width = NULL,
        solidHeader = TRUE,
        h3(
          "PULP-SEED: Philippines UK coLlaborative Partnership-System for
          Environmental and Efficient Drying"
        ),
        "The Philippines produces around 1 million tonnes of mangoes per year,
        with more than half of this quantity being processed into products
        such as juices, dried fruits, fruit bars, candies and jellies. The
        mango processing industries use only about half of the mango fruit (by
        mass), with the remainder being waste such as the peels, seed husk and
        seed kernel. This mango waste is simply disposed of in open dumpsites
        and left to rot, releasing foul odours and potentially hazardous
        leachate. The waste is also a health hazard, as people scavenging
        dumpsites often eat the freshly discarded mango parts.",
        p(),
        "Recently, a start-up company, GEM, was formed out of the University of
        San Carlos (USC) Department of Chemical Engineering that converts
        waste from the mango processing industry into useful products, using
        novel technology developed at USC. The company began operations in
        2012 with initial seed funding of $2 million. The company built its
        2,500 m^2 facility in a one-hectare land area in Bangkal, Lapu-lapu City, Cebu.",
        p(),
        div(
          tags$img(src = "images/green.jpg", width = "60%"),
          style = "text-align: center;"),
        p(),
        div(
          "The aim of this focus area is to make use of Wireless Sensor Network
          (WSN) technology to improve the yield and efficiency of existing mango
          waste processing. The outcome will therefore be to increase the viability of
          mango waste processing such that it can be scaled up to process all or
          most of the available mango waste currently being produced (current
                                                                      processing only takes waste from 1 of 36 plants in the region). This endeavor will
          lead to job creation and increased social wealth in disadvantaged
          communities in the local region. Furthermore,
          it is envisaged that
          another positive outcome of this work will be to inspire other
          Filipino industries to make greater use of their academic institutions
          as a source of technological innovation.",
          p(),
          tags$ol(
          tags$li("Solar drying facility where direct solar energy is harnessed and
          used as an alternative power source for drying of raw mango waste
          peels and seeds. WSNs can be used to monitor the environmental and
          process conditions inside the facility such as temperature,
          humidity,
          light intensity and so on,
          in order to characterise and model its
          drying mechanisms and properties. The data and information gathered by
          the use of WSNs can help to further improve the design of the dryer.
          The solar power generation system can then achieve high productivity,
          yield and cost - efficiency. Further,
          WSNs
          can assist in studying the effects of direct solar heat on the
          characteristics and properties of dried products."),
          tags$li("WSNs will be deployed in a prototype tunnel dryer used in the
          facility,
          which is used to dry the high - value products from mango
          wastes,
          such as mango flour,
          mango tea,
          pectin,
          and others. Data
          obtained with the help of WSNs will be used to study the effects of
          drying conditions and parameters in the product formulation and to
          describe drying mechanisms. Optimisation of process conditions and
          operating parameters can be achieved with the use of WSNs.")
          ),
          p(),
          "The basis for optimisation of processing will be through forming
          statistical models of the processes that incorporate empirical
          data. These models will then be used to optimise the process in terms
          of efficiency and quality of production through automation
          techniques.",
          p(),
          "This project will have impact in the following areas:",
          tags$ul(
          tags$li("GEM will benefit from more efficient production processes and
          logistics based on the research collaboration outputs."),
          tags$li("The plant's current workforces are drawn from the local
          community. Therefore, enhancing the viability and profitability of
          the mango waste processing plant will provide a boost to the local
          community by enabling a larger work force."),
          tags$li("With the help of CU, USC will build a strong research and skill base
          in wireless sensing technology.")
          ),
          p(),
          "To meet the aims of the project the following objectives have been set:",
          tags$ol(
            tags$li("Analysis of the current monitoring process in place at GEM and the current situation including wastage."),
            tags$li("Analysis of the monitoring requirements to diagnose quality and yield of mango waste processing."),
            tags$li("Development of a prototype system for deployment in a mango solar dryer."),
            tags$li("Development of an optimal drying strategy using both data collected from the WSN and a record of
                    yields and quality of the resulting produce."),
            tags$li("Development of automation techniques to manage the solar dryer environment to maximise yield and quality.")
          )
        )
      )
    )
  )
)



