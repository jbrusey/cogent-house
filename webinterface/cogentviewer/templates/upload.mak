<%inherit file="base.mak"/>

<%block name="styles">

<link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dojox/grid/resources/Grid.css')}"/>
<link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dojox/grid/resources/claroGrid.css')}"/>

</%block>



<%block name="pagecontent">
<section>
<h1>Upload Data</h1>
This page allows you to upload data from an external source
</section>

<%doc>
<section>
<h2>External Database Details</h2>
TODO
</section>
</%doc>



<%doc>
<section>
<h1>House Details<h1>
<h2>Houses in Transfer Database</h2>
<table>
  <tr>
    <th>Address</th><th>Start Date</th><th>End Date</th><th>Use</th>
  </tr>						 
% for house in houses :
  <tr>
    <td>${house.address}</td>
    <td>${house.startDate}</td>
    <td>${house.endDate}</td>
    <td><input type="radio" name="depId" value=${house.id}></input></td>
  </tr>
% endfor
</table>
</section>
</%doc>



<section>
##<form method="POST">
<div data-dojo-type="dijit.form.Form" id="uploadForm" data-dojo-id="uploadForm" encType="mutipart/form-data" action="procUpload" method="post">

<h1>Deployment</h1>
Please Select the Deployment Details
<select name="DeploymentSelect" data-dojo-type="dijit.form.ComboBox" id="DeploymentSelect" placeHolder="select deployment">
  % for dep in deployments:
      <option>${dep.name}</option>
  % endfor
</select>

<h1>House to upload</h1>
Please enter details of the house to upload here
<table>
  <tr><td>Address</td><td><input type="text" id="address" name="address" required="true" data-dojo-type="dijit.form.TextBox"></input></tr>
  <tr><td>Start Date</td><td><input id="stDate" name="stDate" data-dojo-type="dijit.form.DateTextBox" required="true"></input></td></tr>
  <tr><td>End Date</td><td><input id="edDate" name="edDate" data-dojo-type="dijit.form.DateTextBox" required="true"></input></td></tr>
</table>



<h1>Nodes</h1>
Please update the node details, leave the input blank if this node was not used.
<table border=1>
  <tr>
    <th>Node Id</th>
    <th>Room</th>
    <th>Room Type</th>
  </tr>

% for node in nodes:
<tr>
  <td>${node.id}</td>
  <td><input type="text" id="Node_${node.id}" name="Node_${node.id}" data-dojo-type="dijit.form.TextBox"></input></td>
  <td>
    <select name="Select_${node.id}"  data-dojo-type="dijit.form.ComboBox"  id="Select_${node.id}">
      % for rType in roomTypes:
          <option value="${rType.name}"> ${rType.name}</option>
      % endfor
    </select>
  </td>
</tr>
% endfor


</table>




<button data-dojo-type="dijit.form.Button" type=button onClick="console.log(uploadForm.getValues())">Get Values</button>
<button data-dojo-type="dijit.form.Button" type="submit" name="submitButton" value="Submit">Submit</button>
<button data-dojo-type="dijit.form.Button" type="reset">Reset</button>
</div>


</section>

</%block>


<%block name="scripts">
    <script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/dojo/dojo/dojo.js')}" djConfig="parseOnLoad:true"></script>

    <script type="text/javascript">
      dojo.require("dijit.form.Form");
      dojo.require("dijit.form.DateTextBox");
      dojo.require("dijit.form.Select");
      dojo.require("dijit.form.TextBox");
      dojo.require("dijit.form.Button");
      dojo.require("dijit.form.ComboBox");
    </script>

 <script type="dojo/method" data-dojo-event="onReset">
        return confirm('Press OK to reset widget values');
    </script>

    <script type="dojo/method" data-dojo-event="onSubmit">
        if(this.validate()){
            return confirm('Form is valid, press OK to submit');
        }else{
            alert('Form contains invalid data.  Please correct first');
            return false;
        }
        return true;
    </script>


</%block>

