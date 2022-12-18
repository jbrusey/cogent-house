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

import csv
import datetime
import logging
import math
import pickle
from optparse import OptionParser
from queue import Empty

import paho.mqtt.client as mqtt
from pulp.node import Packets

if __name__ == "__main__" and __package__ is None:
    __package__ = "pulp.base"

from .BaseIF import BaseIF
from .packstate import PackState

LOGGER = logging.getLogger(__name__)
QUEUE_TIMEOUT = 10
TYPES = {
    0: "temperature",
    1: "d_temperature",
    2: "humidity",
    3: "d_humidity",
    4: "par",
    5: "tsr",
    6: "voltage",
    7: "d_voltage",
    8: "co2",
    9: "aq",
    10: "voc",
    11: "power",
    12: "heat",
    13: "duty_time",
    14: "errno",
    15: "power_min",
    16: "power_max",
    17: "power_kwh",
    18: "heat_energy",
    19: "heat_volume",
    20: "d_co2",
    21: "d_voc",
    22: "d_aq",
    23: "wall_temp",
    24: "d_wall_temp",
    25: "wall_hum",
    26: "d_wall_hum",
    40: "opti",
    41: "tempadc1",
    42: "d_tempadc1",
    43: "gas",
    44: "d_opti",
    45: "window",
    46: "bb",
    47: "d_bb",
}


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
        location_file=None,
    ):
        if bif is None:
            self.bif = BaseIF("sf@localhost:9002")
        else:
            self.bif = bif

        self.running = True

        if location_file is not None:
            self.location = self.read_location_file(location_file)
        else:
            self.location = None

        self.topic = topic
        self.client = mqtt.Client()
        self.client.on_connect = on_connect
        if username:
            self.client.username_pw_set(username, password=password)
        self.client.connect(host=host, port=port, keepalive=keepalive)
        # background async loop
        self.client.loop_start()

    def read_location_file(self, location_file: str) -> dict:
        """The location file allows translation of the location
        numbers to location names for the mqtt message"""
        location = {}
        with open(location_file, "r") as lf:
            reader = csv.reader(lf)
            for row in reader:
                id = int(row[0])
                room = row[1]
                location[id] = room
        return location

    def publish(self, sender=None, subtopic=None, payload=None):
        minfo = self.client.publish(f"{self.topic}/{sender}/{subtopic}", payload)
        LOGGER.debug(
            f"publish('{self.topic}/{sender}/{subtopic}', {payload}) -> {minfo.rc}, {minfo.mid}"
        )

    def store_state(self, msg):
        pack_state = PackState.from_message(msg)

        sender = msg.getAddr()
        if self.location is not None and int(sender) in self.location:
            sender = self.location[int(sender)]

        for type_id, value in pack_state.d.items():
            if math.isinf(value) or math.isnan(value):
                value = None

            if value is not None:
                if type_id not in TYPES:
                    subtopic = f"{type_id}"
                else:
                    subtopic = TYPES[type_id]
                self.publish(sender=sender, subtopic=subtopic, payload=value)

        return True

    def test_connection(self):
        payload = repr(datetime.datetime.now())
        minfo = self.client.publish(f"{self.topic}/test", payload=payload, qos=1)
        minfo.wait_for_publish()
        LOGGER.debug(
            f"publish('{self.topic}/test', payload='{payload}', qos=1) -> rc={minfo.rc}, mid={minfo.mid} pub? {minfo.is_published()}"
        )

    def mainloop(self):
        """Break out run into a single 'mainloop' function

        Poll the bif.queue for data, if something has been received
        process and store.

        :return True: If a packet has been received and stored correctly
        :return False: Otherwise
        """
        status = False
        try:
            msg = self.bif.get(True, QUEUE_TIMEOUT)
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
        "--host",
        default="localhost",
        help="Host for logging mqtt messages (default: localhost)",
    )
    command_line_arguments.add_option(
        "-p",
        "--port",
        default=1883,
        type=int,
        help="Port number for mqtt logging (default: 1883)",
    )
    command_line_arguments.add_option(
        "--keepalive",
        default=60,
        type=int,
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
        "--location-file",
        default=None,
        help="""csv file containing mapping from location number to name.
        The csv file should be formatted as <num>, <name> with one row for each
        location and no header.""",
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

    if options.authpickle is not None and (
        options.username is not None or options.password is not None
    ):
        print("Error: cannot give both authpickle and username / password")
        command_line_arguments.print_help()
        return

    (username, password) = (options.username, options.password)
    if (
        options.username is None
        and options.password is None
        and options.authpickle is not None
    ):
        with open(options.authpickle, "rb") as f:
            (username, password) = pickle.load(f)

    mqttlogger = MqttLogger(
        host=options.host,
        port=options.port,
        keepalive=options.keepalive,
        topic=options.topic,
        username=username,
        password=password,
        location_file=options.location_file,
    )
    if options.test_connection:
        mqttlogger.test_connection()
    else:
        mqttlogger.run()


if __name__ == "__main__":
    main()
