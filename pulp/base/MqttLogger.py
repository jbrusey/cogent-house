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

"""

import logging
import math
import pickle
from queue import Empty
from optparse import OptionParser
from pulp.node import Packets

import paho.mqtt.client as mqtt

if __name__ == "__main__" and __package__ is None:
    __package__ = "pulp.base"

from .packstate import PackState

LOGGER = logging.getLogger(__name__)
QUEUE_TIMEOUT = 10


def on_connect(client, userdata, flags, rc):
    """The callback for when the client receives a CONNACK response
    from the server."""
    LOGGER.debug(f"Connected with result code {rc}")


class MqttLogger(object):
    """Log messages to mqtt"""

    def __init__(
        self,
        bif=None,
        topic="",
        host="localhost",
        port=1883,
        keepalive=60,
        username=None,
        password=None,
    ):
        self.bif = bif

        self.topic = topic
        self.client = mqtt.Client()
        self.client.on_connect = on_connect
        if username:
            self.client.username_pw_set(username, password=password)
        self.client.connect(host=host, port=port, keepalive=keepalive)
        # background async loop
        self.client.loop_start()

    def publish(self, sender=None, type_id=None, value=None):
        self.client.publish(f"{self.topic}/{sender}/{type_id}", value)

    def store_state(self, msg):

        pack_state = PackState.from_message(msg)

        for type_id, value in pack_state.d.items():
            if math.isinf(value) or math.isnan(value):
                value = None

            if value is not None:
                self.publish(sender=msg.getAddr(), type_id=type_id, value=value)
        return True

    def test_connection(self):
        self.client.publish(f"{self.topic}/test", 1)

    def mainloop(self):
        """Break out run into a single 'mainloop' function

        Poll the bif.queue for data, if something has been received
        process and store.

        :return True: If a packet has been received and stored correctly
        :return False: Otherwise
        """
        status = False
        try:
            msg = self.bif.queue.get(True, QUEUE_TIMEOUT)
            if msg.get_amType() == Packets.AM_BOOTMSG:
                # Log node boot
                # status = self.booted_node(msg)
                pass
            elif msg.get_amType() == Packets.AM_STATEMSG:
                LOGGER.debug("received statemsg")
                status = self.store_state(msg)
            else:
                LOGGER.debug(f"received some other message of type {msg.get_amType()}")
                status = False
            # Signal the queue that we have finished processing
            self.bif.queue.task_done()
            return status
        except Empty:
            return False
        except KeyboardInterrupt:
            print("KEYB IRR")
            self.running = False
        except Exception as excepterr:
            LOGGER.exception("during receiving or storing msg: " + str(excepterr))
        return False

    def run(self):
        """run - main loop

        At the moment this is just receiving from the sensor message
        queue and processing the message.

        """
        while self.running:
            self.mainloop()


def main():
    command_line_arguments = OptionParser()

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
        "-A",
        "--authpickle",
        default=None,
        help="Filename for pickle containing credentials",
    )

    command_line_arguments.add_option(
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

    if options.authfile is not None and (
        options.username is not None or options.password is not None
    ):
        print("Error: cannot give both authfile and username / password")
        command_line_arguments.print_help()
        return

    (username, password) = (options.username, options.password)
    if (
        options.username is None
        and options.password is None
        and options.authfile is not None
    ):
        with open(options.authfile, "rb") as f:
            (username, password) = pickle.load(f)

    mqttlogger = MqttLogger(
        host=options.host,
        port=options.port,
        keepalive=options.keepalive,
        topic=options.topic,
        username=username,
        password=password,
    )
    if options.test_connection:
        mqttlogger.test_connection()
    else:
        mqttlogger.run()


if __name__ == "__main__":
    main()
