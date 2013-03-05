# Function to fetch and plot time series data
#


require([
    "dgrid/OnDemandGrid"
    "dgrid/tree"
    "dojo/store/JsonRest"
    "dgrid/extensions/DijitRegistry"
    "dojo/_base/declare"
    "dijit/tree/ObjectStoreModel"
    "dijit/Tree"
    "dojo/domReady!"
    ],
    (Grid,tree,JsonRest,DijitRegistry,Declare,ObjectStoreModel,Tree) ->
        console.log("Starting Tree Grid")

        treeStore = JsonRest({
            target: "rest/deploymenttree/",
            getChildren: (object,options) ->
                #console.log("Fetching Children for ",object, "  ",options)
                if object.type == "house"
                    #console.log("-----> HOUSE")
                    return []
                theChildren = this.query({parent: object.id})
                #console.log("Children Are ",theChildren)
                return theChildren
        })

        #return
        theModel = new ObjectStoreModel({
            store:treeStore
            #query:{id:"root"}
            })

        theTree = new Tree({
            model:theModel
            #persist:false
            }
            "treeNode"
            )

        theTree.getIconClass = (item,opened) ->
            #console.log("Get Icon for ",item)
            if item.id == "root"
                if opened
                    return "dijitFolderOpened"
                else
                    return "dijitFolderClosed"
                #return ""
            else if item.type == "deployment"
                return "deployIcon"
            else if item.type == "house"
                #console.log("Item is House")
                return "houseDarkIcon"
            else if item.type == "location"
                return "locDarkIcon"

            return "dijitLeaf"

        theTree.startup()

        return
    )


require([
  "dijit/form/Button"
  "dijit/form/DateTextBox"
  "dijit/form/FilteringSelect"
  "dojo/store/Cache"
  "dojo/store/JsonRest"
  "dojo/store/Observable"
  "dojo/store/Memory"
  "dojo/ready"
  "dojo/topic"
  "dijit/form/RadioButton"
  "dojo/io-query"
  "dojo/domReady!"
  ],
  #(FilteringSelect,DateTextBox) ->
  (Button,DateTextBox,Select,Cache,JsonRest,Observable,Memory,ready,topic,RadioButton,ioQuery) ->
    #And the Form

    typeStore = Cache(Observable(JsonRest({target:"./rest/sensortype/"})),Memory())

    #Form Elements
    startDateSelect = new DateTextBox({
      name:"startDate"}
      "startDate"
      )
    startDateSelect.startup()

    stopDateSelect = new DateTextBox({
      name:"stopDate"}
      "stopDate"
    )
    stopDateSelect.startup()

    #Buttons
    hourSelect = new RadioButton({}
        "hourlyRad"
        )

    dailySelect = new RadioButton({
        checked:true}
        "dailyRad"
        )


    getData = new Button({
      label:"Get Data",
      onClick: () ->
        #console.log("Getting Data")
        showData()
      }
      "getData"
    )
    getData.startup()


    #And to Clear the Data
    clearData = new Button({
      label:"Clear",
      onClick: () ->
        startDateSelect.reset()
        stopDateSelect.reset()
        sensorTypeSelect.reset()
        #dijit.byId("treeNode").reset()
      }
      "clearData"
    )
    clearData.startup()


    downloadBtn = new Button({
        label:"Download",
        onClick:() ->
            #downloadData()
            showData(true)
        }
        "download"
    )


    ##Functions to process data
    showData = (download=false) ->
        #console.log("Show Data Called")
        theTree = dijit.byId("treeNode")
        #console.log("Tree :",theTree)
        treeItems = theTree.selectedItems
      # outItems = JSON.stringify(x.id for x in treeItems)
        #console.log("Selected: ",treeItems)

        selectedItems = {
            "deployments":[],
            "houses":[],
            "locations":[]
            "locType": []
            }

        for item in treeItems
            if item.id == "root"
                #console.log("Root Item selected, Stopping this madness")
                return
            else
                theId = item.id
                #console.log(theId)
                splitItem = theId.split("_")
                #splitItem = item.id.split("_")
                console.log("Processing item ",item,"  Splits to ",splitItem)
                if splitItem[0] == "d"
                    selectedItems.deployments.push(splitItem[1])
                else if splitItem[0] == "h"
                    selectedItems.houses.push(splitItem[1])

        selStart = startDateSelect.get("value")
        selEnd = stopDateSelect.get("value")
        #selSensor = sensorTypeSelect.get("value")

        selectedItems.startDate = selStart
        selectedItems.endDate = selEnd
        #selectedItems.sensorType = selSensor

        #selectedItems.daily = dailySelect
        if dailySelect.get('value') == "on"
            selectedItems.daily = true
        #else
        #    selectedItems.daily = false
        #console.log("Start ",selStart,"  End: ",selEnd, "  Sensor: ",selSensor)
        console.log("Element to be Published ",selectedItems)

        #Publish an event to the NavTree stream
        #if download
        #    console.log("We need to download this Data")
        url = "../sumRestDL/electric/"

        content ={
            id:selectedItems.houses[0]
            daily:selectedItems.daily
            csv:true
            }

        queryparams = ioQuery.objectToQuery(content)
        queryString = url+"?"+queryparams
        console.log(queryString)

        linkString = "<a href='"+queryString+"' target='_blank'>Download</a>"
        tag = dojo.byId("dlUrl")
        tag.innerHTML = linkString


        topic.publish("navTree",selectedItems)

  )


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
    "dojo/topic"
    "dojo/io/script"
    ]
    (jsonRest,Cache,Observable,Memory,OnDemandGrid,Keyboard,Selection,editor,DijitRegistry,declare,topic,ioScript) ->
        console.log("Starting Grids")

        #Then the Grids
        baseGrid = new declare([OnDemandGrid,Keyboard,Selection,DijitRegistry])

        summaryGrid = baseGrid({
            columns:[
                {label:"Parameter",field:"param"}
                {label:"Value",field:"value"}
                ]
                }
                "sumGrid"
                )

        elecStore = Cache(Observable(jsonRest({target:"../sumRest/electric/"})),Memory())

        #dateFormatter = (dateStr) ->
            #if dateStr
            #    formatDate =  dojo.date.locale.format(theDate,{format:"short"})
            #    return
        #    return Date(dateStr/1000.0)


        dataGrid = baseGrid({
            columns:[
                {label:"Time",field:"date"}
                {label:"kWh",field:"kWh"}
                {label:"event",field:"event"}
                ]
            store: elecStore
            query: {daily:true}
                }
                "dataGrid"

                )

        topic.subscribe("navTree", (args) ->
            #fetchData(arg1)
            console.log("--- FIRED --- ",args)
            houseId = args.houses[0]
            console.log("House Id",houseId, "Daily",args.daily)
            dataGrid.setQuery({id:houseId,daily:args.daily})
            #return
            #And try to print all items in the store

            theData = []
            theSummary = {
                pre:{sum:0.0,count:0}
                post:{sum:0.0,count:0}
                }
            elecStore.query({id:houseId,daily:args.daily}).then((data) ->
                for item in data

                    #values = [Date(item.time),item.kWh]
                    kWh = item.kWh
                    values = [item.time,item.kWh]
                    theData.push(values)
                    if item.event == "PRE"
                        theSummary.pre.sum += kWh
                        theSummary.pre.count += 1
                    else if item.event == "POST"
                        theSummary.post.sum += kWh
                        theSummary.post.count += 1


                #console.log(theData)
                console.log(theSummary)
                plotData(theData)



                return
                )
            return
            )
            #


        plotData = (theData) ->
            #console.log("Plotting Called:",theData)
            options = {
                chart:
                    renderTo: "theGraph"
                title:
                    text: "Title"

                }
                #options.series = theData.series

                #options.series = theData.series
                #options.title.text = theData.title
                #console.log("Options ",options)
            options.series = [{
                name:"The Data",
                type:"column",
                data:theData}]
            chart = new Highcharts.StockChart(options)
            console.log("----> TS DONE", options)
            return





        return
    )

