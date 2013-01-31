<%inherit file="base.mak"/>


<%block name="styles">
<%doc>
<link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dojox/grid/resources/Grid.css')}"/>
<link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dojox/grid/resources/claroGrid.css')}"/>
</%doc>

<link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dgrid/css/skins/claro.css')}"/>


<style>
.good {
    color: green;
}

.fillgood {
    background:green;
}

.middle {
    color: orange;
}

.bad {
    color: red;
}

#grid .field-selector {
    width: 6em;
}
</style>

</%block>


<%block name="pagecontent">

This page allows houses within deployments to be registered or edited.

<section>
%if not theHouse:
    <p>
      Enter the details of the house below, 
      If the deployment has no end date set, please leave that field blank.
    </p>
%endif
</section>

<section>
<h3>Deployment Details</h3>
<form>
<dl>
<dt><label for="depName">Deployment Group</label></dt>
<dd><select id="depName"></select></dd>
</dl>


<h3>House Details</h3>

<dl>
<dt><label for="houseAdd">Address</label></dt>
<dd><input id="houseAdd" ></input></dd>

<dt><label for="stDate">Start Date</label></dt>
<dd><input id="stDate"></input><input id="stTime"></input></dd>

<dt><label for="edDate">End Date</label></dt>
<dd><input id="edDate"></input><input id="edTime"></input></dd>


</dl>


<button  id="Save">Submit</button>
<button  id="Reset">Cancel</button>
</form>

</section>

%if theHouse:
<section>


<h3>Registered Nodes</h3>
Details of nodes that are currenly registered and active to this house.

<div id="regGrid" style="width:100%; height:200px"></div>
<button id="regNode"></button>
<button id="unRegNode"></button>
<button id="clearNode"></button>
<button id="updateNode"></button>



<h3>Recently Heard Nodes</h3>
Details of nodes that have recently been heard by the server

<div id="statusGrid" style="width:100%; height:200px"></div>
<button id="statRegister"></button>
<button id="statRefresh"></button>
</section>
%endif


<!-- ---------- DIALOGS --------------- -->

<div class="dijitHidden">
  <div id="regNodeDialog" style="width:600px;" data-dojo-props="title:'Register Node'" data-dojo-type="dijit.Dialog">
    <form>
    <dl>
      <dt><label for="regNodeId">Node</label></dt>
      <dd><input id="regNodeId"></input></dd>
      <dt><label for="regNodeHouse">House</label></dt>#
      <dd><input id="regNodeHouse"></input></dd>
      <dt><label for="regNodeRoom">Room</label></dt>
      <dd><input id="regNodeRoom"></input></dd>
      <dt><label for="updateTimes">Refactor Dates</label></dt>
      <dd><input type="checkbox" id="updateTimes"></input></dd>
    </dl>
  <button id="dlg_regNode">Register</button>
  <button id="dlg_regCancel">Cancel</button>
  </form>
  </div>
</div>

</%block>

<%block name="scripts">
        %if theHouse:
            <script type="text/javascript">houseId = ${theHouse};</script>
	%else:
            <script type="text/javascript">houseId = null;</script>
        %endif
    
    <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/house.js')}"></script>
</%block>
