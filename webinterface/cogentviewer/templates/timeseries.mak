##<%inherit file="baseContainers.mak"/>
<%inherit file="base.mak"/>

<%!
   _sideWidth = 3
   _mainWidth = 12 - _sideWidth
%>


<%block name="styles">
</%block>


<%block name="pageheader">
   <h1>Time Series Data</h1>
</%block>

<%block name="bodyheader">
  <!-- Add the container for the Controls-->
  <section class="well">
    <h3>Filters</h3>
    <div class="form-inline">
      <label>Start Date</label>
      <input type="datetime" id="startDate"></input>
      <label>Stop Date</label>
      <input type="datetime" id="stopDate"></input>
      <label>Sensor Type</label>
      <select id="sensorType"></select>
      <button id="getData"></button>
      <button id="clearData"></button>
    </div>
  </section>

</%block>

##Main Page Content
<%block name="pagecontent">
<%doc>
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
</%doc>
   
  <section>
    <h3>Graph</h3>
    <div id="graphs">
      <div id="theGraph" style="width:900px"</div>
    </div>
  </section>


</%block>  


##And Our Navigation Block
<%block name="sidenav">
    <h3>Select Data</h3>
    <div class="scroll-nav">
      <aside class="claro">
	<div id="treeNode"></div>  
      </aside>
    </div>
</%block>




<!-- Javascript Stuff -->

<%block name="scripts">
  ##Dojo Now Comes from Base File

  <!-- Global Var for the tree -->
  <script type="text/javascript">treeLimit = "temperature"</script>
  <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/chartingTree.js')}"></script>
  <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/timeplot.js')}"></script>

  <script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/Highstock/js/highstock.js')}"></script>	
  <script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/Highstock/js/themes/grid.js')}"></script>	
  <script src="http://code.highcharts.com/modules/exporting.js"></script>

</%block>

