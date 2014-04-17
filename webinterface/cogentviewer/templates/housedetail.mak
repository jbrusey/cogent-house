<%inherit file="base.mak"/>

<%!
   _sideWidth = 0
   _mainWidth = 12 - _sideWidth
%>


<%block name="pageheader">
<h1>${thehouse.address} Details</h1>
</%block>


<%block name="pagecontent">

     <section>
       <h2>General for House ${thehouse.address}</h2>
       
       <dl class="dl-horizontal">
	 <dt>Server Id</dt>
	 <dd>${servername}</dd>
	 <dt>Last Push</dt>
	 <dd>${lastpush}</dd>
	 <dt>Skew</dt>
	 <dd>${skew}</dd>
	 <dt>Registered Nodes</dt>
	 <dd>${nodecount}</dd>
       </dl>
     </section>

     <section> 
       <h2>Node Details</h2>
       <table class="table table-bordered table-striped">
	 <thead>
	   <tr>
	     <th>NodeId</th>
	     <th>Location</th>
	     <th>Last Reading</th>
	     <th>Last NodeState</th>
	     <th>Voltage</th>
	     <th>Yield (Last 7 days)</th>
	     <th>SIP Compression</th>
	     <th>Resets</th>
	   </tr>
	 </thead>
	 <tbody>
	   %for node in nodedetails:
	     <tr>
	       <td>${node["id"]}</td> 
	       <td>${node["location"]}</td> 
	       <td>${node["lastreading"]}</td> 
	       <td>${node["laststate"]}</td> 
	       <td>${"{0:.2f}".format(node["voltage"])}</td>
	       <td>${"{0:.2f}".format(node["yield"])}</td> 
	       <td>${"{0:.2f}".format(node["compression"])}</td> 
	       <td>${node["resets"]}</td> 
	     </tr>
	   %endfor
	 </tbody>
       </table>
     </section>

     <section>
       <%doc>
     <h2>Graphing</h2>
     <div id="thegraph" style="width:640">
     </div>
     </%doc>
     </section>


<%doc>       
<%block name="scripts">
  <script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/Highstock/js/highstock.js')}"></script>	
  <script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/Highstock/js/themes/grid.js')}"></script>

  <script type="text/javascript">
    theurl = '${request.route_url("newgraphs")}';
    hostname = '${servername}';
    nodepairs = ${nodepairs};
  </script>

  <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/housedetail.js')}">
  </script>
</%block>
</%doc>

</%block>
