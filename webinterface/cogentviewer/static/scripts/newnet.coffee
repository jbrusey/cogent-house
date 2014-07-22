
width = 1024
height = 256

scrollwidth = 1024
scrollheight = 128
scrollborder = 25

            
orignodes = null
maxdepth = 0
maxcount = 0
mincount = 0
maxlinks = 0
minlinks = 0

    

#Work out the Timeline
d3.json "http://127.0.0.1:6543/rest/topology/", (json) ->
    console.log("All Data", json)
    topology = json.topolo
    console.log("Toplolgy is ",topology)

    
    console.log("Drawing Timeline")
    timesvg = d3.select("#timeline").append("svg")
        .attr("width",scrollwidth*2)
        .attr("height",scrollheight)
        
    #append a box
    timesvg.append("svg:rect")
                    .attr("x", 0)
                    .attr("y", 0)
                    .attr("scrollwidth", scrollwidth)
                    .attr("scrollheight", scrollheight)
                    .attr("fill", '#fff')
                    .attr("stroke", '#000')

    
    startdate = new Date(json.startdate) #Fucking 0 based Months !!!!!!
    enddate = new Date(json.enddate)
    console.log("Start ",startdate," End",enddate)

    #Work out our scale
    #thescale = d3.scale.linear()
    #    .domain([0,100])
    #    .range([0,(scrollwidth-scrollborder)*2])
    thescale = d3.time.scale()
        .domain([startdate,enddate])
        .range([0,(scrollwidth-scrollborder)*2])

    theaxis = d3.svg.axis()
        .scale(thescale)
        .orient("bottom")

    timesvg.append("g")
        .attr("transform", "translate("+scrollborder+"," + (scrollheight-25) + ")")
        .call(theaxis)

    timeitems = timesvg.selectAll(".timeitem")
        .data(d3.values(topology))
        .enter().append("g")
            .attr("transform",(d) -> "translate("+thescale(new Date(d.date))+","+(scrollheight-25-10)+")")

    timeitems.append("circle")
        .attr("r",10)
        .attr("fill",'#AAA')
        .attr("stroke",'#000')

    timeitems.append("svg:text")
       .text((d)->d.id)


        
# d3.json "http://127.0.0.1:6543/rest/network/", (json) ->
#     console.log("All Data", json)

#     links = json.links
#     console.log("Links ",links)

#     #Work out the new version of the nodes
#     orignodes = json.nodes
#     nodes = {}

#     nodemap = d3.map()
#     orignodes.forEach (n) ->
#         nodemap.set(n.id, n)

#         if n.depth > maxdepth
#             maxdepth = n.depth
#         if n.count > maxcount
#             maxcount = n.count
#         if mincount == 0
#             mincount = maxcount
#         else if n.count < mincount
#             mincount = n.count

#         n.pinx = 200+(n.depth*150)
                  
#         #n.x = width / 2.0
#         #n.x = 200 + (n.depth*150)
#         #n.y = height / 2.0
#         #n.fixed=true

#     #Normalise counts between 0 and 10
#     rad_step = 10.0 / (maxcount - mincount) 

#     links.forEach (l) ->
#         if l.count > maxlinks
#             maxlinks = l.count
#         if minlinks == 0
#             minlinks = maxlinks
#         else if l.count < minlinks
#             minlinks = l.count
            
#         l.source = nodemap.get(l.source)
#         l.target = nodemap.get(l.target)    

#     tick = () ->
#         link
#             .attr("x1", (d) -> d.source.pinx)
#             .attr("y1", (d) -> d.source.y)
#             .attr("x2", (d) -> d.target.pinx)
#             .attr("y2", (d) -> d.target.y)
            
#         node
#             #.attr("y", (d) -> d.y)
#             .attr("transform", (d) -> return "translate(" + d.pinx + "," + d.y + ")")
#             #.attr("transform", (d) -> return "translate(" + d.x + "," + d.y + ")")
#         return #Important

#     dragstart = (d) ->
#         d3.select(this).classed("fixed", d.fixed=true)



#     force = d3.layout.force()
#         #.nodes(d3.values(nodes))
#         .nodes(orignodes)
#         .links(links)
#         .size([width,height])
#         #.linkDistance(150)
#         #.charge(-60)
#         .linkDistance(100)
#         .charge(-70)
#         .on("tick", tick)
#         .start()

#     drag = force.drag()
#         .on("dragstart",dragstart)


#     svg = d3.select("#vis").append("svg")
#         .attr("width", width)
#         .attr("height", height)


#     #Stuff for arrowheads
#     svg.append("defs").append("marker")
#         .attr("id", "arrowhead")
#         .attr("refX", 6 + 3)
#         .attr("refY", 2)
#         .attr("markerWidth", 12)
#         .attr("markerHeight", 4)
#         .attr("orient", "auto")
#         .append("path")
#             #.attr("d", "M 0,0 V 4 L6,2 Z"); 
#             .attr("d", "M 0,0 V 4 L6,2 Z"); 

#     link = svg.selectAll(".link")
#         .data(force.links())
#             .enter().append("line")
#                 #.attr("class","link")
#                 .attr("marker-end","url(#arrowhead)")
#                 .attr("stroke": '#F00')
#                 .attr("stroke-width": '1.5px')

#     node = svg.selectAll(".node")
#         .data(force.nodes())
#             .enter().append("g")
#                 .attr("class", "node")
#                 .call(force.drag)   

#     node.append("circle")
#         .attr("r", (d) -> 10)
#         .attr("fill", "#ccc")
#         .attr("stroke", "#000")
#         .attr("stroke-width": '1.5px')

#     node.append("svg:text")
#         .text((d) -> d.name)
#         .attr("y", 25)
#         .attr("text-anchor","middle")

#     return