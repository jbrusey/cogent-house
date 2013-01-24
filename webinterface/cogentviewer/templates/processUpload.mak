<%inherit file="base.mak"/>

<%block name="styles">

<link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dojox/grid/resources/Grid.css')}"/>
<link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dojox/grid/resources/claroGrid.css')}"/>

</%block>



<%block name="pagecontent">
<section>
  <h1>Deployment</h1>
      ${depString}

  <h1>House</h1>
      ${houseString}
    
  <h1>Rooms and Locations</h1>
  <table border=1>
    <tr><th>Node</th><th>Room</th><th>Room Type</th><th>Location</th></tr>
  % for room in roomStr:
  <tr><td>${room[0]}</td><td>${room[1]}</td><td>${room[2]}</td><td>${room[3]}</td></tr>
  % endfor
  </table>

  <h1>Data Transfered</h1>
  <table border=1>
    <tr><th>Node</th><th>Sensor Id</th><th>Samples</th></tr>
    % for item in transferStr:
    <tr><td>${item[0]}</td><td>${item[1]}</td><td>${item[2]}</td></tr>
    % endfor
    
  </table>

</section>
</%block>
