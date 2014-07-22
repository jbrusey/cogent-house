#Code to Generate Exposure plots

require(["dojo/topic","dojo/io/script","dojo/store/Memory","dojo/ready","dojo/request","dojo/dom","dojo/dom-construct","dgrid/Grid","dgrid/OnDemandGrid","dijit/form/Button"],
    (topic,ioscript,Memory,Ready,Request,dom,domConstruct,Grid,OnDemandGrid,Button) ->
        topic.subscribe("navTree", (arg1) ->
            fetchData(arg1)
            return
            )

        #For the sensor type Dropdowns
        data = [{id:0,name:"Temperature"}
                {id:2,name:"Humidity"}
            ]

        #Store to hold sensor types
        typeStore = new Memory({data:data})


        #when the DOM is Ready
        Ready (obj) ->
            dropdown = dijit.byId("sensorType")
            dropdown.set("store",typeStore)

            #Test Grid
            cols = [
                {field:"first",label:"First Name"},
                {field:"last",label:"Last Name"},
                {field:"age",label:"Age"}
                ]
                
            data = [
                {first:"Bob",last:"Baker",age:40}
                {first:"Dave",last:"Lister",age:55}
                {first:"Pat",last:"Sajak",age:64}
                ]

            #thisgrid = new Grid({columns:cols},"theGrid")                  
            return

        fetchData = (args) ->
            #console.log("Fetching Data with Args ",args)
            args.graphType = "expose"

            #We need to split out the Arguments to hold both sensor type
            sensorTypes = []
            #console.log("Sensor Types>",args.sensorType,"<")
            if args.sensorType == ""
                #console.log("--> SENSOR TYPE NOT SPECIFIED")
                sensorTypes = [0,2] #Default sensor types
            else
                sensorTypes = [args.sensorType]

            #Find a DIV to hold the graphs
            graphDiv = dom.byId("graphs")
            domConstruct.destroy("theGraph")
            domConstruct.empty("graphs")

            #For Eacg sensor type fetch the data
            for item in sensorTypes
                #Set up Arguments
                console.log("Fetching Data for ",item)
                args.graphType = "expose"
                args.sensorType = item

                #Grab the data from JSON
                ioscript.get({
                    url:"jsonFetch"
                    content:args
                    callbackParamName:"callback"
                    }).then((data) ->
                        #And Process the data
                        console.log("--> Data Returned ",data)
                        divid = "graph#{data.divid}"
                        newSec = domConstruct.create("section",{},"graphs")
                        newDom = domConstruct.create("div",{id:divid}, newSec)
                        plotExposure(data,newDom.id)

                        #And one for the Table
                        
                        divid = "table#{data.divid}"
                        newDom = domConstruct.create("div",{id:divid, style:"height:200px"},newSec)
                        exportBtn = domConstruct.create("button",{innerHTML:"Export"},newSec)
                        #exportBtn = false
                        writeTable(data,newDom,exportBtn)
                        #newDom = domConstruct.create("div",{id:"graph#{item}"},"theGraph","after")

                        #Working
                        #newDom = domConstruct.create("div",{id:divid},"graphs")


                        #tableHead = domConstruct.create("h4",{innerHTML:"Summary"},newDom,"after")
                        #tableBody = domConstruct.create("div",{id:"tab#{data.divid}"},tableHead,"after")
                        sep = domConstruct.create("hr",{},newSec,"after")
                        #plotExposure(data, "1")
                        console.log("--> Plotted")                        
                        return
                    )
            return


        plotExposure = (theData,domItem) ->
            options = {
                chart:
                    #renderTo: "theGraph"
                    renderTo: domItem
                    defaultSeriesType:"column"
                title:
                    text: "EXPOSE CHART"
                #credits:
                #    enabled: false
                exporting:
                    width: 1024
                xAxis:              
                    categories: []
                yAxis:
                    title:
                        text: "Percentage of Samples"
                plotOptions:
                    column:
                        stacking:"percent"
                        dataLabels:
                            enabled: true
                            style:
                                color: '#000000'
                                fontSize: '12px'
                            format: '{percentage:.2f}%'
                tooltip:
                    pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y:.2f}</b>Hours ({point.percentage:.2f}%)<br/>',
                    shared: true
                series: []
                }

            options.xAxis.categories = theData.labels
            options.series = theData.series
            options.title.text = theData.title

            chart = new Highcharts.Chart(options)
            #console.log("----> DONE", options)
            return

        percentFormatter = (thefloat) ->
            if typeof(thefloat) == "string"
                return thefloat
                
            return "#{thefloat.toFixed(2)} %"

        testRender = (object,value,node,options) ->
            console.log("Render Cell")
            console.log("--> Object",object)
            console.log("--> Value", value)
            console.log("--> Node",node)
            return node
            

        writeTable = (theData,domItem,exportBtn) ->
            console.log("Writing Table")
            console.log(theData)
            theseries = theData.series
            thelabels = theData.labels
            console.log("SERIES ",theseries)
            console.log("LABELS ",thelabels)
            console.log("Dom Item ",domItem)
            outData = {}
            #for el in theseries
            #    console.log("element ",element)

        
            #thisGrid = "FOO"
            #Create a grid to show this information

            #    columns: {
            #        level:"Category",
            #        room:"Room",
            #        }
            #    })
            #Test Grid
            #
        
            ##THIS WORKS (LONGTABLE)   
            ## cols = [
            ##     {field:"cat",label:"Category"},
            ##     ]

            ## i = 0
            ## for line in thelabels
            ##     #console.log("Label ",line)
            ##     tmpItem = {field:"cat#{i}",label:line}
            ##     #console.log("--> TMP ITEM ",tmpItem)
            ##     cols.push(tmpItem)
            ##     i++

            ## #And Work out the Data
            ## theData = []
            ## for line in theseries
            ##     console.log("Processing Series ",line)
            ##     outList = {"cat": line["name"]}
            ##     i = 0
            ##     for el in line["data"]
            ##         console.log("--> Processing element ",el)
            ##         outList["cat#{i}"] = el
            ##         i++
            ##     theData.push(outList)
            ##     console.log("OUTLIST ",outList)
            ## WORKS BUT IS LONGTABLE

            #Try WIDE TABLE
            cols = [{field:"room",label:"Room"}]

            idx = 0
            for item in theseries
                cols.push({field:"series#{idx}",label:item["name"],formatter:percentFormatter})
                #cols.push({field:"series#{idx}",label:item["name"],renderCell:testRender})
                idx += 1

            theData = []
            #And switch over the dataitems
            for itm,idx in thelabels
                dataitem = {room:itm}
                console.log("--> Processing Label ",itm,"  idx",idx)

                total = 0
                #colidx = 0
                datalist = [] #Temporay place for this
                for srs in theseries
                    console.log("--> --> And Series:",srs)
                    thedata = srs.data
                    console.log("--> --> And (Data):",thedata)
                    thisvalue = thedata[idx]
                    thecount = thisvalue
                    total += thisvalue
                    #console.log("--> --> And (count):",thecount)
                    #dataitem["series#{colidx}"] = thecount
                    datalist.push(thecount)
                    #colidx += 1
                    
                console.log("--> Series Done")
                #dataitem["total"] = total
                
                #Then update the totals so we get a percentage
                colidx = 0
                for srs in datalist
                   console.log("Srs ",srs)
                   if srs > 0
                       dataitem["series#{colidx}"] = ((srs / total) * 100.0)
                   else
                       dataitem["series#{colidx}"] = 0.00
                   colidx += 1

                console.log("--> Data Item ",dataitem)
                theData.push(dataitem)

            theStore = new Memory({
                data:theData,
                toCSV: (options) ->
                    console.log("SAVING")

                    options = options || {}
                    
                    alwaysQuote = options.alwaysQuote
                    #fieldNames = this.fieldNames
                    header = options.header
                    data = this.data
                    #delimiter = this.delimiter
                    delimiter = ","
                    newline = "\n" #this.newline
                    output = ""
                    console.log("Options Init")
                    console.log(this)
                    console.log(data)
                    console.log(header)
                    #First thing is to get the header
                    for item in header
                        output += "#{item["label"]}#{delimiter} "
                    output += "#{newline}"

                    #Then the rest of the data
                    for row in data
                        #console.log("R ",row)
                        for item in header
                            dataitem = row[item.field]
                            #console.log(dataitem)
                            output += "#{dataitem}#{delimiter} "
                        output += "#{newline}"
                    console.log(output)
                    #Export CSV

                    csvContent = "data:text/csv;charset=utf-8,"
                    csvContent += output
                    encodedURI = encodeURI(csvContent)
                    #console.log("Encoded ",encodedURI)
                    window.open(encodedURI)
                    #console.log("Opened")
                    #link = document.createElement("a")
                    #link.setAttribute("href",encodedURI)
                    #link.click()    
                    return output
                })

            console.log("Store is ",theStore)


            
            console.log("Colums == ",cols)
            console.log("Data == ",theData)
            thisgrid = new OnDemandGrid({columns:cols,store:theStore},domItem)
            #thisgrid.renderArray(theData)



            #exportBtn.onClick = console.log("FOO")
            theBtn = new Button({onClick: () -> theStore.toCSV({header:cols})},exportBtn)
            #domConstruct.create("div",{id:divid}, newSec)
            #console.log("--> The Grid ",thisGrid)
            #thisgrid.renderArray(tmpData)
            console.log("--> Done")
            #a = ['a','b','c']
            #for el,i in thelabels
            #for el,i in theseries
            #    outList = {}
            #    console.log("Element ",el," Index ",i)
                
            #    theName = thelabels[i]
            #    console.log("The Name ", theName)
                #    outList.name = theData.labels[index]
                #outData.push(outList)
                
            #console.log("OUT Data ",outData)
            #thisStore = new Memory()
            #    tablediv = 
            #Work out columns
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