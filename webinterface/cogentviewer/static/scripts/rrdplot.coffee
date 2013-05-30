$(document).ready ->
    console.log("Script Called")

    options = {
        chart:{
            renderTo:"theGraph"
            zoomType: "x"
            }
        title:{
            text:"Test RRD"
            }

        rangeSelector: {
            buttons: [
                {type:"day",
                count:1,
                text:"1d"
                }
                {
                type:"day",
                count:3,
                text:"3d"
                }
                {
                type:"week",
                count:1,
                text:"1w"
                }
                {
                type:"week",
                count:2,
                text:"2w"
                }
                {
                type:"month",
                count:1,
                text:"1m"
                }
                {
                type:"all",
                text:"all"
                }

                ]
            }
        xAxis :{
            events:{
                afterSetExtremes: setExtremes
                }
                }
        series: [# {
            # name:"Daily Avg",
            # #type:"line",
            # #data: [[114341760000,1],[11434176,2],[3,3]]
            # data: [["2011-07-23T01:00:00", 21.899271336],
            #        ["2011-07-24T01:00:00", 22.003058189],
            #        ["2011-07-25T01:00:00", 22.272981256],
            #        ["2011-07-26T01:00:00", 22.658304162]
            #     ]
            # }
        ]
        }


    console.log(options.series)
    #theChart = new Highcharts.StockChart(options)

    url = "/rrd/"
    #Build a urlencoded URL
    $.getJSON(url, {hires:false}, (data) ->
        console.log("Fetching Data",data)
        startTime = data.meta.start * 1000
        step = data.meta.step * 1000
        console.log("Start: ",startTime, "  Step: ",step)
        data = data.data
        console.log(data)

        #Built the series
        #
        theSeries = [{
            name:"A Series"
            data: data
            pointStart:startTime
            pointInterval:step
            }]

        options.series = theSeries

        console.log("Options ",options)

        theChart = new Highcharts.StockChart(options)
        return
        )

    return

setExtremes = (e) ->
    currentExt = this.getExtremes()
    console.log("Extremes ",currentExt)
    console.log("e ",e)
    theChart = $("#theGraph").highcharts()
    theChart.showLoading('Loading Data')

    url = "/rrd/"
    $.getJSON(url, {hires:false,start:e.min,end:e.max}, (data) ->
        startTime = data.meta.start * 1000
        step = data.meta.step * 1000
        theSeries = [{
            name:"A Series"
            data: data
            pointStart:startTime
            pointInterval:step
            }]
        theChart.series[0] = theSeries
        theChart.hideLoading()
        return
        )

    return
    #    console.log("Fetching Data",data)
    #    #console.log("Meta ",data.meta," Step:",data.meta.step)
    #    options.series = data.data
    #    theChart = new Highcharts.StockChart(options)
    #    )
    #     return