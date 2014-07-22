require([
    "dijit/form/FilteringSelect",
    "dojo/store/Cache"
    "dojo/store/JsonRest"
    "dojo/store/Observable"
    "dojo/store/Memory"
    "dojo/dom"
    "dojo/query"
    "dojo/parser"
    "dojo/domReady!"
    ]
    (Select,Cache,JsonRest,Observable,Memory,dom,query,parser) ->
        console.log("Testing")

        #Build the Store
        houseStore = Cache(Observable(JsonRest({target:"./rest/house/"})),Memory())

        houseSelect = new Select({
            name:"houseId"
            store:houseStore
            searchAttr: "address"
            #onChange: -> houseChange()
            }
            "House"
            )

        # houseSelect.startup()

        # roomStore = Cache(Observable(JsonRest({target:"./rest/houserooms/"})),Memory())

        # houseChange = () ->
        #     console.log("Select Changed")
        #     theId = houseSelect.get("value")
        #     selectbox = dom.byId("allsensors")
        #     console.log(selectbox)
        #     updateRooms(theId)
        #     return

        # updateRooms = (houseId) ->
        #     console.log("Id is ",houseId)
        #     htmlStr = ""
        #     roomStore.query({id:houseId}).forEach((item)->
        #         console.log(item)
        #         rname = item['name']
        #         #rid = "sensor_#{item['id']}"
        #         rid = item['id']
        #         htmlStr += '<label class="checkbox inline"><input type="checkbox" name="locids" value="'+rid+'">'+rname+'</label>'
                
        #         ).then(() ->
        #             console.log(htmlStr)
        #             theDiv = dom.byId("roomGroup")
        #             console.log("Div ",theDiv)
        #             theDiv.innerHTML = htmlStr
        #             )
                    
        #     return


        # radioChange = () ->
        #     console.log("Radio Changed")
        #     return

        

        return
    )


