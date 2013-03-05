#For JSONP
dojo.require("dojo.io.script")
#dojo.require("dojox.data.StoreExplorer")
dojo.require("dojo.store.Memory")
dojo.require("dojo.parser")
dojo.require("dojo.data.ObjectStore")
dojo.require("dijit.Tree")
dojo.require("dojo.store.Observable")
dojo.require("dijit.form.Select")
dojo.require("dijit.form.FilteringSelect")
dojo.require("dijit.form.DateTextBox")
dojo.require("dojox.form.CheckedMultiSelect")

#The Object Store model is Dojo 1.8  We have grabbed it from SVN
#dojo.require("dijit.tree.ObjectStoreModel")

newData = []

Sort out the Dropdowns


dojo.xhrGet({
  url:"jsonnav"
  handleAs:"json"
  sync: true
  load: (jsonData) ->
    console.log("IO COMPLETE")
    newData = jsonData
    console.log(jsonData)
  })


# console.log("Creating Store")
# #Map to a new style Memory Store
# treeData= new dojo.store.Memory({
#     #data:theData,
#     data:newData.nav
#     getChildren: (object) ->
#       return this.get(object).children
#     getRoot: (object) ->
#       return this.get("root")
#   })

objData = new dojo.store.Memory({
    data:newData.list
    })


objData.getRoot = (onItem,onError) ->
  console.log("Get Root Called")
  root =  this.get("root")
  onItem(root)

objData.getChildren = (object,onComplete,onError) ->
  children = this.query({parent:object.id})
  onComplete(children)

#objData.getChildren = (object) ->
#  return this.query({parent:object.id})

objData.mayHaveChildren = (object) ->
  children = "children" in object
  return object.children

objData.getLabel = (object) ->
  return object.name


#Try defining a composite Query
objData.filterTemp = (object) ->
  if not object.sensorTypeId
    return true
  return object.sensorTypeId == 0




#treeData = new dojo.store.Observable(treeData)
objOData = new dojo.store.Observable(objData)
objStore = new dojo.data.ObjectStore({objectStore: objOData})


#Then Use the adapter to convert this to the Object Store that is required
#treeStore = new dojo.data.ObjectStore({objectStore: treeData}) #Comment to allow JSON

#treeModel = new dijit.tree.ForestStoreModel({store:treeStore,rootLabel:"houses"})
#treeStore = new dijit.tree.ObjectStoreModel({store:objOData,query:{name:"root"}})


dojo.addOnLoad  ->
	tree = new dijit.Tree(
    {
    #model: treeStore
    model: objOData
    showRoot: false
    },
    'treeNode')
	tree.startup()



#And the Select dropdowns
dojo.addOnLoad ->
  #For the House
  # houseSelect = new dijit.form.FilteringSelect(
  #   {name:"houseSelect",
  #   placeholder:"Select a Deployment"
  #   store:objStore,
  #   query:{"type":"house"}
  #   onChange: (type) ->
  #     updateSelects()
  #   },
  #   "houseSelect")
  # houseSelect.startup()

  # #For the Node
  # nodeSelect = new dijit.form.FilteringSelect(
  #   {name:"nodeSelect",
  #   store:objStore,
  #   placeHolder:"Select a Node"
  #   query:{"type":"node"}
  #   onChange: (type) ->
  #     updateSelects()
  #   },
  #   "nodeSelect")
  # nodeSelect.startup()

  # sensorSelect = new dijit.form.FilteringSelect(
  #   {name:"sensorSelect",
  #   store:objStore,
  #   placeHolder:"Select a Sensor"
  #   query:{"type":"sensor"}
  #   },
  #   "sensorSelect")
  # sensorSelect.startup()


  sensorType = new dijit.form.FilteringSelect(
    {name:"sensorType",
    store:objStore,
    placeHolder:"(Optional) Sensor Type",
    query:{"type":"sensorType"},
    #onChange: (type) ->
    #  updateSelects()
    },
    "sensorType")
  sensorType.startup()

  # startDate = new dijit.form.DateTextBox(
  #   {name:"startDate"
  #   }
  #   "startDate"
  #   )
  # startDate.startup()

  # stopDate = new dijit.form.DateTextBox(
  #   {name:"stopDate"
  #   }
  #   "stopDate"
  #   )
  # stopDate.startup()

  dropFetch = new dijit.form.Button({
    showLabel: true
    label: "Get Data"
    onClick: () ->
      console.log("Drop Button Pressed")
      processDropFetch()
    }
    "dropFetch"
    )

  dropFetch.startup()

  startDateTree = new dijit.form.DateTextBox(
    {name:"startDateTree"
    }
    "startDateTree"
    )

  stopDateTree = new dijit.form.DateTextBox(
    {name:"stopDateTree"
    }
    "stopDateTree"
    )

  treeFetch = new dijit.form.Button({
    showLabel: true
    label: "Get Tree Data"
    onClick: () ->
      console.log("Tree Button Pressed")
      processTreeFetch()
    }
    "treeFetch"
    )

  treeFetch.startup()

  dropClear = new dijit.form.Button({
    showLabel: true
    label: "reset"
    onClick: () ->
      #dijit.byId("houseSelect").reset()
      #dijit.byId("nodeSelect").reset()
      #dijit.byId("sensorSelect").reset()
      dijit.byId("startDateTree").reset()
      dijit.byId("stopDateTree").reset()
      dijit.byId("sensorType").reset()
    }
    "dropClear"
    )


updateSelects = () ->
   #Update all of our selected values
  console.log("Update Selects")


  houseSelect = dijit.byId("houseSelect")
  nodeSelect = dijit.byId("nodeSelect")
  sensorSelect = dijit.byId("sensorSelect")
  #sensorType = dijit.byId("sensorType")

  console.log("House Displayed #{houseSelect.displayedValue} Value #{houseSelect.value}")
  console.log("Node Displayed #{nodeSelect.displayedValue} Value #{nodeSelect.value}")
  console.log("Sensor Displayed #{sensorSelect.displayedValue} Value #{sensorSelect.value}")
  #console.log("Sensor Displayed #{sensorType.displayedValue} Value #{sensorType.value}")

  houseValue = houseSelect.value
  nodeValue = nodeSelect.value
  sensorValue = sensorSelect.value
  #sensorTypeValue = sensorType.value

  if houseValue == -1
    houseValue = "*"
  if nodeValue == -2
    nodeValue = "*"
  if sensorValue == -3
    sensorValue = "*"
  #if sensorTypeValue == -4
  #  sensorTypeValue = null

  #Then update the relevant querys
  nodeSelect.query = {type:"node",parent:houseValue}
  sensorSelect.query = {type:"sensor",parent:nodeValue}
  #nodeSelect.startup()


processDropFetch = () ->
  houseSelect = dijit.byId("houseSelect")
  nodeSelect = dijit.byId("nodeSelect")
  sensorSelect = dijit.byId("sensorSelect")
  console.log("House Displayed #{houseSelect.displayedValue} Value #{houseSelect.value}")
  console.log("Node Displayed #{nodeSelect.displayedValue} Value #{nodeSelect.value}")
  console.log("Sensor Displayed #{sensorSelect.displayedValue} Value #{sensorSelect.value}")

  startDate = dijit.byId("startDateTree").value
  stopDate = dijit.byId("stopDateTree").value

  console.log(startDate)
  #Convert these to Javascript dates
  if startDate
    startTime = startDate.getTime()/1000.0
  if stopDate
    stopTime = stopDate.getTime()/1000.0

  #Fetch the data
  console.log("Fetching Data")
  dojo.io.script.get({
    url:"http://127.0.0.1:6543/jsonFetch",
    content:{
      type:"drop",
      houseId:houseSelect.value,
      nodeId:nodeSelect.value,
      sensorId:sensorSelect.value,
      startTime:startTime
      stopTime:stopTime}
    callbackParamName: "callback",
    load: (jsonData) ->
      graphData(jsonData)
  })
  console.log("Done")

processTreeFetch = () ->

  theTree = dijit.byId("treeNode")
  treeItems = theTree.selectedItems
  #console.log("Tree Selected Items are")

  startDate = dijit.byId("startDateTree")
  stopDate = dijit.byId("stopDateTree")

  #Convert these to Javascript dates
  if startDate.value
    startTime = startDate.value.getTime()/1000
  if stopDate.value
    stopTime = stopDate.value.getTime()/1000

  sensorTypeValue = -1
  sensorType = dijit.byId("sensorType")
  if sensorType.displayedValue == "Temperature"
    sensorTypeValue = 0
  else
    sensorTypeValue = sensorType.value
  console.log("Sensor Type ")
  console.log(sensorTypeValue)
  console.log("-----")

  treeList = []
  console.log("---- Tree Loop----")
  for item in treeItems
    console.log(item)
    if item.type == "deployment"
      console.log("Deployment Selected")
      tempItem = {deploymentId: item.id}

    if item.type == "house"
      console.log("House Selected")
      tempItem = {deploymentId:item.parent,houseId:item.id}

    if item.type == "location"
      console.log("Location Selected")
      tempItem = {locationId:item.id}


    if item.type == "node"
      console.log("Node Selected")
      tempItem = {nodeId:item.id,location:item.location}

    if item.type == "sensor"
      console.log("Sensor Selected")
      tempItem = {sensorId:item.id,location:item.location}

    treeList.push(tempItem)
    console.log(tempItem)

  console.log("--- EOL ----")
  console.log(treeList)
  dojo.io.script.get({
    url:"http://127.0.0.1:6543/jsonFetch",
    content:{
      type:"tree",
      #houseId:houseSelect.value,
      #nodeId:nodeSelect.value,
      #sensorId:sensorSelect.value,
      sensorType:sensorTypeValue
      treeItems:dojo.toJson(treeList)
      startTime:startTime
      stopTime:stopTime}
    callbackParamName: "callback",
    load: (jsonData) ->
      console.log("~~~~~~~~~~~")
      console.log(jsonData)
      console.log("~~~~~~~~~~~")
      graphData(jsonData)
  })
  console.log("Done")




#dojo.addOnLoad ->
#  graphData(null)


graphData = (jsonData) ->
  #Turn an array of objects into a graph

  console.log("Graphing")
  console.log(jsonData)
  options = {
    chart:
      renderTo: "theGraph"
      spacingBottom: 40
    title:
      text: "Time Series Data"
    yAxis:
      title:
        text: "Default Y Title"
    legend:
      enabled: true
      verticalAlign: "bottom"
      y: 35
    credits:
      enabled: false
    xAxis:
      title:
        text: "Time"
    series : [{
      name:"Series"
      data:[[1,1],[2,2]]
      }]
  }

  # #Update the Title
  options.title.text = jsonData.title

  # #Update the series
  options.series = jsonData.series

  options.yAxis.title.text = jsonData.yText

  # console.log(options)
  chart = Highcharts.StockChart(options)
  console.log("Done")