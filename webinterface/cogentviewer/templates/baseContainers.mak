<!DOCTYPE html>  
<html lang="en">

<head>  
  <meta charset="utf-8">
  ##<link rel="stylesheet" href="${request.static_url('cogentviewer:static/normalize.css')}"/>

  <%block name="styles">

  </%block>


  ##Reset
  ##<link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dijit/themes/claro/document.css')}"/> 
  ##Main Claro Theme
  <link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dijit/themes/claro/claro.css')}"/>    

  ##<link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dijit/themes/claro/claro_rtl.css')}"/>

  <link rel="stylesheet" href="${request.static_url('cogentviewer:static/ccarc5.css')}" />

 <script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/dojo/dojo/dojo.js')}"
	 data-dojo-config="async:true, parseOnLoad:true, debug:true">
 </script>

 ##And Load the Relevant Dojo Layout Librarys
 <script>
   require([
   "dijit/layout/BorderContainer",
   "dijit/layout/ContentPane",
   "dijit/MenuBar",
   "dijit/MenuItem",
   "dijit/MenuBarItem",
   "dojo/parser",
   ]);

 <!--   function changePage(){ -->
 <!--       console.log("Click"); -->
 <!--   } -->
 </script>

 <!-- Javascripts -->
 <!-- And If I am using Anylitics, Then we can stick it here -->
 <%block name="scripts">
 </%block>

  <title>${pgTitle}</title>
</head>  


<body class="claro">


  <div dojoType="dijit.layout.BorderContainer" design="headline" persist="false" gutters="false"
    style="min-width: 1em; min-height: 1em; z-index: 0; width: 100%; height: 100%;">
  ##  <div>

    <div dojoType="dijit.layout.ContentPane" extractContent="false" preventCache="false" preload="false" refreshOnShow="false" region="top" splitter="false" doLayout="false" title="Title">
      ##<div>
      <h1>${pgTitle}</h1>

      <nav>
	<ul>
	  % for link in headLinks:
	  <li><a href="${link[1]}">${link[0]}</a></li>
	  % endfor
	</ul>
      </nav>

    </div> <!-- End Header Div -->

    ##Then we want the Main Page Content
    <div dojoType="dijit.layout.ContentPane" extractContent="false" preventCache="false" preload="false" refreshOnShow="false" region="center" splitter="true" doLayout="false" title="Main">

    ##<div>


      <%block name="pagecontent">
    
      </%block>
    </div>

    ##I I want to have a sidebar it could go here
    <%block name="othercontent">
    </%block>
    
    <div  class="footerPanel" dojoType="dijit.layout.ContentPane" region="bottom" splitter="false">
  ##<div  class="footerPanel">
	Cogent-Viewer 2012
    </div>
    
  </div><!-- End Border Container-->



</body>  
</html>  
