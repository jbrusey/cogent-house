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
       <H2>Active Houses</H2>

       <table class="table table-striped">
	 <thead>
	   <tr>
	     <th>Server Id</th>
	     <th>Address</th>
	     <th>Registered Nodes</th>
	     <th>Nodes Reporting today</th>
	     <th>Nodes Reporting in last Week</th>
	     <th>Last Reading</th>
	     <th>Last Server Msg</th>
	     <th>Average Yield (this week)</th>
	     <th>Minimum Yield (this week)</th>
	     <th></th>
	   </tr>
	 </thead>
	 <tbody>
	   %for house in activehouses:
	   <tr class=${house['rowstate']}>
	     <td>${house["hostname"]}</td>
	     <td>${house["address"]}</td>
	     <td>${house["numnodes"]}</td>
	     <td>${house["activenodes"]}</td>
	     <td>${house["weeknodes"]}</td>
	     <td>${house["lastreading"]}</td>
	     <td>${house["lastpush"]}</td>
	     <td>${"{0:.2f}".format(house["avgyield"])}%</td>
	     <td>${"{0:.2f}".format(house["minyield"])}%</td>
	     <td><a href=${request.route_url('housedetail',id=house["id"])}>View Details</a></td>
	   </tr>
	   %endfor
	   
	 </tbody>
       </table>
     </section>
</%block>
