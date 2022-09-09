#!/bin/bash
#
# start flatlogger
. /opt/tinyos-main/tinyos.sh
exec python -m pulp.base.FlatLogger -t /tmp/ -o /opt/pulp/data -d 600.0 -f /var/log/ch/FlatLogger.log
