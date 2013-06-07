#Formatting Functions for the datagrid
require(["dojo/date/stamp"
        "dojo/date/locale"
        "dijit/form/SimpleTextarea"
        "dijit/form/DateTextBox"
        "dijit/form/TextBox"])

#Format the Date In the Grid
dateFormatter = (dateStr) ->
  if dateStr
    theDate = dojo.date.stamp.fromISOString(dateStr)
    #console.log("The Date: ",theDate)
    dojo.date.locale.format(theDate,{format:"short"})
  else
    return null

#Helper Function to allow a Date Text Widget to be used for date input
getDateValue = () ->
  return dojo.date.stamp.toISOString(this.widget.get('value'))
  #value = this.widget.get('value')
  #console.log(this.value)
  #console.log("Fetch Date of ",value)



#Display the Grid Itself
require(["dojo/store/JsonRest"
        "dojox/grid/DataGrid"
        "dojo/data/ObjectStore"
        "dojo/store/Cache"
        "dojo/store/Observable"
        "dojo/store/Memory"
        "dijit/form/Button"
        "dijit/form/FilteringSelect"
        "dijit/Dialog"
        "dojox/grid/cells/dijit"
        "dojo/domReady!"],
        (jsonRest,dataGrid,ObjectStore,Cache,Observable,Memory,Button,FilteringSelect) ->

          # dateFormatter = (dateStr) ->
          #   if dateStr
          #      theDate = DateStamp.fromISOString(dateStr)
          #      console.log("The Date: ",theDate)
          #      Locale.format(theDate,{fromat:"short"})
          #   else
          #      return ""


          #Store to Deal with Deployments
          deployStore = Cache(Observable(jsonRest({target:"rest/deployment/"})),Memory())
          deployGrid = new dataGrid({
                store: deployDataStore = ObjectStore({objectStore:deployStore})
                structure: [
                        {name:"id",field:"id",width:"50px"}
                        {name:"name",field:"name",width:"100px",editable:true}
                        {name:"description",field:"description",width:"100px",editable:true}
                        {name:"startDate",field:"startDate",width:"150px",formatter:dateFormatter,editable:true,type:dojox.grid.cells.DateTextBox,getValue:getDateValue}
                        #{name:"startDate",field:"startDate",width:"150px",formatter:dateFormatter,editable:true,getValue:getDateValue}
                        {name:"endDate",field:"endDate",width:"150px",formatter:dateFormatter,editable:true,type:dojox.grid.cells.DateTextBox,getValue:getDateValue}
                        {name:"table",field:"table",widht:"100px"}
                        ]},
                "deployGrid"
                )
          deployGrid.startup()

          dojo.connect(deployGrid, 'onStyleRow', deployGrid, (row) ->
                item = deployGrid.getItem(row.index)
                if item.endDate is null
                    row.customStyles += "color:red;"

                deployGrid.focus.styleRow(row)
                deployGrid.edit.styleRow(row)
                #console.log(row)
                )


          #We want to link this to the deployment box
          houseDep = new FilteringSelect({
                id:"houseDepSelect",
                name:"deployment",
                value:"",
                store:deployDataStore,
                searchAttr: "name"}
            "houseDep"
            )

          houseDep.startup()

          #Add some Buttons to the Grid
          #newDep = new Button({label:"New",onClick: -> addDeployment()}
          newDep = new Button({label:"New",onClick: -> dijit.byId("depDialog").show()}
                "newDep"
                )

          saveDep = new Button({label:"Save",onClick: -> deployDataStore.save()}
                "saveDep"
                )

          # resetDep = new Button({label:"Reset",onClick: -> deployDataStore.revert()}
          #       "resetDep"
          #       )

          deleteDep = new Button({label:"Delete Selected",onClick: -> depDelete()}
                "deleteDep"
                )

          clearSelectDep = new Button({label:"Clear Selection",onClick : -> deployGrid.selection.clear()}
                "clearDep"
                )

          #Dialog Buttons for adding new deployments
          depAddBtn = new Button({label:"Add",onClick: -> addDeployment()},
                "dlg_addDep"
                )

          depClearBtn = new Button({label:"Cancel",onClick: -> clearDeployment()},
                "dlg_clearDep"
                )

          addDeployment = () ->
              console.log("Storing Deployment")
              theName = dijit.byId("depName").value
              theDesc = dijit.byId("depDesc").value
              startDate = dijit.byId("depStart").value
              endDate = dijit.byId("depEnd").value

              if theName == ""
                console.log("Name Must Be Supplied")
                return

              if startDate is null or isNaN(startDate.valueOf())
                startDate = null
              if endDate is null or isNaN(endDate.valueOf())
                endDate = null


              #console.log("Name: ",theName,"  Desc: ",theDesc," Start ",startDate,"  End ",endDate)
              theObj = {
                name:theName,
                description:theDesc
                startDate:startDate
                endDate:endDate
                table:"__Deployment__"
                }
              #console.log(theObj)
              deployStore.add(theObj)
              clearDeployment()

          clearDeployment = ()->
              #console.log("Clear Deployment")
              dlg = dijit.byId("depDialog")
              dlg.reset()
              dlg.hide()

          depDelete = () ->
              #console.log("Delete Deployments")
              #Get Selected Items
              items = deployGrid.selection.getSelected()
              for row in items
                  deployDataStore.deleteItem(row)

          # ------------------- DEAL WITH HOUSES ---------------------------------

          deployFormatter = (theItem) ->
              #console.log(theItem)
              #Get the Name
              theDep = deployStore.get(theItem)
              #console.log(theDep)
              return theDep.name


          #The Store Itself (Wrap in Cache / Observable)
          houseStore = Cache(Observable(jsonRest({target:"rest/house/"})),Memory())
          houseGrid = new dataGrid({
                store: houseDataStore = ObjectStore({objectStore:houseStore})
                structure: [
                        {name:"id",field:"id",width:"50px"}
                        {name:"address",field:"address",width:"200px",editable:"true"}
                        {name:"startDate",field:"startDate",width:"150px",formatter:dateFormatter,editable:true,type:dojox.grid.cells.DateTextBox,getValue:getDateValue}
                        {name:"endDate",field:"endDate",width:"150px",formatter:dateFormatter,editable:true,type:dojox.grid.cells.DateTextBox,getValue:getDateValue}
                        {name:"Deployment",field:"deploymentId",width:"100px",editable:true,type:dojox.grid.cells._Widget,widgetClass:dijit.form.FilteringSelect,widgetProps:{store:deployDataStore,searchAttr: "name"},formatter:deployFormatter}
                        #{name:"Deployment",field:"deploymentId",width:"100px",editable:true,formatter:deployFormatter}
                        ]
                        },
                "houseGrid"
                )
          houseGrid.startup()


          dojo.connect(houseGrid, 'onStyleRow', houseGrid, (row) ->
                item = houseGrid.getItem(row.index)
                if item.endDate is null
                    row.customStyles += "color:red;"
                if item.deploymentId is null
                    row.customStyles += "color:red;"

                houseGrid.focus.styleRow(row)
                houseGrid.edit.styleRow(row)
                #console.log(row)
                )

          newHouse = new Button({label:"Add",onClick: ->  dijit.byId("houseDialog").show() }
                "newHouse"
                )

          #Dialog Buttons for adding new Houses
          depHouseAddBtn = new Button({label:"Add",onClick: -> addHouse()},
                "dlg_addHouse"
                )

          depHouseClearBtn = new Button({label:"Cancel",onClick: -> clearHouse()},
                "dlg_clearHouse"
                )



          #Buttons Within the Dialog
          addHouse = () ->
              console.log("Add House")
              theAddress = dijit.byId("houseAdd").value
              #theDesc = dijit.byId("depDesc").value
              startDate = dijit.byId("houseStart").value
              endDate = dijit.byId("houseEnd").value
              deployId = dijit.byId("houseDepSelect").value
              console.log(deployId)

              if startDate is null or isNaN(startDate.valueOf())
                startDate = null
              if endDate is null or isNaN(endDate.valueOf())
                endDate = null
              if deployId is ""
                deployId = null

              theObj = {
                 address:theAddress,
                 startDate:startDate
                 endDate:endDate
                 deploymentId:deployId
                 table:"__House__"
                 }
              console.log(theObj)
              houseStore.add(theObj)
              clearHouse()


          clearHouse = ()->
              console.log("Clear Deployment")
              dlg = dijit.byId("houseDialog")
              dlg.reset()
              dlg.hide()


          #And A Button or Two to deal with changes
          houseButton = new Button({label:"Save",onClick: -> houseDataStore.save()}
                  "saveHouse"
                  )

          resetButton = new Button({label:"Reset",onClick: -> houseDataStore.revert()},
                "resetHouse"
                )


          deleteHouse = new Button({label:"Delete Selected",onClick: -> houseDelete()}
                "deleteHouse"
                )

          clearSelectHouse = new Button({label:"Clear Selection",onClick : -> houseGrid.selection.clear()}
                "clearHouse"
                )

          houseDelete = () ->
              #console.log("Delete Deployments")
              #Get Selected Items
              items = houseGrid.selection.getSelected()
              for row in items
                  houseDataStore.deleteItem(row)


          console.log("Script Loaded")
        )


#Sort the Register Node Combobox
require(["dojo/store/JsonRest",
         "dojo/store/Cache"
         "dojo/store/Observable"
         "dojo/store/Memory"
         "dijit/form/Button"
         "dijit/form/ComboBox"
         "dijit/form/FilteringSelect"
         "dijit/Dialog"],
         (jsonRest,Cache,Observable,Memory,Button,ComboBox,FilteringSelect) ->
            console.log("PRocessing Dialog")
            nodeStore = Cache(Observable(jsonRest({target:"rest/node/"})),Memory())
            houseStore = Cache(Observable(jsonRest({target:"rest/house/"})),Memory())
            roomStore = Cache(Observable(jsonRest({target:"rest/room/"})),Memory())
            typeStore = Cache(Observable(jsonRest({target:"rest/roomtype/"})),Memory())
            locationStore = Cache(Observable(jsonRest({target:"rest/location/"})),Memory())

            nodeSelect = new ComboBox({
                id:"nodeSelect",
                value:"",
                store:nodeStore,
                searchAttr:"id"}
                "regNodeId"
                )

            houseSelect = new FilteringSelect({
                id:"houseSelect"
                value:""
                store:houseStore
                searchAttr:"address"}
                "regNodeHouse"
                )

            roomSelect = new FilteringSelect({
                id:"roomSelect"
                value:""
                store:roomStore
                storeAttr:"name"}
                "regNodeRoom"
                )

            #And the Buttons
            regNodeBtn = new Button({label:"Register",onClick: -> regNode()},
                "dlg_regNode"
                )

            cancelNodeBtn = new Button({label:"Cancel",onClick: -> clearNode()},
                "dlg_regCancel"
                )

            newRoomBtn = new Button({label:"New Room", onClick: -> dijit.byId("roomDialog").show()}
                "dlg_regNewRoom"
                )


            regNode = () ->
                console.log("Registering Node")
                nodeId = nodeSelect.value
                houseId = houseSelect.value
                roomId = roomSelect.value
                if (nodeId=="" or houseId=="" or roomId=="")
                    dijit.byId("regDialog").validate()
                    console.log("WARNING: Missing Data")
                    return

                #Check for nodes
                node = nodeSelect.item
                #if node is null
                #    console.log("===== No Such Node Item =====")
                #    if nodeId
                #        console.log("Trying Node ID Trickery")
                #        nodeSelect.store.fetch({
                #        #theObj = nodeStore.query({id:nodeId}).then((obj) ->

                console.log("Node is: ",nodeId, " -> ",node)
                console.log("Checking for location ",houseId, " ",roomId)
                #Process Location
                locationStore.query({"houseId":houseId,"roomId":roomId}).then((obj) ->
                        console.log("Return ",obj)
                        if obj.length > 0
                            console.log("Location Exists", obj[0].id)
                            node.locationId = obj[0].id
                            console.log("The Node ",node)
                            nodeStore.put(node)
                            clearNode()
                        else
                            console.log("Adding New Location ",houseId, " ",roomId)
                            theObj = {
                                id:null
                                houseId : houseId
                                roomId:roomId
                                table:"__location__"
                                }

                            console.log("New Loc: ",theObj)

                            locationStore.put(theObj).then((theLocation) ->
                                console.log("Added Location")
                                console.log("New Location is", theLocation)

                                node.locationId = theLocation
                                nodeStore.put(node)
                                clearNode()
                                )
                            #console.log(newLoc)

                        )

            clearNode = () ->
                dlg = dijit.byId("regDialog")
                dlg.reset()
                dlg.hide()

            #---- Room Dialog

            roomNameSelect = new ComboBox({
                id:"roomNameSelect"
                value:""
                store:roomStore
                storeAttr:"name"}
                "newRoomRoom"
                )

            roomTypeSelect = new ComboBox({
                id:"roomTypeSelect",
                value:""
                store:typeStore
                storeAttr:"name"}
                "newRoomType"
                )

            roomOkBtn = new Button({label:"Add",onClick: -> addRoom()}
                "dlg_roomOk"
                )

            roomCancelButton = new Button({label:"Cancel",onClick: -> clearRoom()}
               "dlg_roomCancel"
               )


            addRoomType = () ->
                #Deferred functionality to add room type
                roomType = roomTypeSelect.item
                if roomType
                    console.log("Using Existing Room Type: ",roomType)
                    return addRoomName(roomType.id)
                else
                    theObj = {
                        id:null
                        name:roomTypeSelect.getValue(),
                        __table__:"RoomType"}
                    console.log("Add New Room Type:", theObj)
                    tempObj = typeStore.add(theObj).then((obj) -> return addRoomName(obj))



            addRoomName = (typeId) ->
                console.log("Dealing with room Name")
                console.log("Room Type Id: ",typeId)
                roomItem = roomNameSelect.item
                if roomItem
                    console.log("Using Existing Room Type: ",roomItem)
                    return
                else
                    theObj = {
                        id:null
                        name:roomNameSelect.getValue()
                        roomTypeId:typeId
                        __table__:"Room"
                        }
                    roomStore.add(theObj)


            addRoom = () ->
                addRoomType()
                clearRoom()



            clearRoom = () ->
                dlg = dijit.byId("roomDialog")
                dlg.reset()
                dlg.hide()


        )


setNodeId = (nodeId) ->
    console.log("Attempting to set node Id ",nodeId)
    dropDown = dijit.byId("nodeSelect")
    console.log("Dropdown is ",dropDown)
    #Fetch the value
    theStore = dropDown.store
    theStore.query({id:nodeId}).then((item) ->
        console.log("Query Items ",item[0])
        #dropDown.set('value',item[0])
        dropDown.set('value',item[0].id)
        dropDown.item = item[0]

        console.log("Done")
        )