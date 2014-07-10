<%inherit file="base.mak"/>

<%block name="styles">

<link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dojox/grid/resources/Grid.css')}"/>
<link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dojox/grid/resources/claroGrid.css')}"/>

</%block>


<%block name="pagecontent">
<h1>Yield Report</h1>

<h2>Summary</h2>
<table class="table table-striped table-bordered">
  <tr>
    <th>Total Houses</th>
    <td>${summarytable["totalhouses"]}</td>
  </tr>
  <tr>
    <th>Total Nodes</th>
    <td>${summarytable["totalnodes"]}</td>
  </tr>
  <tr>
    <th>Nodes Reporting in the last day</th>
    <td>${summarytable["nodestoday"]}  (${summarytable["nodestoday"] / summarytable["totalnodes"] * 100.0})%</td>
  <tr>
  <tr>
    <th>Nodes with 90% Yield</th>
    <td>${summarytable["nodes90"]}</td>
  <tr>
  
</table>


%for house in yieldtable:
<h2>Report for ${house["house"]}:</h2>
<table class="table table-striped table-bordered">
  <thead>
    <tr><th>Node</th><th>Room</th><th>Last Report</th><th>Yield (Data)</th><th> Percent Tx</th></tr>
  <thead>
    <tbody>
      %for row in house["data"]:
      <tr>
	<td>${row["nodeid"]}</td>
	<td>${row["room"]}</td>
	<td><p class=${row["txclass"]}>${row["lasttx"]}</p></td>
	<td>${row["datayield"]}</td>
	<td>${row["packetyield"]}</td>
      <tr>
      %endfor

      <tr>
	<td>Average</td>
	<td>-</td>
	<td>-</td>
	<td>${house["avg"]}</td>
	<td>-</td>
    </tbody>
    
</table>

%endfor

</%block>

<%block name="scripts">

</%block>
