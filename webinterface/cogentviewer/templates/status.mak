<%inherit file="base.mak"/>

<%block name="styles">

<link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dojox/grid/resources/Grid.css')}"/>
<link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dojox/grid/resources/claroGrid.css')}"/>

</%block>


<%block name="pagecontent">

<section>
<h2>Deployments</h2>
<div id="deployGrid" style="width:100%; height:200px">
</div>
<!-- Buttons -->
<div id="newDep"></div>
<div id="saveDep"></div>
<div id="deleteDep"></div>
<div id="clearDep"></div>
</section>

<section>
<h2>Houses</h2>

<div id="houseGrid" style="width:100%; height:200px">
</div>

<div id="newHouse"></div>
<div id="saveHouse"></div>
<div id="deleteHouse"></div>
<div id="clearHouse"></div>
</section>

<section>
<h2>Rooms</h2>

</section>

<%doc>
<section>
  <h2>Nodes</h2>
  <h3>Registered Nodes</h3>
  <table border=1>
    <tr>
      <th>Node</th>
      <th>Location</th>
      <th>House</th>
      <th>Room</th>
      <th>Last Transmission</th>
    </tr>
    
    %for item in liveReg:
    <tr>
      <td>${item.nodeId}</td>
      <td>${item.node.location}</td>
      <td>${item.node.location.house.address}</td>
      <td>${item.node.location.room.name}</td>
      <td>${item.time}</td>
    </tr>
    %endfor

  <%doc>
  </table>
  <h3>Registered Nodes Not Reporting</h3>
  <table border=1>
    <tr>
      <th>Node</th>
      <th>Location</th>
      <th>House</th>
      <th>Room</th>
      <th>Last Transmission</th>
    </tr>

    %for item in deadReg:
    <tr>
      <td>${item.nodeId}</td>
      <td>${item.node.location}</td>
      <td>${item.node.location.house.address}</td>
      <td>${item.node.location.room.name}</td>
      <td>${item.time}</td>
    </tr>
    %endfor
   </%doc>
   
<%doc>
  </table>
  <h3>Unregistered Nodes</h3>
  <table border=1>
    <tr>
      <th>Node</th>
      <th>Last Transmission</th>
      <th></th>

    %for item in unreg:
    <tr>
      <td>${item.nodeId}</td>
      <td>${item.time}</td>
      <td><button data-dojo-type="dijit.form.Button"
		  data-dojo-props="onClick:function(){console.log('Button Pressed Id', ${item.nodeId}); setNodeId(${item.nodeId}); dijit.byId('regDialog').show();}">	  
	  Register</button></td>
    </tr>
    %endfor

  </table>
</%doc>
</section>


<div class="dijitHidden">
  <div id="regDialog" style="width:600px;" data-dojo-props="title:'Register Node'" data-dojo-type="dijit.Dialog">
    <dl>
      <dt><label for="regNodeId">Node</label></dt>
      <dd><input id="regNodeId"></input></dd>
      <dt><label for="regNodeHouse">House</label></dt>
      <dd><input id="regNodeHouse"></input></dd>
      <dt><label for="regNodeRoom">Room</label></dt>
      <dd><input id="regNodeRoom"></input></dd>
    </dl>
  <button id="dlg_regNode">Register</button>
  <button id="dlg_regCancel">Cancel</button>
  <button id="dlg_regNewRoom">New Room</button>
  </div>
</div>

<div class="dijitHidden">
  <div id="roomDialog" style="width:500px;" data-dojo-props="title:'New Room'" data-dojo-type="dijit.Dialog">
    <dl>
      <dt><label for="newRoomRoom">Room Name</label></dt>
      <dd><input id="newRoomRoom"></input></dd>
      <dt><label for="newRoomType">Room Type</label></dt>
      <dd><input id="newRoomType"></input></dd>
    </dl>
    <button id="dlg_roomOk">Add</button>
    <button id="dlg_roomCancel">Cancel</button>
  </div>
</div>



<div class="dijitHidden">
  
    <div id="depDialog" style="width:600px;"  data-dojo-props="title:'Add New Deployment'" data-dojo-type="dijit.Dialog">
    <dl>
      <dt><label for="depName">Name</label></dt>
      <dd><input id="depName" data-dojo-type="dijit.form.TextBox"></input></dd>
      <dt><label for="depDesc">Description</label></dt>
      <dd><textarea id="depDesc" rows=5 cols=30 data-dojo-type="dijit.form.SimpleTextarea"></textarea></dd>
      <dt><label for="depStart">Start Date</label></dt>
      <dd><input id="depStart" data-dojo-type="dijit.form.DateTextBox"></input></dd>
      <dt><label for="depEnd">End Date</label></dt>
      <dd><input id="depEnd" data-dojo-type="dijit.form.DateTextBox"></input></dd>
    </dl>
    <button id="dlg_addDep">Submit</button>
    <button id="dlg_clearDep">Cancel</button>
   </div>
</div>

<div class="dijitHidden">
  <div id="houseDialog" style="width:600px;"  data-dojo-props="title:'Add New Nouse'" data-dojo-type="dijit.Dialog">
    <h3>Add New House</h3>
    <dl>
      <dt><label for="houseAdd">Address</label></dt>
      <dd><input id="houseAdd" data-dojo-type="dijit.form.TextBox"></input></dd>
      <!-- <dt><label for="houseAdd">Address</label></dt> -->
      <!-- <dd><input id="houseAdd"></input></dd> -->
      <dt><label for="houseStart">Start Date</label></dt>
      <dd><input id="houseStart" data-dojo-type="dijit.form.DateTextBox"></input></dd>
      <dt><label for="houseEnd">End Date</label></dt>
      <dd><input id="houseEnd" data-dojo-type="dijit.form.DateTextBox"></input></dd>
      <dt><label for="houseDep">Deployment</label></dt>
      <dd><input id="houseDep" data-dojo-type="dijit.form.TextBox"></input></dd>
    </dl>
    <button id="dlg_addHouse">Submit</button>
    <button id="dlg_clearHouse">Cancel</button>
  </div>

</div>




</%block>  


<!-- Javascripty Stuff -->
<%block name="scripts">
    <!-- Jquery is Required for the Graphing to Work -->
    <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/status.js')}"></script>
</%block>
