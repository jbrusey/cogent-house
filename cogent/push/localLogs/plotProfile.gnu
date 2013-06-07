set datafile sep ","



plot "profile.log" using 4 with linespoints title "Total Time" ,\
     "" using 5 with linespoints title "Tunnel",\
     "" using 6 with linespoints title "Remote",\
     "" using 7 with linespoints title "Node",\
     "" using 8 with linespoints title "Readings"
     


plot "reading_profile.log" using 4 with linespoints title "Total",\
     "" using 5 with linespoints title "URL",\
     "" using 6 with linespoints title "QRY",\
     "" using 7 with linespoints title "Add",\
     "" using 8 with linespoints title "Commit",\
     "" using 9 with linespoints title "Sync State"

     