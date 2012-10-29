require([
    "dgrid/OnDemandGrid"
    "dgrid/tree"
    "dojo/store/JsonRest"
    "dgrid/extensions/DijitRegistry"
    "dgrid/editor"
    "dgrid/Selection"
    "dgrid/selector"
    "dojo/_base/declare"
    "dojo/domReady!"
    ],
    (Grid,tree,JsonRest,DijitRegistry,editor,Selection,selector,Declare) ->
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

        stdGrid = new Declare([Grid,DijitRegistry,Selection])

        theGrid = new stdGrid({
            store:treeStore,
            columns:[
                #tree({label:"id",field:"id"})
                editor({label:"Select",field:"bool"},"checkbox")
                tree({label:"name",field:"name"})
                {label:"parent",field:"parent"}
                {label:"type",field:"type"}
                ]
            }
            "gridNode"
            )

        theGrid.startup()


        #And the Data Grid

        dataGrid = new stdGrid({
            columns:[
                {label:"Deplyoment"}
                ]
            }
            "dataNode"
            )

        dataGrid.startup()

        return

    )
