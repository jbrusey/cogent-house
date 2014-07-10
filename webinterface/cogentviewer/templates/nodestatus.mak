<%inherit file="base.mak"/>

<%!
   _sideWidth = 0
   _mainWidth = 12 - _sideWidth
%>


<%block name="pageheader">
<h1>NodeStatus</h1>
</%block>

<%block name="pagecontent">

<h2>All Nodes</h2>
<table class="table">
  <thead>
  <tr>
    <th colspan="2">
      Node
    </th>
    <th colspan="3">
      Data
      </th>
  </tr>
    
  <tr>
    <th>NodeId</th>
    <th>Location Id</th>
    <th>House</th>
    <th>Room</th>
    <th>Data Locations</th>
    <th>Data Times</th>
    <th>Data Samples</th>
    <th>Data House</th>
  </tr>
  </thead>
  <tbody>
    %for node in nodelist:
      <tr>
	<td>${node["nid"]}</td>
	<td>${node["locationId"]}</td>	
	<td>${node["house"]}</td>
	<td>${node["room"]}</td>
	<td>${node["datalocs"]}</td>
	<td>${node["datatimes"]}</td>
	<td>${node["datacount"]}</td>
	<td>${node["datahouse"]}</td>
      </tr>
    %endfor
  </tbody>

  
</table>

</%block>
