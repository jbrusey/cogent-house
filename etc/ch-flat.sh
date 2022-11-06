#!/bin/bash
#
# start flatlogger
# Modification history:
# 1. 4/2/2020 jpb add sleep of 10 seconds to ensure ch-sf is up
sleep 10
. /opt/tinyos-main/tinyos.sh
exec python -m pulp.base.FlatLogger \
	--log-level debug\
	-t /tmp/ -o /opt/pulp/data -d 600.0 -f /var/log/ch/FlatLogger.log
