library(shinydashboard)

deploymentTab <- tabItem(
  tabName = "deployment",
  fluidRow(
    column(width = 9,
           box(width = NULL, solidHeader = TRUE,
               h3("PULP-SEED: Wireless Sensor Network"),
               "The PULP system is a full end-to-end WSN environmental monitoring
               system targeted at collection of data from the drying
               environment. PULP is designed to gather sensor data (temperature,
               humidity, radiant heat, air flow) and transmit that data to a central
               database where it can be viewed with a web-browser (this site).",p(),
               div(
                 tags$img(src = "images/System.jpg", width = "75%"),
                 style = "text-align: center;"),p(),
               "The diagram above shows the an overview of the end-to-end system
               architecture. Data flows from the sensor nodes to a gateway, where it
               is transmitted to a remote server via the Internet and made available
               to user applications, such as a data analysis portal and further used
               to create a mango drying model. To reduce risk and development time,
               we opted to use off-the-shelf hardware and software wherever
               possible.", p(),
               h4("System Hardware Description"),
               "Our sensor node combines the TelosB platform with a custom interface
               board. The TelosB is based around an MSP430 F1611 CPU and a 2.4 GHz
               CC2420 802.15.4 radio. The TelosB also includes an integrated
               temperature and relative humidity sensor---the Sensirion SHT11. Our
               custom interface board provides input for one black-bulb sensor and
               one air flow sensor. Each sensor node is packaged in an off-the-shelf
               IP65 plastic enclosure with an slot for the air flow sensor. Nodes are
               affixed to the shelf supports using two cable ties.", p(),
               "The gateway was built using a Raspberry Pi 2 model B combined with a
               TelosB node.",
               h4("System Software Description"),
               "The diagram below shows the system flow. A set of WSN nodes transmit
                their data. The sink node (connected to the gateway) receives packets
               from each individual sensor node and forwards these messages via USB
               to the gateway server. The gateway server receives these messages
               through the SerialForwarder program, which opens a packet source (in
               this case the USB-connected sink node) and lets many applications
               connect to it using TCP/IP streams in order to use that
               source. FlatLogger is one such application. FlatLogger receives
               packets from SerialForwarder, extracts the relevant data, and logs the
               data to a flat file. Each hour a Push Data script is run which
               transmits the logged data to a PHP page on the remote server where it
               is archived. Finally this data can be interrogated and downloaded via
               a data portal hosted on the remote server.",p(),
               "This system is open source and the code can be found at
               https://github.com/jbrusey/cogent-house/tree/pulp.",
               div(
                 tags$img(src = "images/SystemFlow.png", width = "75%"),
                 style = "text-align: center;"),p(),
               h3("PULP-SEED: Deployment Description"),
               "From August 2015 our system has been deployed in the GEM factory in
                Cebu, Philippines. The main goals of the deployment are to:
               i) validate the performance of our system in-situ, and ii) collect an
               archive of data for offline analysis which can be used to build the
               drying model.", p(),
               "The PULP system has been deployed in 2 areas of the GEM factory:",
               p(),
               h4("Solar Dryer Deployment"),
               "The solar dryer is the factories primary method of drying out mango
               peel and kernels. A total of 30 nodes have been deployed in the solar
               dryer transmitting to a single server (Pulp1). 15 nodes (Nodes 1--15)
               have been deployed on a bracket at 2.13m in height. The other 15
               nodes (Nodes 15--30) have been deployed on a bracket lower down at
               0.6m. The nodes have been deployed in a 5m X 5m grid.",p(),
               div(
                 tags$img(src = "images/SolarDryingFacility.jpg", width = "25%"),
                 tags$img(src = "images/greenhouse_node.jpg", width = "25%"),
                 style = "text-align: center;"),
               h4("Tunnel Dryer Deployment"),
               "Within the drying tunnel a total of 10 nodes (Nodes 31--40) have been
               deployed. Since the tunnel is made from stainless steel, the server
               (Pulp2) is placed outside of the casing, with the sink node passed
               through a hole cut out into the tunnel.",p(),
               div(
                 tags$img(src = "images/TunnelDeployment.jpg", width  = "25%"),
                 tags$img(src = "images/tunnelNode.jpg", width  = "25%"),
                 style = "text-align: center;")
           )
    )
  )
)



