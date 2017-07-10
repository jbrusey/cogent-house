source("homeTab.R")
source("projectTab.R")
source("factoryTab.R")
source("teamTab.R")
source("deploymentTab.R")

source("deploymentMapTab.R")
source("statusTab.R")
source("dataTab.R")
source("systemTab.R")

source("yieldTab.R")
source("pushTab.R")
source("logTab.R")
source("downloadTab.R")

source("documentTab.R")

library(shinydashboard)

header <- dashboardHeader(
  title = "PULP dashboard"
)


sidebar <- dashboardSidebar(
  sidebarMenu(
    menuItem("Home", tabName = "home", icon = icon("home")),
    menuItem("Project Information", icon = icon("university"),
             menuItem("Project Motivation", tabName = "project", icon = icon("university")),
             menuItem("The Factory", tabName = "factory", icon = icon("building")),
             menuItem("WSN Deployment", tabName = "deployment", icon = icon("signal")),
             menuItem("Project Team", tabName = "team", icon = icon("users"))
    ),
    menuItem("WSN Data Portal", icon = icon("tachometer"),
             menuItem("Deployment Map", tabName = "deploymentMap", icon = icon("compass")),
             menuItem("Data", icon = icon("line-chart"),
                      #menuItem("Node Status", tabName = "status", icon = icon("signal")),
                      menuItem("Sensor Data", tabName = "data", icon = icon("line-chart")),
                      menuItem("System Data", tabName = "system", icon = icon("line-chart"))
                      ),
             menuItem("System Performance", icon = icon("laptop"),
                      menuItem("Data Yield", tabName = "dataYield", icon = icon("line-chart"))
                      #menuItem("Server Status", tabName = "pushYield", icon = icon("signal"))
                      ),
             menuItem("Deployment Log", tabName = "log", icon = icon("calendar")),
             menuItem("Download Data", tabName = "download", icon = icon("download"))
             ),
    menuItem("Project Document Repository", tabName = "documents", icon = icon("file"))
  )
)


body <- dashboardBody(
  tabItems(
    homeTab,
    projectTab,
    factoryTab,
    deploymentTab,
    teamTab,
    deploymentMapTab,
    statusTab,
    dataTab,
    systemTab,
    yieldTab,
    pushTab,
    logTab,
    downloadTab,
    documentTab
    )
)

dashboardPage(
  header,
  sidebar,
  body
)
