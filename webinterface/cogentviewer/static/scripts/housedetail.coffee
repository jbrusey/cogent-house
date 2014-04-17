chart = false

#Add a "helper function" to generate nav ranges
navranges = {
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
                    type:"week"
                    count:2
                    text:"2w"
                    }
                    {
                    type:"month"
                    count:1
                    text:"1m"
                    }
                    {
                    type:"ytd"
                    text:"YTD"
                    }
                    {
                    type:"all"
                    text:"All"
                    }
                    ]
                selected:0
                }


togglePushStatus = () ->
    chart = $('#thegraph').highcharts()
    if chart
        console.log("Chart Exists")
        for series in chart.series
            if series.name == "Push Status"
                console.log("Push Status Series", series)
                series.destroy()
                return
        console.log("Running End Stuff")
        nsum = 0
        for item in nodepairs
            nsum += item[0]

        navg = nsum / nodepairs.length
        console.log("SUM ",nsum, " AVG ",navg)        
        
        
        
        $.getJSON theurl, {graphtype:"pushstatus", hostname: hostname, offset: navg}, (data) ->
            series = {
                name: "Push Status"
                data: data
                #type: "column"
                dashStyle: "longdash"
                marker: {enabled: true}
                }
            console.log("Series to Add ",series)
            console.log("Chart ",chart)
            chart.addSeries(series)
            return
        
    else
        console.log("No Chart Exists")
        chartPushStatus()

    return


chartPushStatus = () ->
    chart = $('#thegraph').highcharts()
    if chart
        console.log("Chart Exists")
        chart.destroy()
    else
        console.log("No Chart Exists")
    
    $.getJSON theurl, {graphtype:"pushstatus", hostname: hostname}, (data) ->
        $('#thegraph').highcharts("StockChart",{
            series : [
                name : "Push Status",
                data: data
                marker: {enabled: true}
                ]
            xAxis:
                type: "datetime"
                ordinal: false
            rangeSelector: navranges
            })
        return
        
    chart = $('#thegraph').highcharts()
    return    


chartNodeState = () ->
    chart = $('#thegraph').highcharts()
    if chart
        console.log("Chart Exists")
        chart.destroy()
    else
        console.log("No Chart Exists")

    $.getJSON theurl, {graphtype:"nodestate", node: nodepairs[0][0]}, (data) ->
        console.log("Data is ",data)
        $('#thegraph').highcharts("StockChart",{
            series : [data]
            xAxis:
                type: "datetime"
                ordinal: false
            rangeSelector: navranges
            })


        chart = $('#thegraph').highcharts()
        console.log("New Chart is ",chart)

        for nodepair in nodepairs[1..]
            console.log("Getting Pair ",nodepair)
            $.getJSON theurl, {graphtype:"nodestate", node: nodepair[0]}, (data) ->
                console.log("Data is ",data)
                chart.addSeries(data)
        return
    return

pandasjson = () ->
    $.getJSON theurl, {graphtype:"nodestate-pandas", node: nodepairs[0][0], hostname: hostname}, (data) ->
        console.log(data)

$(document).ready ->
    chartNodeState()