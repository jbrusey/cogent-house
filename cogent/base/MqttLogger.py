"""MqttLogger - log to mqtt

Revision of BaseLogger that emits mqtt messages instead of storing to a database.

Author
------
J. Brusey, R. Wilkins, D. Goldsmith

Date
----
May, 2021

"""

import logging
import math
from datetime import datetime, timedelta
from optparse import OptionParser
from queue import Empty
import paho.mqtt.client as mqtt

import cogent.base.model as models
import cogent.base.model.meta as meta
from cogent.base.BaseIF import BaseIF
from cogent.base.model import Node, NodeBoot, NodeState, Reading, SensorType
from cogent.base.packstate import PackState
from cogent.node import AckMsg, Packets

# if "TOSROOT" not in os.environ:
#     raise Exception("Please source the Tiny OS environment script first")
# sys.path.append(os.environ["TOSROOT"] + "/support/sdk/python")

LOGGER = logging.getLogger("ch.mqtt")

QUEUE_TIMEOUT = 10


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


def duplicate_packet(session, receipt_time, node_id, localtime):
    """duplicate packets can occur because in a large network,
    the duplicate packet cache used is not sufficient. If such
    packets occur, then they will have the same node id, same
    local time and arrive within a few seconds of each other. In
    some cases, the first received copy may be corrupt and this is
    not dealt with within this code yet.
    """
    earliest = receipt_time - timedelta(minutes=1)
    return (
        session.query(NodeState)
        .filter(
            and_(
                NodeState.nodeId == node_id,
                NodeState.localtime == localtime,
                NodeState.time > earliest,
            )
        )
        .first()
        is not None
    )


def add_node(session, node_id):
    """add a database entry for a node"""
    try:
        session.add(Node(id=node_id, locationId=None, nodeTypeId=(node_id / 4096)))
        session.commit()
    except Exception:
        session.rollback()
        LOGGER.exception("can't add node %d" % node_id)


class MqttLogger(object):
    """MqttLogger class receives sensor messages and writes them to
    MQTT.
    """

    def __init__(self, bif=None):
        """create a new MqttLogger and connect it to the sensor
        source (bif)
        """
        self.mqtt = mqtt.Client()
        self.mqtt.on_connect = on_connect

        self.mqtt.connect("localhost", port=1883)

        models.initialise_sql(self.engine)
        # self.metadata = Base.metadata

        if bif is None:
            self.bif = BaseIF("sf@localhost:9002")
        else:
            self.bif = bif

        self.log = logging.getLogger("baselogger")
        self.running = True

    def create_tables(self):
        """create any missing tables using sqlalchemy"""
        # self.metadata.create_all(self.engine)
        # TODO: follow the instructions at url:
        # https://alembic.readthedocs.org/en/latest/tutorial.html#building-an-up-to-date-database-from-scratch
        # to write an alembic version string

        session = meta.Session()
        models.populateData.init_data(session)
        if session.query(SensorType).get(0) is None:
            raise Exception(
                "SensorType must be populated by alembic before starting MqttLogger"
            )
        session.close()

    def send_ack(self, seq=None, dest=None):
        """send acknowledgement message"""
        ack_msg = AckMsg()
        ack_msg.set_seq(seq)
        ack_msg.set_node_id(dest)

        self.bif.sendMsg(ack_msg, dest)
        self.log.debug("Sending Ack %s to %s" % (seq, dest))

    def booted_node(self, msg):
        """Receieve and process a boot message object from the base station"""

        if msg.get_special() != Packets.SPECIAL:
            raise Exception(
                "Corrupted packet - special is %02x not %02x"
                % (msg.get_special(), Packets.SPECIAL)
            )
        try:
            session = meta.Session()
            current_time = datetime.utcnow()
            node_id = msg.getAddr()
            clustered = msg.get_clustered()
            version = msg.get_version()
            version = "".join([chr(i) for i in version])

            node = session.query(Node).get(node_id)
            if node is None:
                add_node(session, node_id)

            b = NodeBoot(
                time=current_time, nodeId=node_id, clustered=clustered, version=version
            )
            session.add(b)
            session.flush()
            self.log.debug(
                "boot: %s %s, %s, %s" % (current_time, node_id, clustered, version)
            )
            session.commit()
        except Exception as exc:
            session.rollback()
            self.log.exception("error during storing (boot): " + str(exc))
        finally:
            session.close()

        return True

    def store_state(self, msg):
        """receive and process a message object from the base station"""
        if msg.get_special() != Packets.SPECIAL:
            raise Exception(
                "Corrupted packet - special is %02x not %02x"
                % (msg.get_special(), Packets.SPECIAL)
            )

        try:
            session = meta.Session()
            current_time = datetime.utcnow()
            node_id = msg.getAddr()
            parent_id = msg.get_ctp_parent_id()
            seq = msg.get_seq()
            rssi_val = msg.get_rssi()

            node = session.query(Node).get(node_id)
            loc_id = None
            if node is None:
                add_node(session, node_id)
            else:
                loc_id = node.locationId

            pack_state = PackState.from_message(msg)

            if duplicate_packet(
                session=session,
                receipt_time=current_time,
                node_id=node_id,
                localtime=msg.get_timestamp(),
            ):
                LOGGER.info(
                    "duplicate packet %d->%d, %d %s"
                    % (node_id, parent_id, msg.get_timestamp(), str(msg))
                )

                return False

            # write a node state row
            node_state = NodeState(
                time=current_time,
                nodeId=node_id,
                parent=parent_id,
                localtime=msg.get_timestamp(),
                seq_num=seq,
                rssi=rssi_val,
            )
            session.add(node_state)

            for i, value in list(pack_state.d.items()):
                type_id = i
                if math.isinf(value) or math.isnan(value):
                    value = None

                r = Reading(
                    time=current_time,
                    nodeId=node_id,
                    typeId=type_id,
                    locationId=loc_id,
                    value=value,
                )
                try:
                    session.add(r)
                    session.flush()

                except sqlalchemy.exc.IntegrityError as e:
                    self.log.error(
                        "Unable to store reading, checking if node type exists"
                    )
                    self.log.error(e)
                    session.rollback()
                    s = session.query(SensorType).filter_by(id=i).first()
                    if s is None:
                        s = SensorType(id=type_id, name="UNKNOWN")
                        session.add(s)
                        self.log.info("Adding new sensortype")
                        session.flush()
                        session.add(r)
                        session.flush()
                    else:
                        self.log.error("Sensor type exists")

            self.log.debug("reading: %s, %s" % (node_state, pack_state))
            session.commit()

            # send acknowledgement to base station to fwd to node
            self.send_ack(seq=seq, dest=node_id)

        except Exception as exc:
            session.rollback()
            self.log.exception("error during storing (reading): " + str(exc))
        finally:
            session.close()

        return True

    def mainloop(self):
        """Break out run into a single 'mainloop' function

        Poll the bif.queue for data, if something has been received
        process and store.

        :return True: If a packet has been received and stored correctly
        :return False: Otherwise
        """
        # self.log.debug("Main Loop")
        try:
            msg = self.bif.queue.get(True, QUEUE_TIMEOUT)
            if msg.get_amType() == Packets.AM_BOOTMSG:
                # Log node boot
                status = self.booted_node(msg)
            elif msg.get_amType() == Packets.AM_STATEMSG:
                # self.log.debug("Msg Recvd {0}".format(msg))
                status = self.store_state(msg)
            else:
                status = False
            self.bif.queue.task_done()
            return status
        except Empty:
            return False
        except KeyboardInterrupt:
            print("KEYB IRR")
            self.running = False
        except Exception as e:
            self.log.exception("during receiving or storing msg: " + str(e))

    def run(self):
        """run - main loop

        At the moment this is just receiving from the sensor message
        queue and processing the message.

        """

        while self.running:
            self.mainloop()
            self.mqtt.loop()


def main():
    parser = OptionParser()
    parser.add_option(
        "-l",
        "--log-level",
        help="Set log level to LEVEL: debug,info,warning,error",
        default="debug",
        metavar="LEVEL",
    )

    parser.add_option(
        "-f",
        "--log-file",
        help="Log file to use (Default /var/log/ch/Mqttlogger.log",
        default="/var/log/ch/MqttLogger.log",
    )

    parser.add_option(
        "-t",
        "--log-terminal",
        help="Echo Logging output to terminal",
        action="store_true",
        default=False,
    )

    (options, args) = parser.parse_args()
    if len(args) != 0:
        parser.error("incorrect number of arguments")

    lvlmap = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    if options.log_level not in lvlmap:
        parser.error("invalid LEVEL: " + options.log_level)

    logfile = options.log_file

    logging.basicConfig(
        filename=logfile,
        filemode="a",
        format="%(asctime)s %(levelname)s %(message)s",
        level=lvlmap[options.log_level],
    )

    logterm = options.log_terminal
    if logterm:
        console = logging.StreamHandler()
        console.setLevel(lvlmap[options.log_level])
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        console.setFormatter(formatter)
        logging.getLogger("").addHandler(console)

    logging.info("Starting MqttLogger with log-level %s" % (options.log_level))
    lm = MqttLogger()
    lm.create_tables()
    lm.run()


if __name__ == "__main__":
    main()
