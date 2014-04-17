<!DOCTYPE html>
<head>
  <meta charset="utf-8">
  
  <style>
    .wrapper {
      width: 1024px;
      height: 150px;
      overflow: auto;
    }
  </style>
</head>


<body>
  <h1>Network Viz:  Generated at ${time}</h1>
  
    <div id="vis"></div>
  
  <div class="wrapper">
    <div id="timeline"></div>
  </div>
  

  <script src="http://code.jquery.com/jquery-1.11.0.min.js"></script>
  <script type="text/javascript" src="http://d3js.org/d3.v3.js"></script>
  <script type="text/javascript" src="http://d3js.org/colorbrewer.v1.min.js"></script>
  <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/newnet.js')}">
</body>

</html>
