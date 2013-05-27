##<%inherit file="baseContainers.mak"/>


##<%block name="styles">

## <link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dojox/grid/resources/Grid.css')}"/>
## <link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dojox/grid/resources/claroGrid.css')}"/>

##</%block>

<%inherit file="base.mak"/>

<%!
   _sideWidth = 3
   _mainWidth = 12 - _sideWidth
%>

<%block name="pageheader">
<h1>Homepage</h1>
</%block>



<%block name="pagecontent">
<section>
<h1>Graphs</h1>
  <div id="graphs">
    <div id="theGraph" style="width:900px"</div>
  </div>
</section>
</%block>

##And Our Navigation Block
<%block name="sidenav">
  <div dojoType="dijit.layout.ContentPane" extractContent="false" preventCache="false" preload="false" refreshOnShow="false" region="left" splitter="true" doLayout="false" title="Main">

  <h3>Filters</h3>
  <ul>
    <li>StartDate</li>
    <li><div id="startDate"></div></li>
    <li>StopDate</li>
    <li><div id="stopDate"></div></li>
    <li>Sensor Type</li>
    <li><div id="sensorType"></div></li>
  </ul>

  <button id="getData"></button>
  <button id="clearData"></button>

    <h3>Select Data</h3>
    <div id="treeNode"></div>  


  </div>
</%block>

<!-- Javascripty Stuff -->

<%block name="scripts">
<%doc>
    <!-- Jquery is Required for the Graphing to Work -->
    <script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/jquery.min.js')}"></script>
    <script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/Highstock/js/highstock.js')}"></script>	

    <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/exposePlot.js')}"></script>
    <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/newNav.js')}"></script>
</%doc>

  <script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/jquery.min.js')}"></script>
  <script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/Highstock/js/highstock.js')}"></script>	
  <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/chartingTree.js')}"></script>
  <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/exposePlot.js')}"></script>

</%block>
