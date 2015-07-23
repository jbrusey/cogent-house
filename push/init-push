#!/bin/bash

# actual send data script
/bin/echo "[`/bin/date`] START TRANSMISSION" >> /tmp/data-transfer.log

# use google DNS                                                                                                                    
/bin/echo "nameserver 8.8.8.8" > /etc/resolv.conf
/bin/echo "nameserver 8.8.4.4" >> /etc/resolv.conf

/usr/bin/python /opt/pulp/push/push-data.py -u http://cogentee.coventry.ac.uk/pulp/import.php -i /opt/pulp/data -o /opt/pulp/sent -t 5.0 -r 5 >> /tmp/data-transfer.log
/bin/echo "[`/bin/date`] END TRANSMISSION" >> /tmp/data-transfer.log

# truncate the log
/usr/bin/tail -n 1000 /tmp/data-transfer.log > /tmp/.data-transfer.log
/bin/mv /tmp/.data-transfer.log /tmp/data-transfer.log
