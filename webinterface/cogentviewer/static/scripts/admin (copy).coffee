dojo.require("dojo.store.Memory")
dojo.require("dojo.store.Observable")
dojo.require("dijit.Tree")
dojo.require("dijit.tree.ObjectStoreModel")

#dojo.require('dojo.connect')

dojo.require("dijit.form.Button")
dojo.require("dijit.form.TextBox")
dojo.require("dijit.form.DateTextBox")
dojo.require("dijit.form.TimeTextBox")
dojo.require("dijit.form.FilteringSelect")
dojo.require("dijit.form.CheckBox")
dojo.require("dijit.Dialog")
dojo.require("dojo.date")

dojo.require("dojo.io.script")

#We can put a link to the global Objdata Object here for testing
objData = null
tempId = 0

dojo.addOnLoad  ->
  buildTree()
  buildButtons()
  newHouse()
  roomDialog()


buildTree = () ->

  newData = []

  dojo.xhrGet({
    url:"jsonnav"
    handleAs:"json"
    sync: true
    load: (jsonData) ->
      newData = jsonData
    })

  #And put it in a memory Store
  objData = new dojo.store.Memory({
      data:newData.list
      })

  objData.getChildren = (object) ->
    return this.query({parent:object.id})

  #Make the Store Observeable
  objData = new dojo.store.Observable(objData)
  treeModel = new dijit.tree.ObjectStoreModel({store:objData,query:{id:"root"}})

  tree = new dijit.Tree(
    {
    model:treeModel
    showRoot: false
    onDblClick: (item) ->
      treeEvent(item)
    },
    'treeNode')

  tree.startup()

buildButtons = () ->
  #And the Button Bar
  #console.log("Adding Buttons")

  addBtn = new dijit.form.Button(
    {
    label:"New House"
    showLabel: true
    onClick: () ->
      console.log("Add Pressed")
      #Two way Dialog Required
      dijit.byId("newDialog").show()
    }
    "addBtn"
  )

  remBtn = new dijit.form.Button(
    {
    label:"Remove Item"
    onClick: () ->
      console.log("Rem Pressed")
    }
    "remBtn"
    )

  addRoom = new dijit.form.Button(
    {
    label:"Add Room"
    onClick: () ->
      console.log("Add Room Pressed")
      #Select the Deployment
      tree = dijit.byId("treeNode")
      selected = tree.selectedItem

      console.log(selected)
      if selected
        dropdown = dijit.byId("room_depId")
        if selected.type == "house"
          dropdown.set("value",selected.id)
        if selected.type == "node"
          dropdown.set("value",selected.houseId)
        if selected.type == "sensor"
          #Get the node
          node = objData.get(selected.parent)
          dropdown.set("value",node.houseId)


      dijit.byId("roomDialog").show()
    }
    "addRoom"
  )

#Functionality for the Add/Edit house Dialog
newHouse = () ->

  newId = new dijit.form.TextBox({disabled:"disabled"},"newId")
  address = new dijit.form.TextBox({},"newAddress")
  startDate = new dijit.form.DateTextBox({},"newStart")
  startTime = new dijit.form.TimeTextBox({},"newStartTime")
  endDate = new dijit.form.DateTextBox({},"newEnd")
  endTime = new dijit.form.TimeTextBox({},"newEndTime")
  assNodes = new dijit.form.CheckBox({},"assNodes")

  submit = new dijit.form.Button({
    label:"Submit"
    onClick: () ->
      addNewHouse()
      #resetNewHouse()
    }
    "newSubmit")

  cancel = new dijit.form.Button({
    label:"Cancel"
    onClick: () ->
      resetNewHouse()
    }
    "newCancel")




#Process the Room Dialog
roomDialog = () ->
  #deployment = new dijit.form.TextBox({},"room_depId")

  deployment = new dijit.form.FilteringSelect(
    {name:"room_depId"
    store:objData
    query:{"type":"house"}
    placeHolder:"Select Deployment"
    onChange: (item) ->
      console.log(item)
    }
    "room_depId")
  deployment.startup()

  name = new dijit.form.TextBox({},"room_name")
  #type = new dijit.form.TextBox({},"room_type")

  type = new dijit.form.FilteringSelect(
    {name:"room_type"
    store:objData
    query:{"type":"roomType"}
    onChange: (item) ->
      console.log(item)
    }
    "room_type")


  # sensorSelect = new dijit.form.FilteringSelect(
  #   {name:"sensorSelect",
  #   store:objStore,
  #   placeHolder:"Select a Sensor"
  #   query:{"type":"sensor"}
  #   },
  #   "sensorSelect")
  # sensorSelect.startup()


  submit = new dijit.form.Button({
    label:"Update Rooms"
    onClick: () ->
      console.log("Room Submitted")
    }
    "roomSubmit"
    )

  cancel = new dijit.form.Button({
    label:"Cancel"
    onClick: () ->
      console.log("Room Cancelled")
      clearRoom()
    }
    "roomCancel")

clearRoom = () ->
  dijit.byId("room_depId").reset()
  dijit.byId("room_name").reset()
  dijit.byId("room_type").reset()
  dijit.byId("roomDialog").hide()

#What to do if someone double clicks on the tree
treeEvent = (item) ->
  console.log("Tree Event")
  if item.type == "house"
    console.log(item)

    dijit.byId("newId").set("value",item.id)
    dijit.byId("newAddress").set("value",item.name)
    dijit.byId("newStart").set("value",item.start)
    dijit.byId("newStartTime").set("value",item.start)
    dijit.byId("newEnd").set("value",item.end)
    dijit.byId("newEndTime").set("value",item.end)
    dijit.byId("newDialog").show()

  else
    console.log("Not of House Class")

#Process the new house if button is pressed
addNewHouse = () ->
  id = dijit.byId("newId").value
  address = dijit.byId("newAddress").value
  startDate = dijit.byId("newStart").value
  startTime = dijit.byId("newStartTime").value
  endDate = dijit.byId("newEnd").value
  endTime = dijit.byId("newEndTime").value

  unixStart = 0
  unixEnd = 0
  jsStart = null
  jsEnd = null

  console.log("===")
  console.log(id)
  console.log(startDate)
  console.log("===")

  if startDate != null
    if startDate.getTime()
      jsStart = startDate

      unixStart = startDate.getTime()
      if startTime != null

        if startTime.getTime()

          jsStart.setHours(startTime.getHours())
          jsStart.setMinutes(startTime.getMinutes())
          unixStart = unixStart + startTime.getTime()

      jsStart = jsStart.toJSON()

  if endDate!= null
    if endDate.getTime()

      jsEnd = endDate
      unixEnd = endDate.getTime()
      if endTime != null
        if endTime.getTime()

          unixEnd = unixEnd + endTime.getTime()
          jsEnd.setHours(endTime.getHours())
          jsEnd.setMinutes(endTime.getMinutes())

    #jsEnd = Date(unixEnd)

  console.log("Address #{address}")
  console.log("Start #{startDate} #{startTime} =  #{unixStart}")
  console.log("End #{endDate} #{endTime} = #{unixEnd}")
  console.log("#{jsStart} - #{jsEnd}")



  if not id
    tId = "T_#{tempId}"
    id = tId
    tempId += 1
    tempItem = {
      id: tId
      label:address
      name:address
      start:jsStart
      end:jsEnd
      parent:"root"
      type:"house"
      }

    #objData.add(tempItem)

  else
    tempItem = objData.get(id)

    tempItem.address = address
    tempItem.label = address
    tempItem.name = address
    tempItem.start = jsStart
    tempItem.end = jsEnd
    #objData.put(tempItem) #Update the Tree
    #objData.remove(id)
    #objData.add(tempItem)
    #console.log(tempItem)

  console.log("---- NEW ----")
  console.log(tempItem)
  console.log("-------------")

  resetNewHouse()
  #And Clear Everything Down
  #dijit.byId("id").reset()
  #dijit.byId("newAddress").reset()
  #dijit.byId("newStart").reset()
  #dijit.byId("newEnd").reset()
  #dijit.byId("newStartTime").reset()
  #dijit.byId("newEndTime").reset()
  #dijit.byId("newDialog").hide()

  #Transmit the Data to the Sink
  dojo.io.script.get({
     url:"modTree"
     content:{
       id:id
       address:address
       unixStart: unixStart
       unixEnd: unixEnd
       jsStart: jsStart#.toJSON()
       jsEnd: jsEnd#.toJSON()
       }
     callbackParamName: "callback",
     load: (jsonData) ->
       console.log("Returned Value")
       updateHouse(jsonData)
       #console.log(jsonData)
   })

#Reset the Fields on the House Dialog
resetNewHouse = () ->
  dijit.byId("newId").reset()
  dijit.byId("newAddress").reset()
  dijit.byId("newStart").reset()
  dijit.byId("newEnd").reset()
  dijit.byId("newStartTime").reset()
  dijit.byId("newEndTime").reset()
  dijit.byId("newDialog").hide()




#Callback function when we get an item fed back from the DB
updateHouse = (jsonData) ->
  console.log("Returned Object")
  console.log(jsonData)
  #Get the New Object
  #thisObject = objData.get(jsonData.oldId)
  #objData.remove(jsonData.oldId)
  #console.log("Tree Item")
  #console.log(thisObject)
  objData.put(jsonData.update)


