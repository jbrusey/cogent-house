#Display and Deal with the New / Edit House Code

# Some Pretty Hideous convoluted code here
# Mostly due to handling callbacks.

require(["dojo/date"])

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
        return "<div class='middle'>#{theStatus}</div>"
    else if theStatus == "No Data"
        return "<div class='bad'>#{theStatus}</div>"
    else if theStatus == "Low Battery"
        return "<div class='middle'>#{theStatus}</div>"

    return theStatus


# ------------- FOR THE DEPLOYMENT DETAILS --------------------

require(
    ["dijit/form/Button"
    "dijit/form/FilteringSelect"
    "dijit/form/TextBox"
    "dijit/form/SimpleTextarea"
    "dijit/form/DateTextBox"
    "dijit/form/TimeTextBox"
    "dojo/data/ObjectStore"
    "dojo/store/Cache"
    "dojo/store/JsonRest"
    "dojo/store/Memory"
    "dojo/domReady!"]
    ,
    (Button,FilterSelect,TextBox,SimpleTextArea,DateTextBox,TimeTextBox,ObjectStore,Cache,jsonRest,Memory) -> 

        #Load Deployment using JSON
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

        #--- Create Form Objects ---
        houseAdd = new TextBox({},"houseAdd")
        houseAdd.startup()
            
        stDate = new DateTextBox({},"stDate")
        stDate.startup()
    
        stTime = new TimeTextBox({},"stTime")
        stTime.startup()
            
        edDate = new DateTextBox({},"edDate")
        edDate.startup()
            
        edTime = new TimeTextBox({},"edTime")
        edTime.startup()
    
        saveBtn = new Button({
            label:"Save"
            onClick: -> processSave()
            }
            "Save"
            )
        saveBtn.startup()

        houseStore = jsonRest({target:"../rest/house/"})
        if houseId
            houseStore.query({id:houseId}).then((item) ->
                #console.log(item)
                theHouse = item[0]
                #houseAdd.setValue(theHouse.address)
                houseAdd.set("value",theHouse.address)
                stDate.set("value",theHouse.startDate)
                edDate.set("value",theHouse.endDate)
                stTime.set("value",theHouse.startDate)
                edTime.set("value",theHouse.endDate)
                #And try to get the deployment
                deployStore.query({id:theHouse.deploymentId}).then((depItem) ->
                    #console.log(depItem)
                    if depItem.length > 0
                        depSelect.set("displayedValue",depItem[0].name)
                    )
                )
        else
            console.log("No ID Supplied")

        # #Functions
        processSave = () ->
            #console.log("Save Pressed")
            #Get Values from the form
            theDeployment = depSelect.value
            theAddress = houseAdd.value
            startDate = stDate.value
            endDate = edDate.value
            startTime = stTime.value
            endTime = edTime.value

            console.log("The Deployment is ",theDeployment)
            if theDeployment is ""
                console.log("No such deployment")
                #Add this as a new deployment
                textValue = depSelect.get("displayedValue")
                theDeployment = {
                    "__table__": "deployment",
                    "name": textValue
                    }
                console.log(theDeployment)
                deployStore.put(theDeployment).then((obj) ->
                    console.log(obj)
                    theDeployment = obj.id
                    )
                    
            
            if startDate is null or isNaN(startDate.valueOf())
                startDate = null
            if endDate is null or isNaN(endDate.valueOf())
                endDate = null

            if startTime is null or isNaN(startTime.valueOf())
                startTime = null
            if endTime is null or isNaN(endTime.valueOf())
                endTime = null

            console.log("Start Date: ",startDate," Time: ",startTime)
            #Try combining
            if startDate and startTime
                startDate.setHours(startTime.getHours())
                startDate.setMinutes(startTime.getMinutes())

            if endDate and endTime
                endDate.setHours(endTime.getHours())
                endDate.setMinutes(endTime.getMinutes())

            console.log("New Start Date ",startDate)
            console.log("Deploymebnt ID: ",theDeployment)
            #Update the Existing House
            if houseId
                houseStore.query({id:houseId}).then((item) ->
                    theHouse = item[0]
                    console.log("Exisitng House: ",theHouse)
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

            return
        )
    
#Display / Deal with Registered Nodes
require([
    "dijit/form/Button"
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
    "dijit/registry"
    "dojo/parser"
    "dgrid/OnDemandGrid"
    "dgrid/Keyboard"
    "dgrid/Selection"
    "dgrid/editor"
    "dgrid/selector"
    "dojo/_base/declare"
    "dgrid/extensions/DijitRegistry"
    "dgrid/tree"
    "dojo/domReady!"],
    (Button,FilterSelect,ComboBox,TextBox,SimpleTextArea,DateTextBox,TimeTextBox,CheckBox,ObjectStore,Cache,jsonRest,Memory,DataGrid,Observable,Deferred,ioScript,Dialog,registry,parser,OnDemandGrid,Keyboard,Selection,editor,selector,declare,DijitRegistry,tree) ->

        #Open the Stores
        nodeStore = Cache(Observable(jsonRest({target:"../rest/node/"})),Memory())
        houseStore = Cache(Observable(jsonRest({target:"../rest/house/"})),Memory())
        roomStore = Cache(Observable(jsonRest({target:"../rest/room/"})),Memory())
        typeStore = Cache(Observable(jsonRest({target:"../rest/roomtype/"})),Memory())
        locationStore = Cache(Observable(jsonRest({target:"../rest/location/"})),Memory())
        registerStore = Cache(Observable(jsonRest({target:"../sumRest/register/"})),Memory())
        statusStore = Cache(Observable(jsonRest({target:"../sumRest/status/"})),Memory())

        # -------------- STUFF FOR GRIDS ---------------------
        #
        registerStore.getChildren = (object,options) ->
                console.log("Fetching Children for ",object, "  ",options)
                theChildren = this.query({parent: object.id})
                console.log("Children Are ",theChildren)
                return theChildren

        registerGrid = new declare([OnDemandGrid,Keyboard,Selection,DijitRegistry])({
            columns: [
                #{label:"Location Id",field:"id"}
                selector(selectorType:"checkbox",label:"Select")
                {label:"Node",field:"node"}
                #{label:"id",field:"id"}
                {label:"Room",field:"room"}
                #{label:"Type",field:"type"}
                {label:"Status",field:"status",formatter:statusFormatter}
                {label:"Voltage",field:"voltage",formatter:batteryFormatter}
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
            }
            "regGrid"
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


        
                
        # --------------- DIALOG Buttons etc --------------
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
            houseSelect.set("disabled",true)

        roomSelect = new ComboBox({
            id:"roomSelect"
            value:""
            store:roomStore
            required:true
            storeAttr:"name"}
            "regNodeRoom"
        )

        #And the Buttons
        regNodeBtn = new Button({label:"Register",onClick: -> regNodeDlg()},
            "dlg_regNode"
            )
        regNodeBtn.startup()

        cancelNodeBtn = new Button({label:"Cancel",onClick: -> clearNode()},
            "dlg_regCancel"
            )
        cancelNodeBtn.startup()

        clearNode = () ->
            theDlg = registry.byId("regDlg")
            nodeSelect.set("disabled",false)
            theDlg.reset()
            #dijit.byId("regGrid").refresh()
            #dijit.byId("statusGrid").refresh()
            theDlg.hide()
            registerGrid.refresh()
            

        #Checkbox
        updateTimes = new CheckBox({
            id:"updateTimes"
            }
            "updateTimes"
        )
        updateTimes.startup()


        #Controls to show Dialog

        theBtn = new Button({
            onClick: -> showDlg()},
            "regNodeGrd"
            )
        theBtn.startup()


        ##Dialog Buttons

        showDlg = () ->
            foo = registry.byId("regDlg")
            #console.log("Dlg ",foo)
            foo.show()
            return


        regNodeDlg = () ->
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

            theDlg = registry.byId("regDlg")
            if not theDlg.validate()
                console.log("WARNING: Missing Data")
                return
                #
            #Otherwise start to sort out the Location
            roomStore.query({name:theRoom}).then((roomObj) ->
                console.log("This Room",roomObj)

                if roomObj.length == 0
                    console.log("No Such Room")
                #     #I was going to add a dialog, instead just create a new room name
                    theObj = {
                        "__table__":"Room",
                        name:theRoom
                        }
                    roomStore.add(theObj).then((theRoom) ->
                        console.log("New Room Id ",theRoom)
                        addLocation(theRoom.id,theNode)
                    )
                else
                    #Turn that into a location
                    addLocation(roomObj[0].id,theNode)
                )
            return


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
                        console.log("Updated Store ",obj)
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
            return

        updateTimestamps = (locationId,theNode) ->
            #Update the Times if Checked
            console.log("Times Checkbox ",updateTimes)
            chkValue = dijit.byId("updateTimes").checked
            console.log("Check Value ",chkValue)
            if chkValue == true
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
                clearNode()
            else
                console.log("Leaving Times as Be")
                #console.log("Check Value ",chkValue)
                clearNode()
            return


        out = parser.parse()
        console.log("Parsed ",out)
        console.log("BAR")
        #return
    #)


# require(["dojo/store/Cache"
#     "dojo/store/JsonRest"
#     "dojo/store/Memory"
#     "dojo/store/Observable"
#     "dgrid/OnDemandGrid"
#     "dgrid/Keyboard"
#     "dgrid/Selection"
#     "dgrid/editor"
#     "dgrid/selector"
#     "dojo/_base/declare"
#     "dijit/form/Button"
#     "dgrid/extensions/DijitRegistry"
#     "dijit/form/FilteringSelect"
#     "dijit/form/ComboBox"
#     "dojo/data/ObjectStore"
#     "dgrid/tree"
#     "dojo/parser"
#     "dojo/domReady!"
#     ],
#     (Cache,jsonRest,Memory,Observable,OnDemandGrid,Keyboard,Selection,editor,selector,declare,Button,DijitRegistry,FilterSelect,ComboBox,ObjectStore,tree,parser) ->
#         console.log("foo")
        
#        registerStore = Cache(Observable(jsonRest({target:"../sumRest/register/"})),Memory())
#        nodeStore = Cache(Observable(jsonRest({target:"../rest/node/"})),Memory())
#        roomStore = Cache(Observable(jsonRest({target:"../rest/room/"})),Memory())
#        locationStore = Cache(Observable(jsonRest({target:"../rest/location/"})),Memory())
#        statusStore = Cache(Observable(jsonRest({target:"../sumRest/status/"})),Memory())

        # registerStore.getChildren = (object,options) ->
        #         console.log("Fetching Children for ",object, "  ",options)
        #         theChildren = this.query({parent: object.id})
        #         console.log("Children Are ",theChildren)
        #         return theChildren


        # registerGrid = new declare([OnDemandGrid,Keyboard,Selection,DijitRegistry])({
        #     columns: [
        #         {label:"Location Id",field:"id"}
        #         selector(selectorType:"checkbox",label:"Select")
        #         {label:"id",field:"id"}
        #         {label:"Room",field:"room"}
        #         {label:"Type",field:"type"}
        #         {label:"Node",field:"node"}
        #         {label:"Status",field:"status",formatter:statusFormatter}
        #         {label:"First Tx",field:"firstTx",formatter:dateFormatter}
        #         {label:"Last Tx",field:"lastTx",formatter:dateFormatter}
        #         {label:"Total Samples",field:"totalSamples"}

        #         {label:"Last Tx",field:"lastTx",formatter:dateFormatter}
        #         {label:"Voltage",field:"voltage",formatter:batteryFormatter}
        #         ]
        #     selectorType:"checkbox"
        #     store: registerStore
        #     store:statusStore
        #     query:{houseId:houseId,summary:true}
        #     skin:"claro"
        #     }
        #     "regGrid"
        #     )

        # registerGrid.styleRow = (row) ->
        #     console.log("Styling Row ",row)
        #     if not houseId
        #         registerGrid.query.houseId = -1
        #         registerGrid.refresh()
        #     return


        # regNodeGrd = new Button(
        #     {
        #         label:"Register New Node"
        #         onClick: -> registerNode()
        #     }
        #     "regNodeGrd"
        #     )



        #registerNode = () ->
        #    console.log("Register Button Pressed")
        #    dijit.byId("regNodeDialog").show()
        #    regDataStore.revert()
        #    return

        unRegisterNode = () ->
            console.log("Unregister Button Pressed")
            selected = registerGrid.selection
            for id of selected
                row = registerGrid.row(id).data
                console.log("ID: ",id, " Row ",row, " Node: ",row.node)
                ##And unregister these locations

                row.locationId = null
                fetchItem = nodeStore.query({id:row.node})
                console.log(fetchItem)
                fetchItem.then((obj) ->
                    console.log("Node from Store ",obj)
                    theNode = obj[0]
                    theNode.locationId = null
                    nodeStore.put(theNode).then((out) ->
                        console.log("Updated Node ",out)
                        #registerGrid.store.revert()
                        registerGrid.refresh()
                        )
                    )

        statusGrid = new declare([OnDemandGrid,Keyboard,Selection,DijitRegistry])({
            columns: [
                #selector(selectorType:"checkbox",label:" ")
                #editor({"label":"Move Node",field:"newRoom",editorArgs:{store:roomStore,style:"width:150px"},editor:FilterSelect})
                #editor({label: "A CheckBox", field: "bool"}, "checkbox")
                #editor({"label":"Move Node",field:"newRoom",editorArgs:{store:roomStore,style:'width:100px'},editor:ComboBox})
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
            Update a Value
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


        #parser.parse()
        return
    )


