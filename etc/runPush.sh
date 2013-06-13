#!/bin/bash

# Wrapper script for RestPusher - attempts to push the data for half-hour includes checks on 3g connectivity
SIP="8.8.8.8"
TIMEOUT=30
COUNT=1
while [ $COUNT -lt $TIMEOUT ]
do
    let COUNT++
    #PING_RES=$(ping -I ppp0 -c 1 $SIP | grep "bytes from" | wc -l)
    #if [ $PING_RES -eq 1 ]
    if ping -I ppp0 -q -c 1 $SIP >/dev/null
    then
	cd /opt/cogent-house.clustered/cogent/push && python RestPusher.py
	break #SUCESSS
    else
	sudo service 3g-connection start
    fi
    sleep 10
done

