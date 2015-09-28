source("homeTab.R")
source("statusTab.R")
source("dataTab.R")
source("systemTab.R")
source("yieldTab.R")
source("pushTab.R")
#source("pushTab.R")
source("logTab.R")
source("downloadTab.R")
library(shinydashboard)

header <- dashboardHeader(
  title = "PULP dashboard"
)


sidebar <- dashboardSidebar(
  sidebarMenu(
    menuItem("Home", tabName = "home", icon = icon("home")),
    menuItem("Data", icon = icon("line-chart"),
             menuItem("Node Status", tabName = "status", icon = icon("signal")),
             menuItem("Sensor Data", tabName = "data", icon = icon("line-chart")),
             menuItem("System Data", tabName = "system", icon = icon("line-chart"))
             ),
    menuItem("System Performance", icon = icon("laptop"),
             menuItem("Data Yield", tabName = "dataYield", icon = icon("line-chart")),
             menuItem("Server Status", tabName = "pushYield", icon = icon("signal"))
             ),
    menuItem("Deployment Log", tabName = "log", icon = icon("calendar")),
    menuItem("Download Data", tabName = "download", icon = icon("download"))
  )
)


body <- dashboardBody(
  tabItems(
    homeTab,
    statusTab,
    dataTab,
    systemTab,
    yieldTab,
    pushTab,
    logTab,
    downloadTab
    )
)

dashboardPage(
  header,
  sidebar,
  body
)
