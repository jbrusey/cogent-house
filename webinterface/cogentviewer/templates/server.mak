<%inherit file="base.mak"/>

<%!
   _sideWidth = 0
   _mainWidth = 12 - _sideWidth
%>

<%block name="styles">
<style>
.table tbody tr > td.success {
  background-color: #dff0d8 !important;
}

.table tbody tr > td.error {
  background-color: #f2dede !important;
}

.table tbody tr > td.warning {
  background-color: #fcf8e3 !important;
}

.table tbody tr > td.info {
  background-color: #d9edf7 !important;
}

.table-hover tbody tr:hover > td.success {
  background-color: #d0e9c6 !important;
}

.table-hover tbody tr:hover > td.error {
  background-color: #ebcccc !important;
}

.table-hover tbody tr:hover > td.warning {
  background-color: #faf2cc !important;
}

.table-hover tbody tr:hover > td.info {
  background-color: #c4e3f3 !important;
}
</style>
</%block>

<%block name="pageheader">
<h1>Node Details</h1>
</%block>

<%block name="pagecontent">
    <section>
    <h1>Server Status</h1>


      <table class="table table-hover table-bordered">
	<thead>
	  <tr>
	    <th>Server</th>
	    <th>Base Id</th>
	    <th>Address</th>
	    <th>Last Push</th>
	    <td>Local Time</th>
	    <th>Last Reading</th>
	  </tr>
	</thead>
	<tbody>
	  %for row in servertable:
	  ##<tr class=${row["state_state"]}>
	    <tr>
	    <td>${row["servername"]}</td>
	    <td>${row["baseid"]}</td>
	    <td>${row["address"]}</td>
	    <td class=${row["push_state"]}>${row["lastpush"]}</td>
	    <td class=${row["local_state"]}>${row["localtime"]}</td>
	    <td class=${row["state_state"]}>${row["laststate"]}</td>
	  </tr>
	  
	  %endfor
	</tbody>
      </table>
    </section>

    <h2>Node Status</h2>
    <table class="table table-hover table-bordered">
      <thead>
	<tr>
	  <th>Server</th>
	  <th>Base Id</th>
	  <th>House</th>
	  <th>Nodes</th>
	</tr>
	<tr>
	  <th></th>
	  <th></th>
	  <th></th>
	  <th>Node Id</th>
	  <th>Parent</th>
	  <th>Last Tx</th>
	  <th>RSSI</th>
	  <th>Count</th>
	</tr>
      </thead>

      <tbody>
	%for server in serverlist:
	<tr>
	  <td>${server["server"]}</td>
	  <td>${server["baseid"]}</td>
	  <td>${server["house"]}</td>
	</tr>
	    %if server["nodes"]:
 	        %for node in server["nodes"]:
	        <tr>
		  <td></td>
		  <td></td>
		  <td></td>
		  <td>${node[1]}</td>
		  <td>${node[0]}</td>
		  <td>${node[2]}</td>
		  <td>${node[3]}</td>
		  <td>${node[4]}</td>		   
		</tr>
    		%endfor

	    %endif
	%endfor
      </tbody>


    </table>
 
</%block>
