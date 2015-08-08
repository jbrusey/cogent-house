source("homeTab.R")
source("statusTab.R")
source("dataTab.R")
source("systemTab.R")
#source("downloadTab.R")
source("networkTab.R")
#source("serverTab.R")
source("logTab.R")
source("downloadTab.R")
library(shinydashboard)

header <- dashboardHeader(
  title = "Caldecott analysis"
)


sidebar <- dashboardSidebar(
  sidebarMenu(
    menuItem("Home", tabName = "home", icon = icon("home")),
    menuItem("Node Status", tabName = "status", icon = icon("signal")),
    menuItem("Data", tabName = "data", icon = icon("line-chart")),
    menuItem("System", tabName = "system", icon = icon("laptop")),
    #menuItem("Network", tabName = "network", icon = icon("wifi")),
    menuItem("Deployment Log", tabName = "log", icon = icon("calendar")),
    menuItem("Download Data", tabName = "download", icon = icon("download"))
  )#,
  #text = uiOutput("timeSinceLastPushUpdate")
)


body <- dashboardBody(
  tabItems(
    homeTab,
    statusTab,
    dataTab,
    #networkTab,
    systemTab,
    logTab,
    downloadTab
    )
)

dashboardPage(
  header,
  sidebar,
  body
)
