library(shinydashboard)

factoryTab <- tabItem(
  tabName = "factory",
  fluidRow(
    column(width = 9,
           box(width = NULL, solidHeader = TRUE,
               h3("PULP-SEED: The Factory"),
               "Green Enviro Management Systems, Inc. (GEMS) (http://www.greenenviromanagementsystems.com/) is
               engaged in holistic and integrated approaches to (food & agricultural) waste management.",
               p(),
               "GEMS have dveloped two mango waste drying processes in the factory i) a solar dryer
               and ii) a tunnel dryer. Both drying methods process three main mango
               by-products---mango seeds, mango kernels and mango husks. The process
               fully converts this raw material into useful products, leaving no
               waste at all. Two drying processes namely solar and
               tunnel drying are presented here.",
               p(),
               "The solar dryer initiates drying of wet mango waste. Once dry the wastge is grounded using a screw press.
                The resultent material is then further dried in the tunnel dryer.", p(),
               h4("The Solar Dryer"),
               "The solar dryer is a brick building with a transparent polycarbonate
               roof measuring 30m X 30m X 3m. Within the solar dryer there are 36
               drying racks (5.55m X 1.15m X 2m) with 5 drying trays. The flooring of
               each tray is made from nylon netting to allow sunlight the penetrate
               lower levels.", p(),
               "In the solar dryer wet mango waste is spread on the trays twice a day
               at 8am and 4pm. This can not be done at any other time due to extreme
               heat and risk to workers. The mango placed at 8am is usually fully
               dried by 4pm when the new batch is laid out. There is little drying
               during night time but the mango peels and seeds placed at 4pm will be
               ready for the following day.", p(),
               div(
                 tags$img(src = "images/greenhouse.jpg", width = 580),
                 style = "text-align: center;"),
               h4("The Tunnel Dryer"),
               "The tunnel dryer measures 11m X 1.5m X 1.5m and is made entirely of
               stainless steel. The tunnel has ramps on both sides to allow the racks
               to be loaded/unloaded into the dryer. On one side of the tunnel are
               ten 1kW resistive heaters connected to a temperature control panel on
               the outside. The other side of the tunnel has 5 circulation fans, with
               5 exhaust fans directly above to remove cold air.",p(),
               "To dry the mango waste, nine racks of the waste are loaded into the
               tunnel dryer and both ends of the tunnel are sealed. Once ready the
               dryer is switched on for four hours with a set point temperature of
               65 degrees Celsius. After 4 hours the dried product is unloaded and the workers
               check if the mango waste has dried. If not, the product is stirred on
               its tray to remix so wet layers are exposed for the next drying
               time. The mango waste will then undergo another set of drying for four
               hours until completely dry.", p(),
               div(
                 tags$img(src = "images/tunnel.jpg", width = 580),
                 style = "text-align: center;")
           )
    )
  )
)



