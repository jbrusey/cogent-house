#
# BaseLogger
#
# log data from mote to a database and also print out
#
# J. Brusey, R. Wilkins, April 2011
# D. Goldsmith, May 2013

"""BaseLogger - cogent-house data logging process.

Receives sensor readings from the base station and logs them to the
database.

This version also acknowledges logged data once it has been
successfully written to the database.

"""

import logging
import sys
import os
from optparse import OptionParser

if "TOSROOT" not in os.environ:
    raise Exception("Please source the Tiny OS environment script first")
sys.path.append(os.environ["TOSROOT"] + "/support/sdk/python")

from cogent.node import (AckMsg,
                         Packets)
from cogent.base.BaseIF import BaseIF

from Queue import Empty

from datetime import datetime, timedelta

#import time

from cogent.base.model import (Reading, NodeState, SensorType,
                               Base, Session, init_model, Node)

import cogent.base.model as models
import cogent.base.model.meta as meta
from cogent.base.packstate import PackState

LOGGER = logging.getLogger("ch.base")

DBFILE = "mysql://chuser@localhost/ch"
#DBFILE = "sqlite:///test.db"

from sqlalchemy import create_engine, and_

QUEUE_TIMEOUT = 10

def duplicate_packet(session, receipt_time, node_id, localtime):
    """ duplicate packets can occur because in a large network,
    the duplicate packet cache used is not sufficient. If such
    packets occur, then they will have the same node id, same
    local time and arrive within a few seconds of each other. In
    some cases, the first received copy may be corrupt and this is
    not dealt with within this code yet.
    """
    earliest = receipt_time - timedelta(minutes=1)
    return session.query(NodeState).filter(
        and_(NodeState.nodeId==node_id,
             NodeState.localtime==localtime,
             NodeState.time > earliest)).first() is not None

def add_node(session, node_id):
    """ add a database entry for a node
    """
    try:
        session.add(Node(id=node_id,
                         locationId=None,
            nodeTypeId=(node_id / 4096)))
        session.commit()
    except Exception:
        session.rollback()
        LOGGER.exception("can't add node %d" % node_id)


class BaseLogger(object):
    """ BaseLogger class receives sensor messages and writes them to
    the database.
    """
    def __init__(self, bif=None, dbfile=DBFILE):
        """ create a new BaseLogger and connect it to the sensor
        source (bif) and the database (dbfile).
        """
        self.engine = create_engine(dbfile, echo=False)
        #init_model(self.engine)
        models.initialise_sql(self.engine)
        #self.metadata = Base.metadata

        if bif is None:
            self.bif = BaseIF("sf@localhost:9002")
        else:
            self.bif = bif

        self.log = logging.getLogger("baselogger")
        self.running = True

    def create_tables(self):
        """ create any missing tables using sqlalchemy
        """
        #self.metadata.create_all(self.engine)
        # TODO: follow the instructions at url:
        # https://alembic.readthedocs.org/en/latest/tutorial.html#building-an-up-to-date-database-from-scratch
        # to write an alembic version string

        session = meta.Session()
        models.populateData.init_data(session)
        if session.query(SensorType).get(0) is None:
            raise Exception("SensorType must be populated by alembic " +
                            "before starting BaseLogger")
        session.close()    
                             

    def send_ack(self,
                 seq=None,
                 dest=None):
        """ send acknowledgement message
        """
        ack_msg = AckMsg()
        ack_msg.set_seq(seq)
        ack_msg.set_node_id(dest)
        
        self.bif.sendMsg(ack_msg, dest)
        LOGGER.debug("Sending Ack %s to %s" %
                     (seq, dest))


    def store_state(self, msg):
        """ receive and process a message object from the base station
        """
    
        if msg.get_special() != Packets.SPECIAL:
            raise Exception("Corrupted packet - special is %02x not %02x" %
                            (msg.get_special(), Packets.SPECIAL))

        try:
            session = Session()
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
            
            if duplicate_packet(session=session,
                                receipt_time=current_time,
                                node_id=node_id,
                                localtime=msg.get_timestamp()):
                LOGGER.info("duplicate packet %d->%d, %d %s" %
                            (node_id, parent_id, msg.get_timestamp(), str(msg)))

                return False

            # write a node state row
            node_state = NodeState(time=current_time,
                                   nodeId=node_id,
                                   parent=parent_id,
                localtime=msg.get_timestamp(),
                seq_num=seq,
                rssi = rssi_val)
            session.add(node_state)

            for i, value in pack_state.d.iteritems():
                type_id = i

                r = Reading(time=current_time,
                            nodeId=node_id,
                            typeId=type_id,
                            locationId=loc_id,
                            value=value)
                try:
                    session.add(r)
                    session.flush()

                except sqlalchemy.exc.IntegrityError:
                    self.log.error("Unable to store, checking if node type exists")
                    session.rollback()
                    s = session.query(SensorType).filter_by(id=i).first()
                    if s is None:
                        s = SensorType(id=type_id,name="UNKNOWN")
                        session.add(s)
                        self.log.info("Adding new sensortype")
                        session.flush()
                        session.add(r)
                        session.flush()                            
                    else:
                        self.log.error("Sensor type exists")


            self.log.debug("reading: %s, %s" % (node_state, pack_state))
            session.commit()

            #send acknowledgement to base station to fwd to node
            self.send_ack(seq=seq,
                          dest=node_id)
                     

        except Exception as exc:
            session.rollback()
            self.log.exception("during storing: " + str(exc))
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
        #self.log.debug("Main Loop")
        try:
            msg = self.bif.queue.get(True, QUEUE_TIMEOUT)
            #self.log.debug("Msg Recvd {0}".format(msg))
            status = self.store_state(msg)
            #Signal the queue that we have finished processing
            self.bif.queue.task_done()
            return status
        except Empty:
            #self.log.debug("Empty Queue")
            return False
        except KeyboardInterrupt:
            print "KEYB IRR"
            self.running = False
        except Exception as e:
            self.log.exception("during receiving or storing msg: " + str(e))


    def run(self):
        """ run - main loop

        At the moment this is just receiving from the sensor message
        queue and processing the message.

        """

        while self.running:
            self.mainloop()
        # try:
        #     while True:
        #         # wait up to 5 seconds for a message
        #         try:
        #             msg = self.bif.get(True, 5)
        #             self.store_state(msg)
        #         except Empty:
        #             pass
        #         except Exception as exc:
        #             LOGGER.exception("during receiving or storing msg: " +
        #                              str(exc))

        # except KeyboardInterrupt:
        #     self.bif.finishAll()

                
if __name__ == '__main__': # pragma: no cover
    parser = OptionParser()
    parser.add_option("-l", "--log-level",
                      help="Set log level to LEVEL: debug,info,warning,error",
                      default="info",
                      metavar="LEVEL")

    parser.add_option("-f", "--log-file",
                      help="Log file to use (Default /var/log/ch/Baselogging.log",
                      default="/var/log/ch/BaseLogging.log")

    parser.add_option("-t", "--log-terminal",
                      help="Echo Logging output to terminal",
                      action="store_true",
                      default=False)


    (options, args) = parser.parse_args()
    if len(args) != 0:
        parser.error("incorrect number of arguments")

    lvlmap = {"debug": logging.DEBUG,
              "info": logging.INFO,
              "warning": logging.WARNING,
              "error": logging.ERROR,
              "critical": logging.CRITICAL}

    if options.log_level not in lvlmap:
        parser.error("invalid LEVEL: " + options.log_level)

    logfile = options.log_file

    #logging.basicConfig(filename="/var/log/ch/BaseLogging.log"
    logging.basicConfig(filename=logfile,
                        filemode="a",
                        format="%(asctime)s %(levelname)s %(message)s",
                        level=lvlmap[options.log_level])

    #And if we want to echo the output on the terminal
    logterm = options.log_terminal
    if logterm:
        console = logging.StreamHandler()
        console.setLevel(lvlmap[options.log_level])
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)



    logging.info("Starting BaseLogger with log-level %s" % (options.log_level))
    lm = BaseLogger()
    lm.create_tables()
    lm.run()
