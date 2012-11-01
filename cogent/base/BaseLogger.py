#
# BaseLogger
#
# log data from mote to a database and also print out 
#
# J. Brusey, R. Wilkins, April 2011

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

logger = logging.getLogger("ch.base")

DBFILE = "mysql://chuser@localhost/ch"

from sqlalchemy import create_engine, func, and_


class BaseLogger(object):
    def __init__(self, bif=None, dbfile=DBFILE):
        self.engine = create_engine(dbfile, echo=False)
        init_model(self.engine)
        self.metadata = Base.metadata

        if bif is None:
            self.bif = BaseIF("sf@localhost:9002")
        else:
            self.bif = bif

    def create_tables(self):
        self.metadata.create_all(self.engine)

        session = Session()
        if session.query(SensorType).get(0) is None:
            logger.debug("adding sensor types")
            # assume no sensor types have been added
            session.add_all(
                [SensorType(id=0,name="Temperature",
                            code="T",
                            units="deg.C",
                            c0=0., c1=1., c2=0., c3=0.)])
            session.commit()
        session.close()    
                             

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
            
    def getNodeDetails(self, nid):
        return ((nid % 4096) / 32,
                nid % 32,
                nid / 4096)
    	
    def store_state(self, msg):
    
	logger.info(msg)
        logger.info(type(msg))

	dest=0
	for x in msg.get_route():
		if int(x)>0:
			dest=int(x)

        #send acknowledgement to base station to fwd to node
        am = AckMsg()
        am.set_seq(int(msg.get_seq()))
        am.set_route(msg.get_route())
        am.set_hops(msg.get_hops())

        self.bif.sendMsg(am,dest)
        logger.debug("Sending Ack %s to %s:, Hops: %s, Route: %s" % (am.get_seq(), dest, am.get_hops(), am.get_route()))

        if msg.get_special() != Packets.SPECIAL:
            raise Exception("Corrupted packet - special is %02x not %02x" % (msg.get_special(), Packets.SPECIAL))

        try:
            session = Session()
            t = datetime.utcnow()
            n=msg.get_route()[0]
	    pid=msg.get_route()[1]

            localtime = msg.get_timestamp()

            node = session.query(Node).get(n)
            locId = None
            if node is None:
                try:
                    session.add(Node(id=n,
                                     locationId=None,
                                     nodeTypeId=(n / 4096)))
                    session.commit()
                except:
                    session.rollback()
                    logger.exception("can't add node %d" % n)
            else:
                locId = node.locationId

            if self.duplicate_packet(session=session,
                                     time=t,
                                     nodeId=n,
                                     localtime=localtime):
                logger.info("duplicate packet %d->%d, %d %s" % (n, pid, localtime, str(msg)))
                return

            ns = NodeState(time=t,
                           nodeId=n,
                           parent=pid,
                           localtime=msg.get_timestamp())
            session.add(ns)

            j = 0
            mask = Bitset(value=msg.get_packed_state_mask())
            state = []
            for i in range(msg.totalSizeBits_packed_state_mask()):
                if mask[i]:
                    tid=None
                    if msg.get_amType()==8:
                        if i != 6:
                            tid=i+50
			else:
			    tid=6
                    else:
                        tid=i
                    v = msg.getElement_packed_state(j)
                    state.append((i,v))
                    r = Reading(time=t,
                                nodeId=n,
                                typeId=tid,
                                locationId=locId,
                                value=v)
                    session.add(r)
                    j += 1

            session.commit()
            logger.debug("reading: %s, %s, %s" % (ns,mask,state))

        except Exception as e:
            session.rollback()
            logger.exception("during storing: " + str(e))
        finally:
            session.close()

    def run(self):

        try:
            while True:
                # wait up to 30 seconds for a message
                try:
                    msg = self.bif.queue.get(True, 30)
                    self.store_state(msg)
                except Empty:
                    pass
                except Exception as e:
                    logger.exception("during receiving or storing msg: " + str(e))

        except KeyboardInterrupt:
            self.bif.finishAll()

                
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-l", "--log-level",
                      help="Set log level to LEVEL: debug,info,warning,error, [default: info]",
                      default="info",
                      metavar="LEVEL")

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

    
    
    logging.basicConfig(filename="/var/log/ch/BaseLogger.log",
                        filemode="a",
                        format="%(asctime)s %(levelname)s %(message)s",
                        level=lvlmap[options.log_level])
    logger.info("Starting BaseLogger with log-level %s" % (options.log_level))
    lm = BaseLogger()
    lm.create_tables()
    
    lm.run()
		
