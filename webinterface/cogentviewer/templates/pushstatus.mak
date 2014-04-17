<%inherit file="base.mak"/>

<%!
   _sideWidth = 0
   _mainWidth = 12 - _sideWidth
%>


<%block name="pageheader">
<h1>Push Status</h1>
</%block>


<%block name="pagecontent">

<p>
Details of each connected server and the last time they communicated with the central point
</p>

<form>
  <table class="table table-striped">
    <thead>
      <tr>
	<th>Hostname</th>
	<th>First Push</th>
	<th>Last Push</th>
	<th>Num Samples</th>
	<th>Skew</th>
	<th>Houses</th>

      </tr>
    </thead>
    <tbody>
      %for item in serverlist:
	<tr class='${item["rowcolor"]}'>
	  <td>${item["hostname"]}</td>
	  <td>${item["firstpush"]}</td>
	  <td>${item["lastpush"]}</td>
	  <td>${item["numsamps"]}</td>
	  <td>${item["skew"]}</td>
	  <td>${item["houses"]}</td>
	</tr>
      %endfor
    </tbody>
      
  </table>
  
</form>
</%block>
