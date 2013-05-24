# require([
#     "dojo/store/JsonRest"
#     "dgrid/extensions/DijitRegistry"
#     "dgrid/editor"
#     "dgrid/Selection"
#     "dgrid/selector"
#     "dojo/_base/declare"
#     "dojox/charting/Chart",
#     "dojo/domReady!"
#     ],
#     (Grid,tree,JsonRest,DijitRegistry,editor,Selection,selector,Declare,Chart) ->

#         nodeStore = JsonRest({
#             target: "rest/node/"
#             })

#     )


require([
    "dojo/store/JsonRest"
    "dojox/charting/Chart2D"
    "dojox/charting/DataChart"
    "dojox/charting/themes/MiamiNice"
    "dojox/charting/StoreSeries"
    "dojox/charting/DataSeries"
    "dojo/store/Memory"
    "dijit/form/FilteringSelect"
    #"dojox/form/CheckedMultiSelect"
    "dijit/form/Button"
    "dojo/on"
    "dojo/ready"
    #"dojox/charting/plot2d/Columns"
    #"dojox/charting/axis2d/Default"
    ]
    (JsonRest,Chart,DataChart,theme,StoreSeries,DataSeries,Memory,Select,Button,On,ready) ->

        nodeStore = JsonRest({target:"../rest/node/"})

        ready( ->
            console.log("Ready Function Called")
            nodeSelect = new Select({
                    id:"theNode",
                    value:"",
                    store:nodeStore,
                    required:true
                    query:{}
                    searchAttr:"id"}
                "theNode"
                )
            nodeSelect.startup()

            #serverStore = new Memory({
            #    data: ["

            #serverSelect = new Select{


            theButton = new Button({
                    id:"theButton"
                    label:"Show Data"
                    onClick: -> processClick()
                    }
                "theButton"
                )

            return
            )

        #End of Ready Function
        #On(dojo.byId("theButton"),"click",() ->
        #    console.log("Click")
        #    )
        #
        processClick = () ->
            console.log("Processsing Click")
            theItem = dijit.byId("theNode").get("value")
            if theItem
                console.log("Selected Item is ",theItem)
                renderGraph(theItem)


        chartStore = JsonRest({
             id:"chartStore"
             target: "../restTest/"
             identifier: "date"
             #query:{}
             })

        # # #Pure Dojo Charting
        # theChart = new Chart("theChart")
        # theChart.setTheme(theme)

        # theChart.addPlot("default",{
        #     type:"Columns"
        #     gap:1
        #     })

        # #theChart.addSeries("Jan",chartData,"value")
        # theChart.addSeries("y", new StoreSeries(chartStore,{query:{"*"}}))
        # theChart.addAxis("x")
        # theChart.addAxis("y",{vertical:true})
        # #theChart.addAxis("y")
        # theChart.render()



        # #testData = [[ "2011-09-12",  143], [ "2011-09-13",  147], [ "2011-10-28",  102], [ "2011-10-29",  288], [ "2011-10-30",  300], [ "2011-10-31",  288]]
        # chartData = []



        renderGraph = (theId) ->
            if not theId
                return
            chartStore.query({"id":theId}).then((data) ->

                newData = []
                for item in data

                    theDate = item.x #* 1000.0
                    dataItem = [item.x*1000,item.value]
                    newData.push(dataItem)

                highChart = new Highcharts.StockChart({
                chart:
                    renderTo: "highChart"
                    type: "column"
                title:
                    text: "Node #{theId} Data"
                xAxis:
                    type: "datetime"
                series: [
                    {name:"Foo",data:newData}
                    ]
                })



                )

            return

        return
    )
