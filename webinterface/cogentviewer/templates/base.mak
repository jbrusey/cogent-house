<!-- Update to the Bootstrap style -->

<%!
   _sideWidth = 0
   _mainWidth = 12 - _sideWidth
%>


<!DOCTYPE html>  
<!-- <html lang="en"> RM New Style-->

<!--[if lt IE 7]>      <html class="no-js lt-ie9 lt-ie8 lt-ie7" lang=en> <![endif]-->
<!--[if IE 7]>         <html class="no-js lt-ie9 lt-ie8" lang=en> <![endif]-->
<!--[if IE 8]>         <html class="no-js lt-ie9" lang=en> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js" lang=en> <!--<![endif]-->

<head>  
  <meta charset="utf-8">
  <!-- Meta Data -->
  <meta name="description" content="">
  <meta name="viewport" content="width=device-width">
  <meta name="description" content="">
  <meta name="author" content="Daniel Goldmith <djgoldsmith@googlemail.com>">

  ##Main Claro Theme
  <link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dijit/themes/claro/claro.css')}"/>

  <!-- Styleshets added for Bootstrap -->
  <!-- Styles from the LESS source -->
  <link rel="stylesheet/less" href="${request.static_url('cogentviewer:static/less/bootstrap.less')}">
  <link rel="stylesheet/less" href="${request.static_url('cogentviewer:static/less/responsive.less')}">

  <link rel="stylesheet" href="${request.static_url('cogentviewer:static/css/treeicons.css')}"></link>
  <!-- Script to parse the Less -->
  <script src="${request.static_url('cogentviewer:static/js/vendor/less-1.3.1.min.js')}"></script>

  <!-- Overwrite a bit of the style to get the width correct -->
  <style>
    body {
    padding-top: 60px;
    padding-bottom: 40px;
    }

    .scroll-nav{
    height:400px;
    /*height: 100%;*/
    overflow: scroll;
    }    
  </style>

  <!-- User Specified Styles (such as Dojo ones -->
  <%block name="styles">
  </%block>

 <!-- Modernizer -->
 <script src="${request.static_url('cogentviewer:static/js/vendor/modernizr-2.6.1-respond-1.1.0.min.js')}"> </script>

  <title>${pgTitle}</title>

##Configure First
<script>
  dojoConfig = {
      packages: [{
           name: 'dbootstrap',
           location: "${request.static_url('cogentviewer:jslibs/dbootstrap/')}",
           }],
      has: {
           "dojo-firebug":true,
           "dojo-debug-messages":true,
           },

      parseOnLoad: false,
      async: true,
      };
  
</script>

<script type="text/javascript" src="${request.static_url('cogentviewer:jslibs/dojo/dojo/dojo.js')}">
</script>

## Load dbootstrap
<script>
//require(['dbootstrap'], function(dbootstrap) {
//    // Start application.
//});
</script>


</head>  


<body class="claro">
  <!--[if lt IE 7]>
      <p class="chromeframe">You are using an outdated browser. <a href="http://browsehappy.com/">Upgrade your browser today</a> or <a href="http://www.google.com/chromeframe/?redirect=true">install Google Chrome Frame</a> to better experience this site.</p>
      <![endif]-->

  <!-- This code is taken from http://twitter.github.com/bootstrap/examples/hero.html -->

  <!-- Navigation Stuff -->
  <div class="navbar navbar-fixed-top">
    <div class="navbar-inner">
      <div class="container-fluid">
	<a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
        </a>
	
        <a class="brand" href="/">Cogent Viewer</a>
	      
	<div class="nav-collapse collapse">
	  <ul class="nav">
	    % for link in headLinks:
	        <li><a href="${link[1]}">${link[0]}</a></li>
            % endfor
          </ul>
	  
	  <p class="navbar-text pull-right">
	    %if user:
	        Logged in as: ${user} / <a href="${request.route_url('logout')}">Logout</a>
	    %else:
	        <a href="${request.route_url('login')}">Login</a>
	    %endif
	  </p>

	</div><!--/.nav-collapse -->

      </div> <!-- Container -->
    </div> <!-- Nav Inner -->
  </div> <!-- Nav Fixed -->

  <!-- Main Page Contents -->
  <div class="container-fluid">
    
    <!-- Main hero unit for a primary marketing message or call to action -->
    <div class="hero-unit hidden-phone">
      <%block name="pageheader"></%block>
    </div>

    <div class="page-header visable-phone">
      <%block name="phoneheader"></%block>	      
    </div>

    <!-- If we want anything aboue the two column layout -->
    <%block name="bodyheader"></%block>

    <!-- Example row of columns -->
    <div class="row-fluid">
      %if self.attr._sideWidth > 0:
          <div class="span${self.attr._sideWidth}">
            <%block name="sidenav"></%block>
          </div>
       %endif

<div class="span${self.attr._mainWidth}">
  <%block name="pagecontent">
</%block>
</div>
</div> <!-- End of Row Containter -->

<hr>

<footer>
  <p>Cogent-Viewer -  &copy; djgoldsmith 2013</p>
</footer>

</div> <!-- /container -->


<!-- Javascripts -->
<script src="${request.static_url('cogentviewer:static/js/vendor/jquery-1.8.2.min.js')}"></script>
<script src="${request.static_url('cogentviewer:static/js/vendor/bootstrap.min.js')}"></script>

##LOAD DOJO CONFIG

##LOAD DOJO
##New Way of loading / configuring dojo





##General Page Scripts
<%block name="scripts">
</%block>


<!-- And If I am using Anylitics, Then we can stick it here -->

</body>  
</html>  
