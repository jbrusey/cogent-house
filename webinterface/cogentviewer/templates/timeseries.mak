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

##Main Page Content
<%block name="pagecontent">
<section>
##  <div data-spy="affix" data-offset-bottom="700">
  <!-- Add the container for the Graphs-->
  <h2>Global Filters</h2>
  
     
  <div id="graphs">
    <div id="theGraph" style="width:900px"</div>
  </div>
##  </div>
</section>
</%block>  


##And Our Navigation Block
<%block name="sidenav">
##<div dojoType="dijit.layout.ContentPane" extractContent="false" preventCache="false" preload="false" refreshOnShow="false" region="left" splitter="true" doLayout="false" title="Main">
<div class="scroll-nav">
  <aside class="claro">
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
  </aside>

  </div>
</%block>




<!-- Javascript Stuff -->

<%block name="scripts">
  ##Dojo Now Comes from Base File
  ## <script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/jquery.min.js')}"></script>
  <script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/Highstock/js/highstock.js')}"></script>	
  <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/chartingTree.js')}"></script>
  <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/timeplot.js')}"></script>

</%block>

