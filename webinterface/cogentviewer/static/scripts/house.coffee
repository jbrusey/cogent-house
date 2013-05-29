#Display and Deal with the New / Edit House Code

# Some Pretty Hideous convoluted code here
# Mostly due to handling callbacks.

require(["dijit/Dialog","dojo/date"])

createDlg = (nodeId) ->
    console.log("Creating Dialog")
    dlgTitle = "Register Node #{nodeId}"
    theDialog = new dijit.Dialog({
        title:dlgTitle
        nodeId:nodeId
        content:"Some Dialog Text can Go Here"
        })
    theDialog.onClose(dlgCallback)
    theDialog.show()

dlgCallback = () ->
    console.log("Callback")


dateNow = new Date()

dateFormatter = (dateStr) ->
  if dateStr
    theDate = dojo.date.stamp.fromISOString(dateStr)
    dateDiff = dojo.date.difference(theDate,dateNow,"hour")

    #console.log("The Date: ",theDate, " ",dateDiff)
    #theDate - dateNow
    formatDate =  dojo.date.locale.format(theDate,{format:"short"})
    #return formatDate
    if dateDiff > 24
        return "<div class='bad'>#{formatDate}"
    else if dateDiff > 1
        return "<div class='middle'>#{formatDate}"
    else
        return "<div class='good'>#{formatDate}"

    return formatDate
  else
    return null


batteryFormatter = (batteryLevel) ->
    #Formatter for battery levels
    #console.log(batteryLevel)

    if batteryLevel == null
        return ""

    if batteryLevel > 2.8
        return "<div class='good'>#{batteryLevel}</div>"
    else if batteryLevel > 2.4
        return "<div class='middle'>#{batteryLevel}</div>"
    else
        return "<div class='bad'>#{batteryLevel}</div>"

statusFormatter = (theStatus) ->
    if theStatus == "Good"
        return "<div class='good'>#{theStatus}</div>"
    else if theStatus == "Not Reporting"
        return "<div class='bad'>#{theStatus}</div>"
    else if theStatus == "Low Battery"
        return "<div class='middle'>#{theStatus}</div>"

    return theStatus



require(["dijit/form/Button"
        "dijit/form/FilteringSelect"
        "dijit/form/TextBox"
        "dijit/form/SimpleTextarea"
        "dijit/form/DateTextBox"
        "dijit/form/TimeTextBox"
        "dojo/data/ObjectStore"
        "dojo/store/Cache"
        "dojo/store/JsonRest"
        "dojo/store/Memory"
        "dojox/grid/DataGrid"
        "MyWidgets/form/DateTimeBox"
        "dojo/domReady!"]
        ,
        (Button,FilterSelect,TextBox,SimpleTextArea,DateTextBox,TimeTextBox,ObjectStore,Cache,jsonRest,Memory,DataGrid,DateTimeBox) ->

            #Load Deployment using JSON

            #deployStore = Cache(jsonRest({target:"rest/deployment/"}),Memory())
            deployStore = jsonRest({target:"../rest/deployment/"})

            #Populate our Select
            #At the moment we need to wrap as an object store
            deployDataStore = ObjectStore({objectStore:deployStore})

            depSelect = new FilterSelect({
                    id: "depSelect"
                    store:deployStore,
                    searchAttr: "name"
                    placeholder:"Select a deployment"
                    }
                "depName"
                )

            depSelect.startup()


            #Create Everything Programatiaccaly so I can fiddle with the values
            houseAdd = new TextBox({}
                "houseAdd"
                )

            stDate = new DateTextBox({}
                "stDate"
                )

            stTime = new TimeTextBox({}
                "stTime"
                )


            edDate = new DateTextBox({}
                "edDate"
                )

            edTime = new TimeTextBox({}
                "edTime"
                )

            saveBtn = new Button({
                    label:"Save"
                    onClick: -> processSave()
                    }
                "Save"
                )

            resetBtn = new Button({
                    label:"Reset"
                    onClick: -> processReset()
                    }
                "Reset"
                )

            houseStore = jsonRest({target:"../rest/house/"})
            if houseId
                #console.log("House Id: ",houseId)
                #houseStore.get(houseId).then((item) ->
                houseStore.query({id:houseId}).then((item) ->
                        #console.log(item)
                        theHouse = item[0]
                        houseAdd.setValue(theHouse.address)
                        #console.log(theHouse.startDate)
                        #console.log(theHouse.startDate.date)
                        stDate.setValue(theHouse.startDate)
                        edDate.setValue(theHouse.endDate)
                        stTime.setValue(theHouse.startDate)
                        edTime.setValue(theHouse.endDate)
                        #And try to get the deployment
                        deployStore.query({id:theHouse.deploymentId}).then((depItem) ->
                                console.log(depItem)
                                if depItem.length > 0
                                    depSelect.set("displayedValue",depItem[0].name)
                                )
                        )
            else
                console.log("No ID Supplied")
            #foo = dijit.byId("houseAdd")
            #foo.setValue("Foo")


            #Functions
            processSave = () ->
                #console.log("Save Pressed")
                #Get Values from the form
                theDeployment = depSelect.value
                theAddress = houseAdd.value
                startDate = stDate.value
                endDate = edDate.value
                startTime = stTime.value
                endTime = edTime.value


                if startDate is null or isNaN(startDate.valueOf())
                    startDate = null
                if endDate is null or isNaN(endDate.valueOf())
                    endDate = null

                if startTime is null or isNaN(startTime.valueOf())
                    startTime = null
                if endTime is null or isNaN(endTime.valueOf())
                    endTime = null

                #console.log("Start Date: ",startDate," Time: ",startTime)
                #Try combining
                if startDate and startTime
                    startDate.setHours(startTime.getHours())
                    startDate.setMinutes(startTime.getMinutes())

                if endDate and endTime
                    endDate.setHours(endTime.getHours())
                    endDate.setMinutes(endTime.getMinutes())

                #console.log("New Start Date ",startDate)
                #console.log("Deploymebnt ID: ",theDeployment)
                #Update the Existing House
                if houseId
                    houseStore.query({id:houseId}).then((item) ->
                        theHouse = item[0]
                        #console.log("Exisitng House: ",theHouse)
                        theHouse.deploymentId = theDeployment
                        theHouse.address = theAddress
                        theHouse.startDate = startDate
                        theHouse.endDate = endDate
                        houseStore.put(theHouse)
                    )
                else
                    theItem = {
                        "deploymentId":theDeployment
                        "address":theAddress
                        "startDate":startDate
                        "endDate":endDate
                        "__table__":"House"
                        }

                    out = houseStore.put(theItem).then((obj) ->
                        #console.log("OUT IS: ",obj.id)
                        #And Update our stred houseId
                        houseId = obj.id

                        window.location = "#{obj.id}"
                        return
                        )

                return

            processReset = () ->
                console.log("Reset Pressed")
                return


            return
        )


# ------------- DIALOGS to Register Nodes / Add Locations

#Display / Deal with Registered Nodes
require(["dijit/form/Button"
        "dijit/form/FilteringSelect"
        "dijit/form/ComboBox"
        "dijit/form/TextBox"
        "dijit/form/SimpleTextarea"
        "dijit/form/DateTextBox"
        "dijit/form/TimeTextBox"
        "dijit/form/CheckBox"
        "dojo/data/ObjectStore"
        "dojo/store/Cache"
        "dojo/store/JsonRest"
        "dojo/store/Memory"
        "dojox/grid/DataGrid"
        "dojo/store/Observable"
        "dojo/_base/Deferred"
        "dojo/io/script"
        "dijit/Dialog"
        "dojo/domReady!"]
        ,
        (Button,FilterSelect,ComboBox,TextBox,SimpleTextArea,DateTextBox,TimeTextBox,CheckBox,ObjectStore,Cache,jsonRest,Memory,DataGrid,Observable,Deferred,ioScript) ->

            #Open the Stores
            nodeStore = Cache(Observable(jsonRest({target:"../rest/node/"})),Memory())
            houseStore = Cache(Observable(jsonRest({target:"../rest/house/"})),Memory())
            roomStore = Cache(Observable(jsonRest({target:"../rest/room/"})),Memory())
            typeStore = Cache(Observable(jsonRest({target:"../rest/roomtype/"})),Memory())
            locationStore = Cache(Observable(jsonRest({target:"../rest/location/"})),Memory())

            #Sort out the Buttons Etc
            nodeSelect = new ComboBox({
                    id:"nodeSelect",
                    value:"",
                    store:nodeStore,
                    required:true
                    searchAttr:"id"}
                "regNodeId"
                )

            houseSelect = new FilterSelect({
                    id:"houseSelect"
                    value:""
                    store:houseStore
                    searchAttr:"address"}
                    "regNodeHouse"
                    )

            if houseId
                houseSelect.setDisabled(true)

            #roomSelect = new FilterSelect({
            roomSelect = new ComboBox({
                id:"roomSelect"
                value:""
                store:roomStore
                required:true
                storeAttr:"name"}
                "regNodeRoom"
                )


            #Checkbox
            updateTimes = new CheckBox({
                id:"updateTimes"
                }
                "updateTimes"
                )

            #And the Buttons
            regNodeBtn = new Button({label:"Register",onClick: -> regNode()},
                "dlg_regNode"
                )

            cancelNodeBtn = new Button({label:"Cancel",onClick: -> clearNode()},
                "dlg_regCancel"
                )


            clearNode = () ->
                theDlg = dijit.byId("regNodeDialog")
                nodeSelect.setDisabled(false)
                theDlg.reset()
                dijit.byId("regGrid").refresh()
                dijit.byId("statusGrid").refresh()
                theDlg.hide()

            regNode = () ->
                #Code to Actually Register a Node
                #Get the Parameters

                theNode = nodeSelect.value
                if houseId
                    #houseSelect.set("value",houseId)
                    theHouse = houseId
                else
                    theHouse = houseSelect.value

                theRoom = roomSelect.value

                console.log("N #{theNode} H #{theHouse} R #{theRoom}")


                #Quick bit of Validation
                #if (theNode=="" or theHouse=="" or theRoom=="")
                #    dijit.byId("regNodeDialog").validate()
                #    console.log("WARNING: Missing Data")
                #    return
                if not dijit.byId("regNodeDialog").validate()
                    return
                #
                #Otherwise start to sort out the Location
                roomStore.query({name:theRoom}).then((roomObj) ->
                   if roomObj.length == 0
                       #I was going to add a dialog, instead just create a new room name
                       theObj = {
                                "__table__":"Room",
                                name:theRoom
                                }
                       roomStore.add(theObj).then((roomId) ->
                           console.log("New Room Id ",roomId)
                           addLocation(roomId,theNode)
                           )
                       #roomNameSelect.setValue(theRoom)
                       #dijit.byId("newRoomDialog").show()

                   else
                       #Turn that into a location
                       addLocation(roomObj[0].id,theNode)
                   return
                   )

            addLocation = (theRoom,theNode) ->
               #Add a new location to the system, as there are a couple of corner cases here, we want to call in a seperate function
               console.log("Setting Up Location for: ",theRoom, " House ", houseId, "  Node: ",theNode)
               #We know the room Id and the Node Id

               #Look for an Existing Location
               locationStore.query({houseId:houseId,roomId:theRoom}).then((theLoc) ->
                   console.log("Returned Location: ",theLoc)
                   if theLoc.length > 0
                        updateNodeLocation(theLoc[0].id,theNode)
                   else
                        theObj = {
                                "__table__":"Location"
                                houseId:houseId
                                roomId:theRoom
                                }
                        locationStore.add(theObj).then((newLoc) ->
                                console.log("New Location ",newLoc)
                                updateNodeLocation(newLoc.id,theNode)
                                )

                   )
               return

            updateNodeLocation = (locationId,theNode) ->
                #Update a Nodes Location
                console.log("Updating Node #{theNode} to Location #{locationId}")
                nodeStore.query({id:theNode}).then((storeNode) ->
                        console.log("Returned Items from Node Store ",storeNode)
                        if storeNode.length > 0
                            storeNode = storeNode[0]
                            console.log("Node from Store ",storeNode)
                            storeNode.locationId = locationId
                            nodeStore.put(storeNode).then((obj) ->
                                updateTimestamps(locationId,theNode)
                                )
                        else
                            #Add a new node
                            theObj = {
                                "__table__":"Node"
                                id: theNode
                                locationId: locationId
                                }
                            console.log("Adding New Node ",theObj)
                            nodeStore.add(theObj).then((obj) ->
                                console.log(obj)
                                updateTimestamps(locationId,theNode)
                                )
                        )

             updateTimestamps = (locationId,theNode) ->
                #Update the Times if Checked
                console.log(updateTimes)
                chkValue = updateTimes
                if chkValue.checked
                    console.log("Times Need Updating")
                    ioScript.get({
                        url:"../sumRest/updateTimes/"
                        callbackParamName:"callback"
                        content:{
                            houseId:houseId
                            nodeId:theNode
                            locationId:locationId
                            }

                        })
                else
                    console.log("Leaving Times as Be")
                #console.log("Check Value ",chkValue)
                #clearNode()
                return

        )


#Grids



require(
    ["dojo/store/Cache"
     "dojo/store/JsonRest"
     "dojo/store/Memory"
     "dojo/store/Observable"
     "dgrid/OnDemandGrid"
     "dgrid/Keyboard"
     "dgrid/Selection"
     "dgrid/editor"
     "dgrid/selector"
     "dojo/_base/declare"
     "dijit/form/Button"
     "dgrid/extensions/DijitRegistry"
     "dijit/Dialog"
     "dijit/form/FilteringSelect"
     "dijit/form/ComboBox"
     "dojo/data/ObjectStore"
     "dgrid/tree"
     "dojo/domReady!"],
     (Cache,jsonRest,Memory,Observable,OnDemandGrid,Keyboard,Selection,editor,selector,declare,Button,DijitRegistry,Dialog,FilterSelect,ComboBox,ObjectStore,tree) ->
        registerStore = Cache(Observable(jsonRest({target:"../sumRest/register/"})),Memory())
        nodeStore = Cache(Observable(jsonRest({target:"../rest/node/"})),Memory())
        roomStore = Cache(Observable(jsonRest({target:"../rest/room/"})),Memory())
        locationStore = Cache(Observable(jsonRest({target:"../rest/location/"})),Memory())
        statusStore = Cache(Observable(jsonRest({target:"../sumRest/status/"})),Memory())

        #For Registered Nodes
        #roomObjStore = ObjectStore(objectstore:roomStore)

            #row = registerGrid.row(obj.id)
            #console.log("Row ",row)

        registerStore.getChildren = (object,options) ->
                #console.log("Fetching Children for ",object, "  ",options)
                theChildren = this.query({parent: object.id})
                #console.log("Children Are ",theChildren)
                return theChildren


        registerGrid = new declare([OnDemandGrid,Keyboard,Selection,DijitRegistry])({
            columns: [
                #{label:"Location Id",field:"id"}
                selector(selectorType:"checkbox",label:"Select")
                {label:"id",field:"id"}
                tree({label:"Room",field:"room"})
                {label:"Type",field:"type"}
                {label:"Node",field:"node"}
                {label:"Status",field:"status",formatter:statusFormatter}
                {label:"First Tx",field:"firstTx",formatter:dateFormatter}
                {label:"Last Tx",field:"lastTx",formatter:dateFormatter}
                {label:"Total Samples",field:"totalSamples"}

                #{label:"Last Tx",field:"lastTx",formatter:dateFormatter}
                #{label:"Voltage",field:"voltage",formatter:batteryFormatter}
                ]
            selectorType:"checkbox"
            store: registerStore
            #store:statusStore
            query:{houseId:houseId,summary:true}
            skin:"claro"
            #renderRow:testRow
            }
            "regGrid"
            )

        registerGrid.styleRow = (row) ->
            console.log("Styling Row ",row)

        if not houseId
            registerGrid.query.houseId = -1
            registerGrid.refresh()



            #Then Style the Row Itself
        #    row =

        regNode = new Button(
            {
                label:"Register New Node"
                onClick: -> registerNode()
            }
            "regNode"
            )

        unRegNode = new Button(
            {
                label:"Unregister Selected"
                onClick: -> unRegisterNode()
            }
            "unRegNode"
            )

        clearNode = new Button(
            {
                label:"Clear Selection"
                onClick: ->  registerGrid.refresh()
            }
            "clearNode"
            )

        updateNode = new Button(
            {
                label:"Update"
                onClick: ->  registerGrid.refresh()
            }
            "updateNode"
            )


        registerNode = () ->
            console.log("Register Button Pressed")
            dijit.byId("regNodeDialog").show()
            #regDataStore.revert()
            return

         unRegisterNode = () ->
            console.log("Unregister Button Pressed")
            selected = registerGrid.selection
            for id of selected
                row = registerGrid.row(id).data
                console.log("ID: ",id, " Row ",row, " Node: ",row.node)
                #And unregister these locations

                #row.locationId = null
                fetchItem = nodeStore.query({id:row.node})
                #console.log(fetchItem)
                fetchItem.then((obj) ->
                    console.log("Node from Store ",obj)
                    theNode = obj[0]
                    theNode.locationId = null
                    nodeStore.put(theNode).then((out) ->
                        #console.log("Updated Node ",out)
                        #registerGrid.store.revert()
                        registerGrid.refresh()
                        )
                    )

        statusGrid = new declare([OnDemandGrid,Keyboard,Selection,DijitRegistry])({
            columns: [
                #selector(selectorType:"checkbox",label:" ")
                #editor({"label":"Move Node",field:"newRoom",editorArgs:{store:roomStore,style:"width:150px"},editor:FilterSelect})
                #editor({label: "A CheckBox", field: "bool"}, "checkbox")
                editor({"label":"Move Node",field:"newRoom",editorArgs:{store:roomStore,style:'width:100px;'},editor:ComboBox})
                {label:"Node",field:"node"}
                {label:"Status",field:"status",formatter:statusFormatter}
                {label:"Current House",field:"currentHouse"}
                {label:"Current Room",field:"currentRoom"}
                {label:"Last Tx",field:"lastTx",formatter:dateFormatter}
                {label:"Voltage",field:"voltage",formatter:batteryFormatter}
                ]
            selectorType:"checkbox"
            store: statusStore
            query:{cutTime:30}
            }
            "statusGrid"
            )

        #Link up the Edit Function as it does not appear to be wholly sensible at the moment
        statusGrid.on("dgrid-datachange", (evt) ->
            console.log("Data changed: ",evt)
            #Update a Value
            evt.cell.row.data.houseId = houseId
            )

        statRegister = new Button(
            {label:"Register Selected"
            onClick : -> procRegister()
            }
            "statRegister"
            )

        statRefresh = new Button(
            {label:"Refresh"
            onClick: -> statusGrid.refresh()
            }
            "statRefresh"
            )

        procRegister = () ->
            statusGrid.save()

        return
    )


