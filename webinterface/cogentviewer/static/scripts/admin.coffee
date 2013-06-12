require(["dojo/date","dojo/date/locale"])

dateFormatter = (dateStr) ->
  console.log("Formatting Date ",dateStr)
  if dateStr
    theDate = dojo.date.stamp.fromISOString(dateStr)
    fmtDate = dojo.date.locale.format(theDate,{format:"short"})
    return fmtDate
  else
    return null

#Formatting Functions for the datagrid (The Grids themselves)
require([
    "dojo/store/JsonRest"
    "dojo/store/Cache"
    "dojo/store/Observable"
    "dojo/store/Memory"
    "dgrid/OnDemandGrid"
    "dgrid/Keyboard"
    "dgrid/Selection"
    "dgrid/editor"
    "dgrid/extensions/DijitRegistry"
    "dojo/_base/declare"
    "MyWidgets/form/DateTimeBox"
    "dijit/form/Button"
    "dijit/form/FilteringSelect"
    "dojo/ready"
    "dojo/on"
    "dijit/Dialog"
    "dijit/form/TextBox"
    "dijit/form/SimpleTextarea"
    "dojo/domReady!"
    ]
    (jsonRest,Cache,Observable,Memory,OnDemandGrid,Keyboard,Selection,editor,DijitRegistry,declare,DateTimeBox,Button,FilteringSelect,ready,On,Dialog,TextBox,SimpleTextarea) ->
        console.log("Starting Admin Interface")

        #Get the Stores Ready
        deployStore = Cache(Observable(jsonRest({target:"./rest/deployment/"})),Memory())

        houseStore = Cache(Observable(jsonRest({target:"./rest/house/"})),Memory())
        typeStore = Cache(Observable(jsonRest({target:"./rest/roomtype/"})),Memory())
        roomStore = Cache(Observable(jsonRest({target:"./rest/room/"})),Memory())

        #Then the Grids
        baseGrid = new declare([OnDemandGrid,Keyboard,Selection,DijitRegistry])

        deployGrid = baseGrid({
            columns:[
                {label:"Id",field:"id"}
                #{label:"Name",field:"name"}
                editor({label:"Name",field:"name",editor:"text",dismissOnEnter:false,editOn:"click"})
                editor({label:"Decription",field:"description",editor:"textarea",dismissOnEnter:false,editOn:"click"})
                editor({label:"Start Date",field:"startDate",editor:DateTimeBox})
                editor({label:"End Date",field:"endDate",editor:DateTimeBox})
                ]
            store:deployStore
            }
            "deployGrid"
            )

        houseGrid = baseGrid({
            columns:[
                {label:"Id",field:"id"}
                editor({label:"Address",field:"address",editor:"text",editOn:"click"})
                editor({label:"Deployment",field:"deploymentId",editor:FilteringSelect,editorArgs:{store:deployStore,style:"width:150px"}})
                editor({label:"Start Date",field:"startDate",editor:DateTextBox})
                editor({label:"End Date",field:"endDate",editor:DateTextBox})
                ]
            store:houseStore
            }
            "houseGrid"
            )

        roomGrid = baseGrid({
            columns:[
                {label:"Id",field:"id"}
                editor({label:"Name",field:"name",editor:"text",editOn:"click"})
                editor({label:"Type",field:"roomTypeId",editor:FilteringSelect,editorArgs:{store:typeStore}})
                ]
            store:roomStore
            }
            "roomGrid"
            )


        typeGrid = new declare([OnDemandGrid,Keyboard,Selection,DijitRegistry])({
            columns:[
                {label:"Id",field:"id"}
                editor({label:"name",field:"name",editOn:"click"})
                ]
            store:typeStore
            }
            "typeGrid"
            )


        deployGrid.startup()
        houseGrid.startup()
        roomGrid.startup()
        typeGrid.startup()


        # -------------------------- BUTTONS --------------------------
        #
        # --- DEPLOYMENT GRID
        deploySave = new Button({
            label:"Save Changes"
            onClick: -> deployGrid.save()
            }
            "deploySave"
            )

        deployReset = new Button({
            label:"Reset"
            onClick: -> deployGrid.revert()
            }
            "deployReset"
            )

        deployNew = new Button({
            label:"Add"
            onClick: -> dijit.byId("depDlg").show()
            }
            "deployNew"
            )

        deployReset = new Button({
            label:"Delete"
            onClick: ->
                if confirm("This Will Delete the Selected items")
                    selected = deployGrid.selection
                    console.log("Selected ",selected)
                    for id of selected
                        deployStore.remove(id)
                    return

                return
            }
            "deployDelete"
            )



        # --- HOUSES
        houseSave = new Button({
            label:"Save Changes"
            onClick: -> houseGrid.save()
            }
            "houseSave"
            )

        houseReset = new Button({
            label:"Reset"
            onClick: -> houseGrid.revert()
            }
            "houseReset"
            )

        houseNew = new Button({
            label:"Add"
            onClick: -> dijit.byId("houseDlg").show()
            }
            "houseNew"
            )

        houseDelete = new Button({
            label:"Delete"
            onClick: ->
                if confirm("This Will Delete the Selected items")
                    selected = houseGrid.selection
                    console.log("Selected ",selected)
                    for id of selected
                        houseStore.remove(id)
                    return

                return
            }
            "houseDelete"
            )
        # ------------ ROOM TYPES ---------------
        typeSave = new Button({
            label:"Save Changes"
            onClick: -> typeGrid.save()
            }
            "typeSave"
            )

        typeReset = new Button({
            label:"Reset"
            onClick: -> typeGrid.revert()
            }
            "typeReset"
            )

        typeNew = new Button({
            label:"Add"
            onClick: -> dijit.byId("typeDlg").show()
            }
            "typeNew"
            )



        # ----------------- ROOMS --------------------

        #Buttons for the Grid
        roomSave = new Button({
            label:"Save Changes"
            onClick: -> roomGrid.save()
            }
            "roomSave"
            )

        roomReset = new Button({
            label:"Reset"
            onClick: -> roomGrid.revert()
            }
            "roomReset"
            )

        roomNew = new Button({
            label:"Add"
            onClick: -> dijit.byId("roomDlg").show()
            }
            "roomNew"
            )


        roomDelete = new Button({
            label:"Delete"
            onClick: ->
                if confirm("This Will Delete the Selected items")
                    selected = roomGrid.selection
                    console.log("Selected ",selected)
                    for id of selected
                        roomStore.remove(id)
                    return

                return
            }
            "roomDelete"
            )


        #---------------------------
        #
        #        DIALOGS
        #
        # ----------------------------


        #         #New Deployment Dialog
        dep_name = new TextBox(
            {required:true}
            "dep_name"
            )
        dep_name.startup()

        dep_desc = new SimpleTextarea(
            {rows:4
            cols:40}
            "dep_desc"
            )
        dep_desc.startup()

        dep_startDate = new DateTimeBox(
            {}
            "dep_startDate"
            )
        dep_startDate.startup()

        dep_endDate = new DateTimeBox(
            {}
            "dep_endDate"
            )

        dep_endDate.startup()

        dep_ok = new Button(
            {label:"Save",
            onClick: -> procDep()
            }
            "dep_ok"
            )

        dep_cancel = new Button(
            {label:"Cancel"
            onClick: -> closeDlg("depDlg")
            }
            "dep_cancel"
            )


        procDep = () ->
            console.log("Processing")
            dlg = dijit.byId("depDlg")
            if not dlg.validate()
                return

            #Get the items
            theItem = {
                "__table__":"Deployment"
                name:dep_name.get("value")
                description: dep_desc.get("value")
                startDate:dep_startDate.get("value")
                endDate:dep_endDate.get("value")
                }

            if theItem.name == null
                return

            console.log(theItem)
            #Find the store and add it to it
            theStore = dijit.byId("deployGrid").store
            theStore.add(theItem)
            closeDlg("depDlg")

            #pass

        closeDlg = (theName) ->
            dlg = dijit.byId(theName)
            dlg.reset()
            dlg.hide()


        #And for the House
        houseAdd = new TextBox(
            {required:true}
            "house_add"
            )
        houseAdd.startup()

        houseDep = new FilteringSelect(
            {required:true
            store:deployStore
            }
            "house_dep"
            )

        houseStart = new DateTimeBox(
            {required:true}
            "house_startDate"
            )
        houseStart.startup()

        houseEnd = new DateTimeBox(
            {}
            "house_endDate"
            )
        houseEnd.startup()


        house_ok = new Button(
            {label:"Save",
            onClick: -> procHouse()
            }
            "house_ok"
            )

        house_cancel = new Button(
            {label:"Cancel"
            onClick: -> closeDlg("houseDlg")
            }
            "house_cancel"
            )


        procHouse = () ->
            console.log("Processing")
            dlg = dijit.byId("houseDlg")

            if not dlg.validate()
                return

            item = {
                "table":"__house__"
                address:houseAdd.get("value")
                deploymentId:houseDep.get("value")
                startDate:houseStart.get("value")
                endDate:houseEnd.get("value")
                }

            console.log(item)
            theStore = dijit.byId("houseGrid").store
            theStore.add(item)
            closeDlg("houseDlg")



        return
    )

