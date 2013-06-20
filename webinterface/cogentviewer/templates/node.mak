<%inherit file="base.mak"/>

<%!
   _sideWidth = 0
   _mainWidth = 12 - _sideWidth
%>

<%block name="pageheader">
<h1>Node Details</h1>
</%block>

<%block name="pagecontent">

<% import time %>



    <h1>Details for Node ${nid}</h1>
    <section>
      <h2>Overview</h2>
      <ul>
	<li>Current Location: ${locDetails} </li>
	<li>Last Transmission: ${lastState} (GMT) </li>
	<li>Battery Level: ${batLevel} (Volts)</li>
      </ul>
    </section>

    <section>
      <h2>Sensors</h2>
      <table class="table table-hover table-bordered">
	<thead>
	  <tr>
	    <th>Sensor</th>
	    <th>Current Value</th>
	    ##<th><button>Last hour</button><button>Last day</button><button>Last week</button></th>
	    ##<th>Last Hour</th>
	    <th>
	      %for btn in btnList:
	      <a href="?duration=${btn[0]}" class="${btn[2]}">${btn[1]}</a>
	      ##${btn}
	      %endfor
	  </tr>
	</thead>
	<tbody>
	  %for row in allReadings:
	  <tr>
	    <td>${row[0]}</td>
	    <td>${row[1]}</td>
	    <td>
	      <img SRC="${row[2]}?time=${time.clock()}">
	    </td>
	  </tr>
	  %endfor

	<tbody>
      </table>

      <!-- And a few buttons to change the parameters -->
      <a href="?duration=hour" class="btn">Last Hour</a>
      <a href="?duration=day" class="btn">Last Day</a>
      <a href="?duration=week" class="btn">Last Week</a>
    </section>

    


</%block>
