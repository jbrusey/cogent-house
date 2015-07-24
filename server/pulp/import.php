<?php

$filefullname = basename($_FILES['userfile']['name']);
$file_to_copy = $_FILES['userfile']['tmp_name'];
$uploadfile = "/home/ross/pulp/".$filefullname;

/* attempt to copy the file and return success to the node */
if (copy($file_to_copy, $uploadfile)) {
  /* success, send checksum back to node */
  #echo "checksum:".md5_file($_FILES['userfile']['tmp_name']).":".$filefullname.":".$_FILES['userfile']['tmp_name'];
  echo "checksum:".md5_file($uploadfile).":".$filefullname.":";
} 
else { 
  echo "\nUpload failed\n";
}


