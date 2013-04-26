console.log("FOO")

width = 960
height = 2000

tree = d3.layout.tree().size([height,width-160])

diagonal = d3.svg.diagonal().projection((d) -> [d.y,d.x])

vis = d3.select("#d3").append("svg").attr("width",width).attr("height",height).append("g").attr("transform","translate(40,0)")

d3.json("../restTest/", (json) ->
    nodes = tree.nodes(json)

    )