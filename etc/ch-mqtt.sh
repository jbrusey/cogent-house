#!/bin/bash
#
# start mqttlogger
exec /usr/bin/python3 -m pulp.base.MqttLogger \
			   --log-level=debug\
			   --host=localhost\
			   --port=1883\
			   --topic=silicon\
			   --authpickle=/home/pi/mqtt.auth
