<%inherit file="base.mak"/>

<%!
   _sideWidth = 0
   _mainWidth = 12 - _sideWidth
%>


<%block name="pageheader">
<h1>NodeStatus</h1>
</%block>


<%block name="pagecontent">

<h2>House ${house}</h2>

<table class="table">
<tr>
<th>Location Id</th>
<th>Room</th>
</tr>

%for row in locs:
  <tr>
    <td>${row[0]}</td>
    <td>${row[1]}</td>
  </tr>
%endfor
</table>

<h2>Nodes Registered Here</h2>
<table class="table">
  <tr>
    <th>Location</th>
    <th>Room</th>
    <th>Registered Nodes</th>
    <th>Nodes with data</th>
  </tr>
  %for line in regnodes:
    <tr>
      <td>${line["location"]}</td>
      <td>${line["room"]}</td>
      <td>${line["registered"]}</td>
      <td>${line["data"]}</td>
    </tr>
  %endfor
</table>

<h2>Unresigeterd Nodes (Have data but are not registered here</h2>
<table class="table">
  <tr>
    <th>Node</th>
    <th>Registered To</th>
  </tr>
  %for line in unreg:
    <tr>
      <td>${line[0]}</td>
      <td>${line[1]}</td>
    </tr>
  %endfor
</table>   

<h2>Location of nodes with data reporting here</h2>
<table class="table">
  <tr>
    <th>Node</th>
    <th>Registerd Loc</th>
    <th>Data Loc<th>
  </tr>
  %for line in reglocs:
    <tr>
      <td>${line["nid"]}</td>
      <td>${line["currentloc"]}</td>
      <td>${line["dataloc"]}</td>
    </tr>
  %endfor
</table>


</%block>
