#TRy to get the tree sorted here
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
                theChildren = this.query({parent: object.id})
                #console.log("Children Are ",theChildren)
                return theChildren
            #mayHaveChildren: (object) ->
            #    console.log("May Have children Called for ",object)
            #    return object.children == true
                #return false
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
        # treeModel = new ObjectStoreModel({
        #     store: treeStore,
        #     query: {"root"}
        #     mayHaveChildren: (item) ->
        #         log.debug("Calling May Have Children for ",item)
        #         return item.children == true
        # })

        # theTree = new Tree({
        #     model: treeModel
        #     }
        #     "treeNode"
        #     )

        # theTree.startup()

    #theTree.startup()

    )



#Sort out the Dropdowns
require([
  "dijit/form/Button"
  "dijit/form/DateTextBox"
  "dijit/form/FilteringSelect"
  "dojo/store/Cache"
  "dojo/store/JsonRest"
  "dojo/store/Observable"
  "dojo/store/Memory"
  "dijit/tree/ObjectStoreModel"
  "dijit/Tree"
  "dojo/ready"
  "dojo/topic"
  "dojo/domReady!"
  ],
  #(FilteringSelect,DateTextBox) ->
  (Button,DateTextBox,Select,Cache,JsonRest,Observable,Memory,ObjectStoreModel,Tree,ready,topic) ->

    # #Make the Tree
    # #treeStore = Cache(Observable(JsonRest({target:"./rest/deploymenttree/"})),Memory())
    # treeStore = JsonRest({
    #     target: "./rest/deploymenttree/"
    #     })

    # #treeStore.getParent = (object) ->
    # #    console.log("Getting parent for ",object)
    # #   return this.query({parent: object.id})



    # #treeStore.mayHaveChildren = () ->


    # treeModel = new ObjectStoreModel({
    #     store: treeStore,
    #     query: {id:"root"}
    #     })


    # ready(() ->
    #     theTree = new Tree({
    #         model: treeModel
    #         }
    #         "treeNode"
    #         )
    #     console.log("Starting Tree")
    #     theTree.startup()
    #     console.log(treeModel)
    #     )
    #
    # theTree = new Tree({
    #     model: treeModel
    #     }
    #     "treeNode"
    #     )
    # theTree.startup()

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


    #Store the the Filtering Select
    #typeStore = new ItemFileReadStore({
    #  url: "jsonnav"
    #  })

    sensorTypeSelect = new Select({
      name:"sensorType"
      store: typeStore
      #query:{"type":"sensor"}
      }
      "sensorType"
      )

    sensorTypeSelect.startup()

    #Buttons

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


    ##Functions to process data
    showData = () ->
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
                else if splitItem[0] == "l"
                    selectedItems.locations.push(splitItem[1])
                else if splitItem[0] == "t"
                    selectedItems.locType.push([splitItem[1],splitItem[2]])
        #console.log("Selected Items ",selectedItems)
        #We can then deail with the selected items

        selStart = startDateSelect.get("value")
        selEnd = stopDateSelect.get("value")
        selSensor = sensorTypeSelect.get("value")

        selectedItems.startDate = selStart
        selectedItems.endDate = selEnd
        selectedItems.sensorType = selSensor

        #console.log("Start ",selStart,"  End: ",selEnd, "  Sensor: ",selSensor)
        console.log("Element to be Published ",selectedItems)

        #Publish an event to the NavTree stream
        topic.publish("navTree",selectedItems)

  )
