#################################################
# MqttLogger                                    #
#                                               #
# Extends FlatLogger to also send mqtt messages #
#                                               #
# J. Brusey, September 2022                     #
#################################################

"""MqttLogger - cogent-house data logging to MQTT

Receives sensor readings from the base station and logs them using
paho mqtt publish messages.

This sits on top of FlatLogger so that it works in addition to the
logging to file.

The acknowledgement is made to be only dependent on FlatLogger and
should not be held up by delays in sending MQTT messages.

"""

import logging
import math
from optparse import OptionParser

import paho.mqtt.client as mqtt

if __name__ == "__main__" and __package__ is None:
    __package__ = "pulp.base"

from .FlatLogger import FlatLogger
from .packstate import PackState

LOGGER = logging.getLogger(__name__)


def on_connect(client, userdata, flags, rc):
    """The callback for when the client receives a CONNACK response
    from the server."""
    LOGGER.debug(f"Connected with result code {rc}")


class MqttLogger(FlatLogger):
    """Extension to FlatLogger to also log messages to mqtt"""

    def __init__(
        self,
        bif=None,
        tmp_dir=".",
        duration=900,
        out_dir=".",
        topic="",
        mqtthost="localhost",
        mqttport=1883,
        mqttkeepalive=60,
        username=None,
        password=None,
    ):
        super().__init__(bif, tmp_dir, duration, out_dir)
        self.topic = topic
        self.client = mqtt.Client()
        self.client.on_connect = on_connect
        if username:
            self.client.username_pw_set(username, password=password)
        self.client.connect(host=mqtthost, port=mqttport, keepalive=mqttkeepalive)
        # background async loop
        self.client.loop_start()

    def publish(self, sender=None, type_id=None, value=None):
        self.client.publish(f"{self.topic}/{sender}/{type_id}", value)

    def store_state(self, msg):
        status = super().store_state(msg)

        pack_state = PackState.from_message(msg)

        for type_id, value in pack_state.d.items():
            if math.isinf(value) or math.isnan(value):
                value = None

            if value is not None:
                self.publish(sender=msg.getAddr(), type_id=type_id, value=value)
        return status

    def test_connection(self):
        self.client.publish(f"{self.topic}/test", 1)


def main():
    command_line_arguments = OptionParser()

    command_line_arguments.add_option(
        "-o",
        "--out-dir",
        metavar="DIR",
        default=".",
        help="Output directory for files (default .)",
    )
    command_line_arguments.add_option(
        "--tmp-dir",
        metavar="DIR",
        default=".",
        help="Temporary directory for files (default .)",
    )
    command_line_arguments.add_option(
        "-d",
        "--duration",
        metavar="SEC",
        default=900,
        help="Number of seconds between files (default 900)",
    )
    command_line_arguments.add_option(
        "-l",
        "--log-level",
        default="info",
        metavar="LEVEL",
        help="Set log level to LEVEL: debug,info,warning,error",
    )
    command_line_arguments.add_option(
        "-f",
        "--log-file",
        default="/var/log/ch/MqttLogger.log",
        help="Log file to use (Default ./Mqttlogger.log",
    )

    # mqtt arguments
    command_line_arguments.add_option(
        "-h",
        "--host",
        default="localhost",
        help="Host for logging mqtt messages (default: localhost)",
    )
    command_line_arguments.add_option(
        "-p",
        "--port",
        default=1883,
        help="Port number for mqtt logging (default: 1883)",
    )
    command_line_arguments.add_option(
        "--keepalive",
        default=60,
        help="Keepalive time (default: 60)",
    )
    command_line_arguments.add_option(
        "-u", "--username", default=None, help="Username for mqtt"
    )
    command_line_arguments.add_option(
        "-P", "--password", default=None, help="Password for mqtt"
    )

    command_line_arguments.add_option(
        "-t",
        "--topic",
        default="null",
        help="Topic for logging mqtt messages (default: null)",
    )

    command_line_arguments.add_option(
        "--test-connection",
        default=False,
        action="store_true",
        help="Test the connection",
    )

    (options, args) = command_line_arguments.parse_args()

    LVLMAP = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    if options.log_level not in LVLMAP:
        command_line_arguments.error("invalid LEVEL: " + options.log_level)

    logging.basicConfig(
        filename=options.log_file,
        filemode="a",
        format="%(asctime)s %(levelname)s %(message)s",
        level=LVLMAP[options.log_level],
    )

    LOGGER.info("Starting MqttLogger with log-level %s" % (options.log_level))

    mqttlogger = MqttLogger(
        tmp_dir=options.tmp_dir,
        duration=options.duration,
        out_dir=options.out_dir,
        mqtthost=options.host,
        mqttport=options.port,
        mqttkeepalive=options.keepalive,
        topic=options.topic,
        username=options.username,
        password=options.password,
    )
    if options.test_connection:
        mqttlogger.test_connection()
    else:
        mqttlogger.run()


if __name__ == "__main__":
    main()
