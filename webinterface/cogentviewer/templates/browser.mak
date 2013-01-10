<%inherit file="base.mak"/>

<%block name="styles">

<link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dojox/grid/resources/Grid.css')}"/>
<link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dojox/grid/resources/claroGrid.css')}"/>

<style>
  .field-bool {
      width:4em;
  }
</style>
</%block>


<%block name="pagecontent">
<h2>Data Selection</h2>

<div id="gridNode"></div>
<!-- We Want Two Sections, Upper section selects nodes, lower actually displays the information -->

<h2>Data Summary</h2>
<div id="dataNode"></div>

</%block>


<%block name="scripts">
        <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/browserNav.js')}"></script>
</%block>

