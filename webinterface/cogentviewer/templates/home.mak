<%inherit file="base.mak"/>

<%!
   _sideWidth = 0
   _mainWidth = 12 - _sideWidth
%>


<%block name="pageheader">
<h1>Homepage</h1>
</%block>


<%block name="pagecontent">

     <section>
       <p>Welcome to the CogentHouse Maintenance Portal </br>
	 This portal can be used to monitor your deployed CogentHouse sensors and to view graphs of all recorded data.</p>
     </section>
     
     <hr>
     <section>
       <h2>Currently Active Deployments</h2>

       The table below lists any deployments that are still active on the system.  
       To edit an active deployment use the edit link.
     
       <table class="table table-hover table-bordered">
	 <thead>
	   <tr>
	     <th>Id</th>
	     <th>Address</th>
	     <th>Deployment Group</th>
	     <th>Start Date</th>
	     <th>End Date</th>
	     <th>Edit</th>
	   </tr>
	 </thead>
	 
	 <tbody>	 
	   %for house,url in activeHouses:
	   <tr>
	     <td>${house.id}</td>
	     <td>${house.address}</td>
	     %if house.deployment:
	     <td>${house.deployment.name}</td>
	     %else:
	     <td>&nbsp;</td>
	     %endif
	     <td>${house.startDate}</td>
	     <td>${house.endDate}</td>
	     <td><a href=${url}>Edit</a></td>
	   </tr>
	   %endfor
	 </tbody>
       </table>
     </section>

     <a class="btn" href="${newLink}">Start New Deployment</a>

     <hr>
     <section>
       <h2>Node Status</h2>
       
       <h3>Recently Heard Nodes</h3>
       <table class="table table-hover table-bordered">
	 <thead>
	   <tr>
	     <th>NodeId</th>
	     <th>Last TX (Local Time)</th>
	     <th>Battery Level</th>
	     <th>Deployment</th>
	     <th>Show Node</th>
	   </tr>
	 </thead>
	 <tbody>
	   %for row in nodeStates:
	   <tr class="${row[0]}">
	     <td>${row[1]}</td> <!--node-->
	     <td>${row[2]}</td> <!--Tx (Local)-->
	     <td><p class=${row[3]}>${row[4]}</p></td> <!--Batt-->
	     <td>${row[5]}</td> <!--Depoyment-->
	     <td><a href="${request.route_url('node',id=row[1])}">Node Details,</a></td> <!--Link-->
	   </tr>
	   %endfor
	 </tbody>
       </table>
     </section>

     <section>
       <h3>Missing Nodes</h3>
       <table class="table table-hover table-bordered">
	 <thead>
	   <tr>
	     <th>NodeId</th>
	     <th>Last TX (Local Time)</th>
	     <th>Battery Level</th>
	     <th>Deployment</th>
	     <th>Show Node</th>
	   </tr>
	 </thead>
	 <tbody>
	   %for row in missingNodes:
	   <tr class="${row[0]}">
	     <td>${row[1]}</td> <!--node-->
	     <td>${row[2]}</td> <!--Tx (Local)-->
	     <td><p class=${row[3]}>${row[4]}</p></td> <!--Batt-->
	     <td>${row[5]}</td> <!--Depoyment-->
	     <td><a href="${request.route_url('node',id=row[1])}">Node Details,</a></td> <!--Link-->
	   </tr>
	   %endfor
	 </tbody>
       </table>
     </section>
</%block>  

<%block name="scripts">
    
</%block>
