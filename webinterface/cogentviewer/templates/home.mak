<%inherit file="base.mak"/>

<%block name="pagecontent">
     <section>  
       <h1>Homepage</h1>
	<p>Welcome to the CogentHouse Maintenance Portal</p>
	<p>This portal can be used to monitor your deployed CogentHouse sensors and to view graphs of all recorded data.</p>
    </section>  

     
     <section>
       <h2>Add / Edit Active Deployments</h2>

       The table below lists any deployments that are still active on the system.  
       To edit an active deployment use the edit link.

       Otherwise to start a new deployment click here:
       <form method="LINK" action="${newLink}">
	 <input type="submit" value="Add New House"></input>
       </form>
     </section>

     <section>
     <h2>Active Deployments</h2>

     <table border=1px solid width=90%>
       <tr>
	 <th>Id</th>
	 <th>Address</th>
	 <th>Deployment Group</th>
	 <th>Start Date</th>
	 <th>End Date</th>
	 <th>Edit</th>
       </tr>
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
     </table>
     </section>

<div id="theGrid">
  
</div>

</%block>  

<%block name="scripts">
    <!-- <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/home.js')}"></script> -->

</%block>
