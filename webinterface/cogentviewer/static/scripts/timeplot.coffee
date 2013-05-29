# Function to fetch and plot time series data
#

options = {
    chart:
        renderTo: "theGraph"
    rangeSelector :
        selected : 1
    title:
        text: "Time Series Data"
    series: [{}]
    }

window.chart = new Highcharts.StockChart({
    chart:
        renderTo: "theGraph"
    rangeSelector :
        selected : 1
    title:
        text: "Time Series Data"
    series: [{}]
    })


require(["dojo/topic","dojo/io/script"],
    (topic,ioscript) ->
        topic.subscribe("navTree", (arg1) ->
            fetchData(arg1)

            console.log("--- FIRED --- ",arg1)
            )
#                         title:
#                             text: "Time Series Data"
#                         legend:
#                             enabled: true
#                             align: "left"
#                             layout: "vertical"
#                             verticalAlign:"top"
#                         credits:
#                             enabled: false
#                         exporting:
#                             width: 1024
#                         xAxis:
#                             type: "datetime"
#                         rangeSelector:{
#                             buttons: [
#                                 {
#                                 type:"day"
#                                 count:1
#                                 text:"1d"
#                                 }
#                                 {
#                                 type:"day"
#                                 count:3
#                                 text:"3d"
#                                 }
#                                 {
#                                 type:"week"
#                                 count:1
#                                 text:"1w"
#                                 }
#                                 {
#                                 type:"all"
#                                 text:"All"
#                                 }
#                                 ]
#                                 selected:2
#                             }

##                        }

##        theChart = new Highcharts.StockChart(graphOptions)

        fetchData = (args) ->
            console.log("Fetching Data with Args ",args)
            args.graphType = "time"
            #console.log("Graphing Opts ",graphOptions)
            window.chart.showLoading()
            console.log("Done")
            ioscript.get({
                url:"jsonFetch"
                content:args
                callbackParamName:"callback"
                }).then((data) ->
                    console.log("Data Returned ",data)
                    #plotTS(data)
                    console.log("Plotted")
                    return
                )

                #legend:
                #    enabled: true
                #    align: "left"
                #    layout: "vertical"
                #    verticalAlign:"middle"
                #credits:
                #    enabled: false
                #exporting:
                #    width: 1024


        plotTS = (theData) ->
            console.log("Building Time Series ",theData)
            console.log("Title",theData.title)
            console.log("Seires",theData.series)
            options = {
                chart:
                    renderTo: "theGraph"
                title:
                    text: "CHART TITLE"
                legend:
                    enabled: true
                    align: "left"
                    layout: "vertical"
                    verticalAlign:"top"
                credits:
                    enabled: false
                exporting:
                    width: 1024
                xAxis:
                    type: "datetime"
                    #ordinal: false
                rangeSelector:{
                    buttons: [
                            {
                            type:"day"
                            count:1
                            text:"1d"
                            }
                            {
                            type:"day"
                            count:3
                            text:"3d"
                            }
                            {
                            type:"week"
                            count:1
                            text:"1w"
                            }
                            {
                            type:"all"
                            text:"All"
                            }
                        ]
                        selected:2
                        }

                #series: []
            }
            #options.series = theData.series

            options.series = theData.series
            options.title.text = theData.title
            console.log("Options ",options)
            chart = new Highcharts.StockChart(options)
            console.log("----> TS DONE", options)
            return

        return
    )


# fetchData = (contents) ->
#   console.log("Fetching Time Series")
#   console.log(contents)

#   contents.graphType = "time"

#   dojo.io.script.get({
#     url:"jsonFetch"
#     content:contents
#     callbackParamName:"callback"
#     }).then((data) ->
#        console.log(data)
#        plotTimeSeries(data)
#     )


# plotTimeSeries = (theData) ->
#   console.log("Plotting Graph")
#   console.log(theData)
#   options = {
#     chart:
#       renderTo: "theGraph"
#       #spacingBottom: 40
#     title:
#       text: ""
#     yAxis:
#       title:
#         text: ""
#     legend:
#       enabled: true
#       align: "left"
#       layout:"vertical"
#       verticalAlign: "middle"
#       #y: 35
#     credits:
#       enabled: false
#     xAxis:
#       title:
#         text: "Time"
#     exporting:
#       width: 1024
#     series : []
#   }

#   options.title.text = theData.title
#   options.yAxis.title.text = theData.yAxis
#   options.series = theData.series
#   chart = new Highcharts.StockChart(options)