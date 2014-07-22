##<%inherit file="baseContainers.mak"/>
<%inherit file="base.mak"/>

<%!
   _sideWidth = 0
   _mainWidth = 12 - _sideWidth
%>


<%block name="styles">
</%block>


<%block name="pageheader">
   <h1>Export Data</h1>
</%block>

<%block name="bodyheader">
  <!-- Add the container for the Controls-->
 

</%block>

##Main Page Content
<%block name="pagecontent">
   
  <section>
    <h3>Select Data</h3>
    %if warnings:
       <div class="alert alert-error">${warnings}</div>
    %endif

    <form method="POST" action="" accept-charset="UTF-8">
      <div class="form-horizontal">
	<div class="control-group">
    	  <label class="control-label" for="House">House</label>
    	  <div class="controls">
    	    <select id="House" name="houseId" required="true"></select>
    	  </div>
	</div>

	<div class="control-group">    	
    	  <label class="control-label" for="allrooms">Rooms</label>
	  <div class="controls">
	    <label class="checkbox inline">
	      <input type="checkbox" id="allrooms-all" name="allrooms" checked> All
	    </label>

	    <!-- <label class="radio inline"> -->
	    <!--   <input type="radio" id="allrooms-all" name="allrooms" value="allrooms-all" checked>All -->
	    <!-- </label> -->
	    <!-- <label class="radio inline"> -->
	    <!--   <input type="radio" id="allrooms-select" name="allrooms" value="allrooms-select">Select Rooms -->
	    <!-- </label> -->	      
	    <div id="roomGroup">
	      <!-- Open Area to add rooms -->
	    </div>
	  </div>
	</div>

	<div class="control-group">
	  <label class="control-label" for="sensors">Sensor Types</label>
	  <div class="controls">
	    <label class="checkbox inline">
	      <input type="checkbox" id="chk_temperature" name="stype" value="Temperature" checked>Temperature
	    </label>
	    <label class="checkbox inline">
	      <input type="checkbox" id="chk_humidity" name="stype" value="Humidity" checked> Humidity
	    </label>
	    <label class="checkbox inline">
	      <input type="checkbox" id="chk_co2" name="stype" value="CO2">Co2
	    </label>
	    <label class="checkbox inline">
	      <input type="checkbox" id="chk_voc" name="stype" value="VOC">VOC
	    </label>
	    <label class="checkbox inline">
	      <input type="checkbox" id="chk_electricity" name="stype" value="Power">Electricity (CC)
	    </label>
	    <label class="checkbox inline">
	      <input type="checkbox" id="chk_gas" name="stype" value="Gas Pulse Count">Gas Pulse
	    </label>
	    <!-- <label class="checkbox inline"> -->
	    <!--   <input type="checkbox" id="chk_electricity_watts" name="stype" value="Power_kw">Electricity (kWh) -->
	    <!-- </label> -->
	    <label class="checkbox inline">
	      <input type="checkbox" id="chk_battery" name="stype" value="Battery Voltage">Battery
	    </label>
	  </div> <!-- End of Controls -->
	</div> <!-- End of Group -->

      <div class="control-group">
	<label class="control-label" for="startdate">Start Date</label>
	<div class="controls">
	  <input type="datetime" id="startdate" name="startdate" placeholder="DD-MM-YYYY">
	</div>
      </div>

      <div class="control-group">
	<label class="control-label" for="stopdate">Stop Date</label>
	<div class="controls">
	  <input type="datetime" id="stopdate" name="stopdate" placeholder="DD-MM-YYYY">
	</div>
      </div>
      

	  

      </div> <!-- End  Horizontal form -->

	  

      <h3>Filter and Aggregate</h3>

      <div class="form-horizontal">
	<div class="control-group">
	  <label class="control-label" for="aggregate">Summarise</label>
	  <div class="controls">
	    <label class="radio inline">
	      <input type="radio" name="aggregate" id="aggregate-none" value="aggregate-none" checked>
	      Raw Data
	    </label>
	    <label class="radio inline">
	      <input type="radio" name="aggregate" id="aggregate-none" value="aggregate5">
	      Normalised 5 Minute
	    </label>
	    <label class="radio inline">
	      <input type="radio" name="aggregate" id="aggregate15" value="aggregate15">15 min summary
	    </label>
	    <label class="radio inline">
	      <input type="radio" name="aggregate" id="aggregate30" value="aggregate30">30 min summary
	    </label>
	    <label class="radio inline">
	      <input type="radio" name="aggregate" id="aggregatehour" value="aggregateHour">Hourly summary
	    </label>
	    <label class="radio inline">
	      <input type="radio" name="aggregate" id="aggregatehour" value="aggregateDaily">Daily summary
	    </label>
	  </div>
	</div> <!-- Control Group -->

	<div class="control-group">
	  <label class="control-label" for="aggstats">Aggregate Stats</label>
	  <div class="controls">
	    <label class="checkbox inline">
	      <input type="checkbox" name="agg-param" id="agg-mean" value="mean" checked>Mean
	    </label>
	    <label class="checkbox inline">
	      <input type="checkbox" name="agg-param" id="agg-min" value="min">Min
	    </label>
	    <label class="checkbox inline">
	      <input type="checkbox" name="agg-param" id="agg-max" value="max">Max
	    </label>
	    <label class="checkbox inline">
	      <input type="checkbox" name="agg-param" id="agg-sum" value="sum">Sum
	    </label>
	  </div>
	</div> <!-- Control Group -->

	<div class="control-group">
	  <label class="control-label" for="interp">Interpolate Missing Values</label>
	  <div class="controls">
	    <input type="checkbox" name="interp" id="interp">
	  </div>
	</div>
	<!-- <div class="control-group"> -->
	<!--   <label class="control-label" for="calibrate">Calibrate</label> -->
	<!--   <div class="controls"> -->
	<!--     <label class="radio inline"> -->
	<!--       <input type="radio" name="calibrate" id="calib-yes" value="calib-yes" checked> -->
	<!--       Yes -->
	<!--     </label> -->
	<!--     <label class="radio inline"> -->
	<!--       <input type="radio" name="calibrate" id="calib-no" value="calib-no"> -->
	<!--       No -->
	<!--     </label> -->
	<!--   </div> -->
	<!-- </div> <\!-- Group -\-> -->

      </div> <!-- Form -->
    
      <div class="form-inline">
	<button id="getData" class="btn btn-primary" name="submit">Get Data</button>
	<button id="clearData" class="btn" name="reset">Clear Selection</button>
      </div>
    </form>

    %if hasDl:
        <div class="alert alert-info">
	  Data is ready for download
	</div>
    %endif

  </section>
  
</%block>  


##And Our Navigation Block
<%block name="sidenav">
    <!-- <h3>Select Data</h3> -->
    <!-- <div class="scroll-nav"> -->
    <!--   <aside class="claro"> -->
    <!-- 	<div id="treeNode"></div>   -->
    <!--   </aside> -->
    <!-- </div> -->
</%block>




<!-- Javascript Stuff -->

<%block name="scripts">
  ##Dojo Now Comes from Base File

  <!-- <script type="text/javascript">treeLimit = "temperature"</script> -->
  <!-- <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/chartingTree.js')}"></script> -->
  <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/export.js')}"></script>

</%block>

