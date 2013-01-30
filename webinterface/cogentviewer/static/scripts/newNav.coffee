#require(["dojo/store/Memory"])

#objData = null


# theData = []

require([
    "dojo/store/Memory"
    "dojo/store/JsonRest"
    "dojo/data/ObjectStore"
    "dijit/Tree"
    "dojo/domReady!"
    ]
    (Memory,JsonRest,ObjectStore,Tree) ->
      console.log("Loading Data")

      # memStore = new Memory({
      #  data: [
      #          {id:"A",label:"Root",children:[
      #            {id:"A1",label:"First"}
      #            {id:"A2",label:"Second"}
      #            ]}
      #        ]
      #        })

      memStore = new JsonRest({target:"jsonRest/"})

      console.log("Done")

      #Wrap as objectstore
      dataStore = new ObjectStore({objectStore:memStore})
      treeStore = new dijit.tree.TreeStoreModel({store:dataStore})

      theTree = new Tree({
        model:treeStore
        },
        "treeNode"
        )
      theTree.startup()
    )

#-------------- WORKING CODES --------------------------

#Sort out the Dropdowns
require([
  "dijit/form/Button"
  "dijit/form/DateTextBox"
  "dijit/form/FilteringSelect"
  "dojo/data/ItemFileReadStore"
  "dojo/domReady!"
  ],
  #(FilteringSelect,DateTextBox) ->
  (Button,DateTextBox,Select,ItemFileReadStore) ->

    getData = new Button({
      label:"Get Data",
      onClick: () ->
        console.log("Getting Data")
        showData()
      }
      "getData"
    )
    getData.startup()

    #And to Clear the Data
    clearData = new Button({
      label:"Clear",
      onClick: () ->
        dijit.byId("startDate").reset()
        dijit.byId("stopDate").reset()
        dijit.byId("sensorType").reset()
      }
      "clearData"
    )
    clearData.startup()

    startDate = new DateTextBox({
      name:"startDate"}
      "startDate"
      )
    startDate.startup()

    stopDate = new DateTextBox({
      name:"stopDate"}
      "stopDate"
    )
    stopDate.startup()

    #Store the the Filtering Select
    typeStore = new ItemFileReadStore({
      url: "jsonnav"
      })

    sensorType = new Select({
      name:"sensorType"
      store: typeStore
      query:{"type":"sensor"}
      }
      "sensorType"
      )

    sensorType.startup()

    ##Functions to process data
    showData = () ->
      console.log("Show Data Called")
      theTree = dijit.byId("treeNode")
      #console.log(theTree)
      treeItems = theTree.selectedItems
      outItems = JSON.stringify(x.id for x in treeItems)
      console.log(outItems)

      #Start Date
      startDate = dijit.byId("startDate").value
      stopDate = dijit.byId("stopDate").value
      sensorType = dijit.byId("sensorType").value
      typeDisp = dijit.byId("sensorType").getDisplayedValue()

      console.log("Sensor Type >#{sensorType}<")

      if sensorType == ""
       console.log(dijit.byId("sensorType"))
       if dijit.byId("sensorType").getDisplayedValue() == "Temperature"
         sensorType = 0

      console.log(sensorType)
      #Try Charting

      content = {
        startDate:startDate
        stopDate:stopDate
        sensorType:sensorType
        treeItems:outItems
      }

      console.log("Fetching Data")

      #We call the Fetch Data Class,  Hopefully this means we can just
      #Include a second script (for time series or exposure) and keep the
      # Nav stuff between pages.
      fetchData(content)

      console.log("Graphs Done")

  console.log("Init Functions Called")
  )



# plotTimeSeries = (theData) ->
#   console.log("Plotting Graph")
#   console.log(theData)
#   options = {
#     chart:
#       renderTo: "theGraph"
#       #spacingBottom: 40
#     title:
#       text: "DEFUALT"
#     yAxis:
#       title:
#         text: "DEFAULT"
#     legend:
#       enabled: true
#       align: "right"
#       layout:"vertical"
#       verticalAlign: "top"
#       #y: 35
#     credits:
#       enabled: false
#     xAxis:
#       title:
#         text: "Time"
#     series : [{
#       name:"Series"
#       data:[[1,1],[2,2]]
#       }]
#   }

#   options.title.text = theData.title
#   options.yAxis.title.text = theData.yAxis
#   options.series = theData.series
#   chart = new Highcharts.StockChart(options)