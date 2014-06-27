<!DOCTYPE html>

<html lang="en">

  <head>  
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">

    <!-- Meta Data -->
    <meta name="viewport" content="width=device-width">
    <meta name="description" content="Daily Automated Report">
    <meta name="author" content="Daniel Goldmith <djgoldsmith@googlemail.com>">
  </head>

  <body>
    <h1>${project}:  Daily Automated Report</h1>
    <h2>${date.date()}</h2>

    <h2 id="sec-1"><span class="section-number-2">1</span> Server and House Overview</h2>
    <div class="outline-text-2" id="text-1">
      <table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


	<colgroup>
	  <col  class="left" />
	  <col  class="right" />
	</colgroup>
	<thead>
	  <tr>
	    <th scope="col" class="left">&#xa0;</th>
	    <th scope="col" class="right">Number</th>
	  </tr>
	</thead>
	<tbody>
	  <tr>
	    <td class="left">Total Servers Deployed</td>
	    <td class="right">${deployed_serv}</td>

	  </tr>

	  <tr>
	    <td class="left">Number of Houses</td>
	    <td class="right">${deployed_houses}</td>
	  </tr>

	  <tr>
	    <td class="left">Total Number of Nodes Deployed</td>
	    <td class="right">${deployed_nodes}</td>
	  </tr>

	  <tr>
	    <td class="left">Servers that have pushed today</td>
	    <td class="right">${push_today}</td>
	  </tr>
	</tbody>
      </table>
    </div>
</div>

<div id="outline-container-sec-2" class="outline-2">
  <h2 id="sec-2"><span class="section-number-2">2</span> Push / Server Status</h2>
  <div class="outline-text-2" id="text-2">
    <table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


      <colgroup>
	<col  class="left" />

	<col  class="right" />

	<col  class="right" />
      </colgroup>
      <thead>
	<tr>
	  <th scope="col" class="left">&#xa0;</th>
	  <th scope="col" class="right">Number</th>
	  <th scope="col" class="right">Percentage</th>
	</tr>
      </thead>
      <tbody>
	<tr>
	  <td class="left">Deployed servers that Have pushed this week</td>
	  <td class="right">${push_week}</td>
	  <td class="right">${"{0:.2f}".format(float(push_week) / (float(deployed_serv)) * 100)}%</td>
	</tr>

	<tr>
	  <td class="left">Deployed Servers that have pushed today</td>
	  <td class="right">${push_today}</td>
	  <td class="right">${"{0:.2f}".format((float(push_today) / deployed_serv) * 100)}%</td>
	</tr>
	<tr>
	  <td class="left">Houses with data in the Past 24 hours</td>
	  <td class="right">${houses_today}</td>
	  <td class="right">${"{0:.2f}".format((float(houses_today) / deployed_houses) * 100)}%</td>
	</tr>
      </tbody>
    </table>
  </div>
</div>




<div id="outline-container-sec-3" class="outline-2">
  <h2 id="sec-3"><span class="section-number-2">3</span> Houses with problems:</h2>
  <ul>
    	%for house in houses_missing:
	  <li>${house}</li>
	%endfor
  </ul>


<div id="outline-container-sec-4" class="outline-2">
  <h2 id="sec-4"><span class="section-number-2">4</span> Node Status</h2>
  <div class="outline-text-2" id="text-4">
    <table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


      <colgroup>
	<col  class="left" />

	<col  class="right" />

	<col  class="right" />
      </colgroup>
      <thead>
	<tr>
	  <th scope="col" class="left">&#xa0;</th>
	  <th scope="col" class="right">Number</th>
	  <th scope="col" class="right">Percentage</th>
	</tr>
      </thead>
      <tbody>
	<tr>
	  <td class="left">Total Nodes in last Week</td>
	  <td class="right">${node_week}</td>
	  <td class="right">${"{0:.2f}".format((float(node_week) / deployed_nodes) * 100)}%</td>
	</tr>

	<tr>
	  <td class="left">Total Nodes In last 24 Hours</td>
	  <td class="right">${node_today}</td>
	  <td class="right">${"{0:.2f}".format((float(node_today) / deployed_nodes) * 100)}%</td>
	</tr>


      </tbody>
    </table>

  </div>
</div>

<div id="outline-container-sec-5" class="outline-2">
  <h2 id="sec-5"><span class="section-number-2">5</span> Pulse Nodes where a Given Sensing Type has not changed in the past day</h2>
  <div class="outline-text-2" id="text-5">
    <ul>
      %for node in pulse_warnings:
      <li>${node}</li>
      %endfor
    </ul>
  </div>
</div>
</div>

<div id="postamble" class="status">
  <p class="author">Author: Daniel Goldsmith</p>
</div>

</body>

</html>
