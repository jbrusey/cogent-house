<%inherit file="base.mak"/>

<%!
   _sideWidth = 0
   _mainWidth = 12 - _sideWidth
%>

<%block name="pageheader">
<h1>Homepage</h1>
</%block>


##<%inherit file="baseContainers.mak"/>


<%block name="pagecontent">
<section>
  <h1>Electricity Use</h1>
</section>

<h3>Summary</h3>
<div id="mean"></div>

<h3>Data</h3>
<div id="dlUrl"></div>
<div id="theGraph"></div>
<div id="dataGrid" style="width:100%; height:200px"></div>

</%block>  


##And Our Navigation Block
<%block name="othercontent">
  <div dojoType="dijit.layout.ContentPane" extractContent="false" preventCache="false" preload="false" refreshOnShow="false" region="left" splitter="true" doLayout="false" title="Main">

  <aside>
  <h3>Filters</h3>
  <ul>
    <li>StartDate</li>
    <li><div id="startDate"></div></li>
    <li>StopDate</li>
    <li><div id="stopDate"></div></li>
    <li>Summary By</li>
    <li><input type="radio" name="hourly" id="hourlyRad" value="hourly">Hourly</input>
      <input type="radio" name="hourly" id="dailyRad" value="daily" checked>Daily</input>
    <%doc>
    <li>Sensor Type</li>
    <li><div id="sensorType"></div></li>
    </%doc>
  </ul>

  <button id="getData"></button>
  <button id="clearData"></button>
    <h3>Select Data</h3>
    <div id="treeNode"></div>  
  </aside>

  </div>
</%block>

<!-- Javascripty Stuff -->
<%block name="scripts">
  <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/electric.js')}"></script>
  <script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/jquery.min.js')}"></script>
  <script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/Highstock/js/highstock.js')}"></script>	
</%block>
