#Heatmap script using d3.js
#

console.log("Starting Heatmap Script")

margin = {
    top : 100
    right: 20
    bottom: 0
    left: 30
    }

buckets = 9 #Number of buckets for data (Array -1)
#colors = ["#ffffd9","#edf8b1","#c7e9b4","#7fcdbb","#41b6c4","#1d91c0","#225ea8","#253494","#081d58"]
colors = colorbrewer.RdYlGn[10]

#nodes = [33,34] #Again overload this when we know the node Ids
#dates = ["2013-12-14","2013-12-15","2013-12-16"] #Over load when we know the Days.


#dates = {}
#nodes = {}


    # (thejson) ->


doplot = () ->
    d3.json("http://127.0.0.1:6543/rest/heatmap/",
        (thejson) ->
            console.log(thejson)
            nodes = thejson.nodelist
            dates = thejson.datelist
            data = thejson.data
            #minval = +thejson.min
            minval = 0
            maxval = +thejson.max
            range = maxval - minval
            bucketwidth = (range+1) / buckets
            console.log("Min ",minval, "Max",maxval)
            console.log("The Range is ",range, "Bucket Width", bucketwidth)
            #console.log("Nodes ",nodes)
            #console.log("Dates ",dates)
            #Work out which is the largest of the two arrays
            largest = nodes.length
            if dates.length > nodes.length
                largest = dates.length

            console.log("Largest Element ",largest)
            gridsize = Math.floor(height / largest)
            #gridheight = Math.floor(height / nodes.length) #We need to change this to match lenght of times
            #gridwidth = Math.floor(width / dates.length) #We need to change this to match lenght of times
            gridheight = 25
            gridwidth = 25

            viewport_width = (gridheight*dates.length) + 50
            viewport_height = (gridheight*nodes.length) + 100
            width = viewport_width - margin.left - margin.right
            height = viewport_height - margin.top - margin.bottom

            console.log("Gridwidth ",gridwidth)
            #legentElementWidth = gridsize*10

            #Now we create the rectangle
            svg = d3.select("#chart")
                .append("svg")
                .attr("width", viewport_width)
                .attr("height", viewport_height)
                .attr("display", "block")
                .append("g")
                .attr("transform", "translate("+margin.left+","+margin.top+")")

            #Stick a box around it
            svg.append("svg:rect")
                .attr("x", 0)
                .attr("y", 0)
                .attr("width", width)
                .attr("height", height)
                .attr("fill", '#fff')
                .attr("stroke", '#000')

            #Work out labels for the node
            nodelabels = svg.selectAll(".nodelabel")
                .data(nodes)
                .enter().append("svg:text")
                    .text((d) -> return d)
                    .attr("x", 0)
                    .attr("y", (d, i) -> return i*gridheight) #Shift down by gridzise (Change this to size to get square items)
                    .style("text-anchor","end") #Anchor outside of the box
                    .attr("dx", -6) #Move away from edge of box
                    .attr("dy", gridheight/2) #Centre 
                    #.attr("transform","translate(-6,"+gridsize/1.5+")") #Centre
                    
            #Labels for the date component
            datelabels = svg.selectAll(".datelabel")
                .data(dates)
                .enter().append("svg:text")
                    .text((d) -> return d)
                    .attr("transform", "rotate(-90)")
                    .attr("text-anchor", "start")                    
                    .attr("x", 0)
                    .attr("y", (d, i) -> return i*gridwidth ) #Shift across by gridzise
                    .attr("dy", gridwidth/1.5)


            for row, idx in data
                heatrows = svg.selectAll(".heatrows") 
                    .data(row)
                    .enter().append("svg:rect")
                        .attr("width", gridwidth)
                        .attr("height", gridheight)
                        .attr("fill", (d) -> return colors[Math.floor(d / bucketwidth)])
                        #.attr("stroke", '#f00')
                        .attr("stroke", '#aaa')
                        .attr("x", (d, i) -> return i*gridwidth)
                        .attr("y", (d) -> return idx*gridheight)



                heatlabel = svg.selectAll(".heatlabel")
                    .data(row)
                    .enter().append("svg:text")
                        .text((d) -> return d)
                        #    .attr("width", gridwidth)
                        #.attr("height", gridheight)
                        #.attr("fill", '#fff')
                        #.attr("stroke", '#f00')
                        .attr("x", (d, i) -> return i*gridwidth)
                        .attr("y", (d) -> return idx*gridheight)
                        .attr("dy", gridheight/2)
            #    .enter().append("svg:text")
            #    .text((d) -> d.count)

        )
        

doplot()