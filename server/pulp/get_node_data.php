<?php
// read node files and put last json in dicts..
foreach (glob("/tmp/node_*.log") as $filename) {
  $lines = file($filename);
  foreach ($lines as $line_num => $line) {
    echo $line."\n";
  }
}
?>

