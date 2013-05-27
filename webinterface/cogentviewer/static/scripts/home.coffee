require(
    ["dgrid/Grid",
     "dojo/ready",
    ]
    (Grid,ready) ->
        console.log("Loading JS")

        theGrid = new Grid({},"statusGrid")
        return
    )


# require(
#     ["dojo/store/Cache"
#      "dojo/store/JsonRest"
#      "dojo/store/Memory"
#      "dojo/store/Observable"
#      "dgrid/OnDemandGrid"
#      "dgrid/Keyboard"
#      "dgrid/Selection"
#      "dgrid/editor"
#      "dgrid/selector"
#      "dojo/_base/declare"
#      "dijit/form/Button"
#      "dgrid/extensions/DijitRegistry"
#      "dijit/Dialog"
#      "dijit/form/FilteringSelect"
#      "dijit/form/ComboBox"
#      "dojo/data/ObjectStore"
#      "dgrid/tree"
#      "dojo/ready"
#      ],
#      (Cache,jsonRest,Memory,Observable,OnDemandGrid,Keyboard,Selection,editor,selector,declare,Button,DijitRegistry,Dialog,FilterSelect,ComboBox,ObjectStore,tree,ready) ->


#       registerStore = Cache(Observable(jsonRest({target:"../sumRest/register/"})),Memory())

#       registerGrid = new declare([OnDemandGrid,Keyboard,Selection,DijitRegistry])({
#             columns: [
#                 #{label:"Location Id",field:"id"}
#                 selector(selectorType:"checkbox",label:"Select")
#                 {label:"id",field:"id"}
#                 tree({label:"Room",field:"room"})
#                 {label:"Type",field:"type"}
#                 {label:"Node",field:"node"}
#                 {label:"Status",field:"status"}#,formatter:statusFormatter}
#                 {label:"First Tx",field:"firstTx"}#,formatter:dateFormatter}
#                 {label:"Last Tx",field:"lastTx"}#,formatter:dateFormatter}
#                 {label:"Total Samples",field:"totalSamples"}

#                 #{label:"Last Tx",field:"lastTx",formatter:dateFormatter}
#                 #{label:"Voltage",field:"voltage",formatter:batteryFormatter}
#                 ]
#             selectorType:"checkbox"
#             store: registerStore
#             #store:statusStore
#             #query:{houseId:houseId,summary:true}
#             skin:"claro"
#             #renderRow:testRow
#             }
#             "theGrid"
#             )

#       return
#       )
