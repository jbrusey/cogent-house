<%inherit file="base.mak"/>

<%block name="styles">
    <style type="text/css">

.chart {
  display: block;
  margin: auto;
  margin-top: 60px;
  font-size: 11px;
}

rect {
  stroke: #eee;
  fill: #aaa;
  fill-opacity: .8;
}

rect.parent {
  cursor: pointer;
  fill: steelblue;
}

text {
  pointer-events: none;
}

    </style>
</%block>


<%block name="pagecontent">
<h3>Node</h3>
<div id="theNode"></div>
<button id="theButton"></button>

<h3>High Chart</h3>
<div id="highChart"></div>


<h3>D3</h3>
<div id="d3">
      <button id="size" class="first">
        Size
      </button
      ><button id="count" class="active last">
        Count
      </button>

</div>
<script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/d3/d3.v2.js')}"></script>

    <script type="text/javascript">

var showCount = true;

var w = 1120,
    h = 600,
    //h= 1024,
    x = d3.scale.linear().range([0, w]),
    y = d3.scale.linear().range([0, h]);

//var vis = d3.select("#body").append("div")
var vis = d3.select("#d3").append("div")
    .attr("class", "chart")
    .style("width", w + "px")
    .style("height", h + "px")
  .append("svg:svg")
    .attr("width", w)
    .attr("height", h);

var partition = d3.layout.partition()
    .value(function(d) { return d.size; });
    //.value(function(d) { return 1; });

//d3.json("flare.json", function(root) {
//d3.json("../data/database.json", function(root) {
d3.json("../restTest/", function(root) {
  var g = vis.selectAll("g")
      .data(partition.nodes(root))
    .enter().append("svg:g")
      .attr("transform", function(d) { return "translate(" + x(d.y) + "," + y(d.x) + ")"; })
      .on("click", click);

  var kx = w / root.dx,
      ky = h / 1;

var color = d3.scale.category20c();

  g.append("svg:rect")
      .attr("width", root.dy * kx)
      .attr("height", function(d) { return d.dx * ky; })
      .attr("fill", function(d) { return color((d.children ? d : d.parent).name); })
      .attr("class", function(d) { return d.children ? "parent" : "child"; });

  g.append("svg:text")
      .attr("transform", transform)
      .attr("dy", ".35em")
      .style("opacity", function(d) { return d.dx * ky > 12 ? 1 : 0; })
      .text(function(d) {// if (d.size){
                         //   return d.name + " " +d.size + " (" +d.value +")";
                        //}
                        return d.name + " ("+d.value+")";

})


  d3.select(window)
      .on("click", function() { click(root); })

  function click(d) {
    if (!d.children) return;

    kx = (d.y ? w - 40 : w) / (1 - d.y);
    ky = h / d.dx;
    x.domain([d.y, 1]).range([d.y ? 40 : 0, w]);
    y.domain([d.x, d.x + d.dx]);

    var t = g.transition()
        .duration(d3.event.altKey ? 7500 : 750)
        .attr("transform", function(d) { return "translate(" + x(d.y) + "," + y(d.x) + ")"; });

    t.select("rect")
        .attr("width", d.dy * kx)
        .attr("height", function(d) { return d.dx * ky; });

    t.select("text")
        .attr("transform", transform)
        .style("opacity", function(d) { return d.dx * ky > 12 ? 1 : 0; });

    d3.event.stopPropagation();
  }

  function transform(d) {
    return "translate(8," + d.dx * ky / 2 + ")";
  }

d3.select("#count").on("click",function() {
    console.log("Count Clicked");
    showCount = true;
    d3.select("#size").classed("active",false);
    d3.select("#count").classed("active",true);
    
    //g.data(partition.value(function(d) { return 1; }));

//    partition
//        .value(function(d) { return 1; });
//    g.transition()
//        .duration(1500);
/*

        .data(partition.value(function(d) {return 1;}))
        .transition()
        .duration(1500);
*/
});

d3.select("#size").on("click",function() {
    console.log("Size Clicked");
    showCount = false;
    d3.select("#size").classed("active",true);
    d3.select("#count").classed("active",false);
});


});

    </script>



</%block>


<%block name="scripts">
  ##Dojo Now Comes from Base File
##<script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/dojo/dojo/dojo.js')}"></script>


  <script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/jquery.min.js')}"></script>
  <script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/Highstock/js/highstock.js')}"></script>	

  <%doc>
  <script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/Highcharts/js/highcharts.js')}"></script>	
  <script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/Highstock/js/modules/exporting.js')}"></script>	
  <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/timeplot.js')}"></script>
  <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/newNav.js')}"></script>

  <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/chartingTree.js')}"></script>
  <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/timeplot.js')}"></script>
  </%doc>


<script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/chartTest.js')}"></script>


<%doc>
<script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/d3/d3.v2.js')}"></script>
<script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/d3Test.js')}"></script>
</%doc>
</%block>

