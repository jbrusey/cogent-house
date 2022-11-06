#!/bin/bash
#
# start serialforwarder
. /opt/tinyos-main/tinyos.sh
exec java net.tinyos.sf.SerialForwarder -comm serial@/dev/ttyUSB0:telosb -no-output
