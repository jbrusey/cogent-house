#
# BaseLogger
#
# log data from mote to a database and also print out
#
# J. Brusey, R. Wilkins, April 2011
# D. Goldsmith, May 2013

import logging
import sys
import os
from optparse import OptionParser

if "TOSROOT" not in os.environ:
    raise Exception("Please source the Tiny OS environment script first")
sys.path.append(os.environ["TOSROOT"] + "/support/sdk/python")

from cogent.node import *
from cogent.base.BaseIF import BaseIF

from Queue import Empty

from datetime import datetime, timedelta

import time

from cogent.base.model import *
import cogent.base.model.populateData as populateData


F = "/home/james/sa.db"
DBFILE = "sqlite:///test.db"
#DBFILE = "mysql://chuser@localhost/ch"

from sqlalchemy import create_engine, func, and_
import sqlalchemy.exc

QUEUE_TIMEOUT = 10


class BaseLogger(object):
    """Baselogger Class

    Connects to the serial forwarder, and deals with queued packets.
    This class will add any new readings received over the serial interface
    to the database.
    """
    def __init__(self, bif=None, dbfile=DBFILE):
        log.debug("Init Engine")
        self.engine = create_engine(dbfile, echo=False)
        init_model(self.engine)
        if DBFILE[:7] == "sqlite:":
            self.engine.execute("pragma foreign_keys=on")
        self.metadata = Base.metadata

        if bif is None:
            self.bif = BaseIF("sf@localhost:9002")
        else:
            self.bif = bif

        self.log = logging.getLogger("baselogger")
        self.running = True

    def create_tables(self):
        """Populate the intial database"""
        self.metadata.create_all(self.engine)

        session = Session()

        #Moved this so it calls the models.populate data version of this code
        populateData.init_data(session)
        return

    def duplicate_packet(self, session, time, nodeId, localtime):
        """ duplicate packets can occur because in a large network,
        the duplicate packet cache used is not sufficient. If such
        packets occur, then they will have the same node id, same
        local time and arrive within a few seconds of each other. In
        some cases, the first received copy may be corrupt and this is
        not dealt with within this code yet.
        """
        earliest = time - timedelta(minutes=1)
        return session.query(NodeState).filter(
            and_(NodeState.nodeId==nodeId,
                 NodeState.localtime==localtime,
                 NodeState.time > earliest)).first() is not None

    # def getNodeDetails(self, nid):
    #     return ((nid % 4096) / 32,
    #             nid % 32,
    #             nid / 4096)

    def store_state(self, msg):
        if msg.get_special() != Packets.SPECIAL:
            exp="Corrupted packet - special is %02x not %02x"%(msg.get_special(),
                                                               Packets.SPECIAL)
            raise Exception(exp)

        try:
            session = Session()
            t = datetime.utcnow()
            n = msg.getAddr()
            parent = msg.get_ctp_parent_id()
            localtime = msg.get_timestamp()

            node = session.query(Node).get(n)
            locId = None
            if node is None:
                try:
                    session.add(Node(id=n,
                                     locationId=None,
                                     #nodeTypeId=(n / 4096)))
                                     nodeTypeId=None,
                                     )
                                )
                    session.commit()
                except sqlalchemy.exc.IntegrityError, e:
                    #Really this should only be a problem on Integrity Error
                    self.log.exception("can't add node {0} As {1}".format(n,
                                                                          e))
                    session.rollback()

            else:
                locId = node.locationId

            if self.duplicate_packet(session=session,
                                     time=t,
                                     nodeId=n,
                                     localtime=localtime):
                self.log.info("duplicate packet %d->%d, %d %s" % (n,
                                                                  parent,
                                                                  localtime,
                                                                  str(msg)))
                return

            ns = NodeState(time=t,
                           nodeId=n,
                           parent=msg.get_ctp_parent_id(),
                           localtime=msg.get_timestamp())
            session.add(ns)


            self.log.debug("Message from {0}".format(n))

            j = 0
            mask = Bitset(value=msg.get_packed_state_mask())
            state = []
            for i in range(msg.totalSizeBits_packed_state_mask()):
                if mask[i]:
                    v = msg.getElement_packed_state(j)
                    state.append((i, v))
                    logmsg = "Message received t:{0} n{1} i{2} v{3}".format(t,
                                                                            n,
                                                                            i,
                                                                            v)
                    self.log.debug(logmsg)

                    #Store in RRD
                    #self.store_rrd(n, i, t, v)
                    t1 = time.time()

                    try:
                        r = Reading(time=t,
                                    nodeId=n,
                                    typeId=i,
                                    locationId=locId,
                                    value=v)
                        session.add(r)
                        session.flush()
                        session.commit()
                    except sqlalchemy.exc.IntegrityError, e:
                        #No Idea why the sensortype code is not called using sqlite
                        self.log.error("Integrity Error on store: {0}".format(e))
                        session.rollback()
                        s = session.query(SensorType).filter_by(id=i).first()
                        if s is None:
                            self.log.info("--> No such SensorType")
                            s = SensorType(id=i, name="UNKNOWN")
                            session.add(s)
                            self.log.info("Adding new sensortype")
                            session.flush()
                            r = Reading(time=t,
                                        nodeId=n,
                                        typeId=i,
                                        locationId=locId,
                                        value=v)
                            session.add(r)
                            session.flush()
                            session.commit()
                        else:
                            self.log.error("--> Unable to add reading")

                    t2 = time.time()
                    self.log.debug("Time taken to update DB {0}".format(t2-t1))
                    j += 1

            session.commit()
            self.log.debug("reading: %s, %s, %s" % (ns, mask, state))
        except Exception as e:
            session.rollback()
            self.log.exception("during storing: " + str(e))
        finally:
            session.close()

    def mainloop(self):
        """Break out run into a single 'mainloop' function

        Poll the bif.queue for data, if something has been received
        process and store.

        :return True: If a packet has been received and stored correctly
        :return False: Otherwise
        """
        log.debug("Main Loop")
        try:
            msg = self.bif.queue.get(True, QUEUE_TIMEOUT)
            #self.log.debug("Msg Recvd {0}".format(msg))
            self.store_state(msg)
            #Signal the queue that we have finished processing
            self.bif.queue.task_done()
            return True
        except Empty:
            self.log.debug("Empty Queue")
            return False
        except KeyboardInterrupt:
            print "KEYB IRR"
            self.running = False
        except Exception as e:
            self.log.exception("during receiving or storing msg: " + str(e))


    def run(self):
        """Mainloop function"""
        self.log.info("Stating Baselogger Daemon")
        while self.running:
            self.mainloop()
            # try:
            #     msg = self.bif.queue.get(True, 30)
            #     #msg = self.bif.get(True, 10) #Avoid using this for the moment
            #     self.store_state(msg)
            #     #Signal the queue that we have finished processing
            #     self.bif.queue.task_done()
            # except Empty:
            #     self.log.debug("Empty Queue")
            # except KeyboardInterrupt:
            #     print "KEYB IRR"
            #     self.running = False
            # except Exception as e:
            #     self.log.exception("during receiving or storing msg: " + str(e))

        print "SHUTDOWN"
        self.bif.finishAll()
        print "---> Done"


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
