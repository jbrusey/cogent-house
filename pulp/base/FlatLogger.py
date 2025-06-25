#
# FlatLogger
#
# log data from mote to a flat file and also print out
#
# J. Brusey, R. Wilkins, July 2015

"""FlatLogger - cogent-house data logging process.

Receives sensor readings from the base station and logs them to a flat file
This version also acknowledges logged data once it has been
successfully written to the file.

"""

import logging
import json
import os
import math
import time
from optparse import OptionParser
from tinyos3.message import MoteIF
from pulp.node import AckMsg, Packets
from pulp.base.BaseIF import BaseIF
from queue import Empty
from pulp.base.packstate import PackState

LOGGER = logging.getLogger(__name__)
QUEUE_TIMEOUT = 10
HOST_NAME = os.uname()[1]


class FlatLogger(object):
    """FlatLogger class receives sensor messages and writes them to
    a flat file.
    """

    def __init__(self, bif=None, tmp_dir=".", duration=900, out_dir="."):
        """create a new FlatLogger and connect it to the sensor
        source (bif)
        """
        if bif is None:
            self.bif = BaseIF("sf@localhost:9002")
        else:
            self.bif = bif

        self.tmp_dir = tmp_dir
        self.duration = duration
        self.out_dir = out_dir

        self.time_count = 0.0  # how many seconds we've waited since last file
        self.last_time = time.time()  # compare against for time_count
        self.log = logging.getLogger("flatlogger")
        self.running = True
        self.first = True
        time_string = time.strftime("%Y_%j_%H-%M", time.gmtime())
        self.out_fname = "%s_%s.log" % (time_string, HOST_NAME)
        self.log_fname = "%s/%s" % (self.tmp_dir, self.out_fname)
        self.log.debug("Logging directory %s" % (self.log_fname))
        print(f"opening {self.log_fname}")
        self.tmp_file = open(self.log_fname, "w")

    def send_ack(self, seq=None, dest=None):
        """send acknowledgement message"""
        ack_msg = AckMsg()
        ack_msg.set_seq(seq)
        ack_msg.set_node_id(dest)

        self.bif.sendMsg(ack_msg, dest)
        self.log.debug("Sending Ack %s to %s" % (seq, dest))

    def store_state(self, msg):
        """receive and process a message object from the base station"""

        # update amount of time we've been waiting
        tmp_time = time.time()
        self.time_count += tmp_time - self.last_time
        self.last_time = tmp_time

        # do we need to start a new file?
        if self.time_count >= float(self.duration):
            self.tmp_file.close()

            # move it
            try:
                os.rename(self.log_fname, f"{self.out_dir}/{self.out_fname}")
            except OSError as e:
                self.log.exception(e)
            # ready for next interval
            self.time_count = 0
            # start new file
            time_string = time.strftime("%Y_%j_%H-%M", time.gmtime())
            self.out_fname = "%s_%s.log" % (time_string, HOST_NAME)
            self.log_fname = "%s/%s" % (self.tmp_dir, self.out_fname)
            self.tmp_file = open(self.log_fname, "w")

        if msg.get_special() != Packets.SPECIAL:
            raise Exception(
                "Corrupted packet - special is %02x not %02x"
                % (msg.get_special(), Packets.SPECIAL)
            )

        pack_state = PackState.from_message(msg)

        output = {}
        for type_id, value in pack_state.d.items():
            if math.isinf(value) or math.isnan(value):
                value = None
            # out_type = type_lookup[type_id]
            output[type_id] = value

        output["server_time"] = time.time()
        output["localtime"] = msg.get_timestamp()
        output["sender"] = msg.getAddr()
        output["parent"] = msg.get_ctp_parent_id()
        output["seq"] = msg.get_seq()
        output["rssi"] = msg.get_rssi()

        # prep output JSON line
        json_str = json.dumps(output) + "\n"

        # write to node file
        node_file = open("%s/node_%s.log" % (self.tmp_dir, output["sender"]), "w")
        node_file.write(json_str)
        node_file.close()

        # write to file in /tmp/
        self.tmp_file.write(json_str)
        self.tmp_file.flush()

        # send acknowledgement to base station to fwd to node
        self.send_ack(seq=output["seq"], dest=output["sender"])
        return True

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
                self.log.debug("received statemsg")
                status = self.store_state(msg)
            else:
                self.log.debug(
                    f"received some other message of type {msg.get_amType()}"
                )
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
            self.log.exception("during receiving or storing msg: " + str(excepterr))

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
        "-o",
        "--out-dir",
        metavar="DIR",
        default=".",
        help="Output directory for files (default .)",
    )
    command_line_arguments.add_option(
        "-t",
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
        default="/var/log/ch/FlatLogger.log",
        help="Log file to use (Default ./Flatlogger.log",
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

    try:
        MoteIF.set_debug_level(LVLMAP[options.log_level])
    except Exception as e:
        LOGGER.warning(f"Could not set MoteIF debug level: {e}")

    LOGGER.info("Starting FlatLogger with log-level %s" % (options.log_level))
    flatlog = FlatLogger(
        tmp_dir=options.tmp_dir, duration=options.duration, out_dir=options.out_dir
    )
    flatlog.run()


if __name__ == "__main__":  # pragma: no cover
    main()
