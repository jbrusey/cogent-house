# require(["dojo/io/script"])

require(["dojo/topic","dojo/io/script","dojo/store/Memory","dojo/ready","dojo/request","dojo/dom","dojo/dom-construct"],
    (topic,ioscript,Memory,Ready,Request,dom,domConstruct) ->
        topic.subscribe("navTree", (arg1) ->
            #fetchData(arg1)
            #console.log("--- FIRED --- ",arg1)
            fetchData(arg1)
            return
            )

        data = [{id:1,name:"Temperature"}
                {id:2,name:"Humidity"}
                {id:3,name:"Co2"}
            ]

        typeStore = new Memory({data:data})

        Ready (obj) ->
            #console.log("On Ready")
            dropdown = dijit.byId("sensorType")
            console.log("Drop ",dropdown)
            dropdown.set("store",typeStore)
            return

        fetchData = (args) ->
            console.log("Fecthing Data with Args ",args)
            args.graphType = "expose"

            #We need to split out the Arguments to hold both sensor type
            sensorTypes = []
            if args.sensorType == ""
                console.log("--> SENSOR TYPE NOT SPECIFIED")
                sensorTypes = ["1","2"]
            else
                sensorTypes = [args.sensorType]
            console.log("SENSOR TYPES ",sensorTypes)


            # Request.get("jsonFetch",{
            #     handleAs:"json"
            #     data:args
            #     }).then((response) ->
            #         console.log("======= REQ =========")
            #         console.log(response)
            #         console.log("======= REQ =========")
            #         plotExposure(response)
            #     )

            # return


            #graphDiv = dom.byId("graphs")
            domConstruct.destroy("theGraph")
            domConstruct.empty("graphs")
            domConstruct.create("div",{id:"theGraph"},"graphs")

            #console.log("Graph Div ",graphDiv)
            #for item in graphDiv.children
            #    console.log("--> ",item)

            for item in sensorTypes
                console.log(item)

                args.sensorType = item

                ioscript.get({
                    url:"jsonFetch"
                    content:args
                    callbackParamName:"callback"
                    }).then((data) ->
                        console.log("Data Returned ",data)
                        newDom = domConstruct.create("div",{id:"graph#{item}"},"theGraph","after")
                        console.log(newDom)
                        plotExposure(data,newDom.id)
                        console.log("Plotted")
                        return
                    )


        plotExposure = (theData,domItem) ->
            console.log("Building Time Series ",theData)
            console.log("Title",theData.title)
            options = {
                chart:
                    #renderTo: "theGraph"
                    renderTo: domItem
                    defaultSeriesType:"column"
                title:
                    text: "EXPOSE CHART"
                #legend:
                #    enabled: true
                #    layout: "vertical"
                #    verticalAlign:"bottom"
                credits:
                    enabled: false
                exporting:
                    width: 1024
                xAxis:
                    categories:["Default"]
                yAxis:
                    title:
                        text: "Percentage of Samples"
                plotOptions:
                    column:
                        stacking:"percent"
                series: []
                }

            options.xAxis.categories = theData.headers
            options.series = theData.series
            options.title.text = theData.title

            chart = new Highcharts.Chart(options)
            console.log("----> DONE", options)
            return


        return
    )

# fetchData = (contents) ->
#   console.log("Fetching Exposure Series")

#   console.log(contents)

#   contents.graphType = "expose"

#   dojo.io.script.get({
#     url:"jsonFetch"
#     content:contents
#     callbackParamName:"callback"
#     }).then((data) ->
#        console.log(data)
#        #console.log("Data Items")
#        #for item in data
#        #  console.log("-->")
#        #  console.log(item)
#        #plotTimeSeries(data)

#        if data.temperature
#          console.log("Plot Temperature")
#          plotExposure(data.temperature,"tempGraph")
#        if data.humidity
#          console.log("Plot Humidity")
#          plotExposure(data.humidity,"humGraph")

#        if data.co2
#         console.log("Plot Co2")
#         plotExposure(data.co2,"co2Graph")


#     )

# plotExposure = (theData,theDiv) ->
#   console.log("Plotting Exposure Graph")
#   console.log(theData)
#   options = {
#     chart:
#       renderTo: theDiv
#       defaultSeriesType: "column"
#     title:
#       text: "Exposure Graph"
#     yAxis:
#       title:
#         text: "Percentage Of Samples"
#     xAxis:
#       categories: ["Default"]
#     tooltip:
#       formatter: ->
#         "#{this.series.name}: #{this.percentage.toFixed(1)} %"
#     plotOptions:
#       column:
#         stacking: "percent"
#     credits:
#       enabled: false

#     series : []
#   }

#   options.title.text = theData.title
#   options.yAxis.title.text = theData.yAxis
#   options.series = theData.series
#   options.xAxis.categories = theData.labels
#   chart = new Highcharts.Chart(options)