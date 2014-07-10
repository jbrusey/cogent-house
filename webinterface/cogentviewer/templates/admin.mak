<%inherit file="base.mak"/>

<%block name="styles">

<link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dojox/grid/resources/Grid.css')}"/>
<link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dojox/grid/resources/claroGrid.css')}"/>

</%block>


<%block name="pagecontent">

<h1>Admin Interface</h1>
Here we can update all the various room types and other metadata

<h2>Deployments</h2>
<div id="deployGrid" style="width:100%; height:200px;"></div>
<div class="btn-group">
  <button id="deployNew" class="btn">New</button>
  <button id="deployDelete" class="btn">Delete</button>
  <button id="deploySave" class="btn">Save</button>
  <button id="deployReset" class="btn">Refresh</button>
</div>

<h2>Houses</h2>
<div id="houseGrid" style="width:100%; height:200px;"></div>
<div class="btn-group">
  <button id="houseNew" class="btn">New</button>
  <button id="houseReset" class="btn">Delete</button>
  <button id="houseSave" class="btn">Save</button>
  <button id="houseDelete" class="btn">Refresh</button>
</div>



<h2>Rooms</h2>
<div id="roomGrid" style="width:100%; height:200px;"></div>
<div class="btn-group">
  <button id="roomSave" class="btn"></button>
  <button id="roomReset" class="btn"></button>
  <button id="roomDelete" class="btn" ></button>
</div>
<!-- <button id="roomNew"></button> -->

<h2>Room Types</h2>
<div id="typeGrid" style="width:100%; height:200px;"></div>
<div class="btn-group">
  <button id="typeSave" class="btn"></button>
  <button id="typeReset" class="btn"></button>
</div>
<!-- <button id="typeNew"></button> -->

<h3>Users</h2>
<table class="table">
  <thead>
    <tr>
      <td>Username</td>
      <td>Email</td>
      <td>Edit</td>
    </tr>
  </thead>
 
  <tbody>
    %for user in userList:
    <tr>
      <td>${user[0]}</td>
      <td>${user[1]}</td>
      <td><a href=${user[2]}>Edit User</a></td>
    </tr>
    %endfor
  </tbody>
</table>
<a class="btn" href="${request.route_url('user',id='')}">Add New User</a>

<!-- Dialogs -->
<div class="dijitHidden">
  <div data-dojo-type="dijit/Dialog" data-dojo-id="depDlg" title="Add Deployment">
    <p>Test Dialog</p>
  </div>
</div>

<%doc>
## <div class="dijitHidden">
##  <div id="depDlg" style="width:600px;" data-dojo-props="title:'Add Deployment'" data-dojo-type="dijit/Dialog" data-dojo-id="depDlg">
    <dl>
      <dt><label for="dep_name">Name</label></dt>
      <dd><input id="dep_name" required="true"></input></dd>

      <dt><label for="dep_desc">Description</label></dt>
      <dd><input id="dep_desc"></input></dd>

      <dt><label for="dep_startDate">Start Date</input></dt>
      <dd><input id="dep_startDate"></input></dd>

      <dt><label for="dep_endDate">End Date</input></dt>
      <dd><input id="dep_endDate"></input></dd>
    </dl>
    <button id="dep_ok">Save</button>
    <button id="dep_cancel">Cancel</button>
##  </div>
## </div>

<div class="dijitHidden">
  <div id="houseDlg" style="width:600px;" data-dojo-id="houseDlg" data-dojo-props="title:'Add House'" data-dojo-type="dijit.Dialog">
    <dl>
      <dt><label for="house_add">Address</label></dt>
      <dd><input id="house_add" required="true"></input></dd>
      
      <dt><label for="house_dep">Deployment</label></dt>
      <dd><input id="house_dep" required="true"></input></dd>

      <dt><label for="house_startDate">Start Date</input></dt>
      <dd><input id="house_startDate"></input></dd>

      <dt><label for="house_endDate">End Date</input></dt>
      <dd><input id="house_endDate"></input></dd>
    </dl>
    <button id="house_ok"></button>
    <button id="house_cancel"></button>
  </div>
</div>

<div class="dijitHidden">
  <div id="typeDlg" style="width:600px" data-dojo-props="title:'Add Room Type'" data-dojo-type="dijit.Dialog">
    <dl>
      <dt><label for="type_name">Name</label></dt>
      <dd><input id="type_name"></dd>
    </dl>
    <button id="type_ok"></button>
    <button id="type_cancel"></button>
  </div>
</div>

<div class="dijitHidden">
  <div id="roomDlg" style="width:600px" data-dojo-props="title:'Add Room'" data-dojo-type="dijit.Dialog">
    <dl>
      <dt><label for="room_name">Name</label></dt>
      <dd><input id="room_name"><input></dd>
      <dt><label for="room_type">Type<label></dt>
      <dd><input id="room_type"><input></dd>
    </dl>
    <button id="room_ok"></button>
    <button id="room_cancel"></button>
  </div>
</div>
</%doc>

</%block>

<%block name="scripts">
        <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/admin.js')}"></script>
</%block>
