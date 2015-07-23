#!/bin/bash

#We don't have 3G for pulp yet, sow e assume we have an internet connection

/bin/echo "[`/bin/date`] START SCRIPT" >> /tmp/data-transfer.log

# switch on 3g and wait for the connection to start
#/opt/BioSense/scripts/gpio-device.sh $GPIO on
#/bin/sleep 10
#/sbin/ifup ppp0 # start connection - wvdial will be called when this interface is brought up
#/bin/sleep 30 # could be longer..

# use google DNS
/bin/echo "nameserver 8.8.8.8" > /etc/resolv.conf
/bin/echo "nameserver 8.8.4.4" >> /etc/resolv.conf

# actual send data script
/bin/echo "[`/bin/date`] START TRANSMISSION" >> /tmp/data-transfer.log

/usr/bin/python /opt/pulp/push/push-data.py -u http://pulp.coventry.ac.uk/import.php -i /opt/pulp/data -o /opt/pulp/sent -t 5.0 -r 5 >> /tmp/data-transfer.log
/bin/echo "[`/bin/date`] END TRANSMISSION" >> /tmp/data-transfer.log

# switch off 3g
#/sbin/ifdown ppp0
#/bin/sleep 10 # wait for wvdial to get rid off connection
#/opt/BioSense/scripts/gpio-device.sh $GPIO off

/bin/echo "[`/bin/date`] END SCRIPT" >> /tmp/data-transfer.log

# truncate the log
/usr/bin/tail -n 1000 /tmp/data-transfer.log > /tmp/.data-transfer.log
/bin/mv /tmp/.data-transfer.log /tmp/data-transfer.log
