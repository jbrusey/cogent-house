<!DOCTYPE html>
<meta charset="utf-8">
<html>
<head>
    <style>
      rect.bordered {
        stroke: #E6E6E6;
        stroke-width:2px;   
      }

      text.mono {
        font-size: 9pt;
        font-family: Consolas, courier;
        fill: #aaa;
      }

      text.axis-workweek {
        fill: #000;
      }

      text.axis-worktime {
        fill: #000;
      }

      .wrapper {
          width: 1024px;
          height: 786px;
          overflow: auto;
      }
         

    </style>

    <script src="http://d3js.org/d3.v3.js"></script>
    <script src="http://d3js.org/colorbrewer.v1.min.js"></script>
  </head>
  <body>
    <div class="wrapper">
      <div id="chart"></div>
    </div>
    <script type="text/javascript" src="${request.static_url('cogentviewer:static/scripts/heatmap.js')}">
    </script>
  </body>
</html>
