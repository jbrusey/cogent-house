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

F="/home/james/sa.db"
#DBFILE = "sqlite:///" 
DBFILE = "mysql://chuser@localhost/ch"

from sqlalchemy import create_engine, func, and_


class BaseLogger(object):
    def __init__(self, bif=None, dbfile=DBFILE):
        self.engine = create_engine(dbfile, echo=False)
        init_model(self.engine)
        #if DBFILE[:7] == "sqlite:":
        #    self.engine.execute("pragma foreign_keys=on")
        self.metadata = Base.metadata

        if bif is None:
            self.bif = BaseIF("sf@localhost:9002")
        else:
            self.bif = bif

    def create_tables(self):
        self.metadata.create_all(self.engine)

        session = Session()

        #Fix this so if we happen to add a new sensor type things will work
        if session.query(SensorType).get(0) is None:
            logger.debug("adding sensor types")
            # assume no sensor types have been added
            session.add_all(
                [SensorType(id=0,name="Temperature",
                            code="T",
                            units="deg.C",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=1,name="Delta Temperature",
                            code="dT",
                            units="deg.C/s",
                            c0=0., c1=1., c2=0., c3=0.),                              
                 SensorType(id=2,name="Humidity",
                            code="RH",
                            units="%",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=3,name="Delta Humidity",
                            code="dRH",
                            units="%/s",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=4,name="Light PAR",
                            code="PAR",
                            units="Lux",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=5,name="Light TSR",
                            code="TSR",
                            units="Lux",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=6,name="Battery Voltage",
                            code="BAT",
                            units="V",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=7,name="Delta Battery Voltage",
                            code="dBT",
                            units="V/s",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=8,name="CO2",
                            code="CO2",
                            units="ppm",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=9,name="Air Quality",
                            code="AQ",
                            units="ppm",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=10,name="VOC",
                            code="VOC",
                            units="ppm",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=11,name="Power",
                            code="POW",
                            units="W",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=12,name="Heat",
                            code="HET",
                            units="W",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=13,name="Duty cycle",
                            code="DUT",
                            units="ms",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=14,name="Error",
                            code="ERR",
                            units="",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=15,name="Power Min",
                            code="PMI",
                            units="w",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=16,name="Power Max",
                            code="PMA",
                            units="w",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=17,name="Power Consumption",
                            code="CON",
                            units="kWh",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=18,name="Heat Energy",
                            code="HEN",
                            units="kWh",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=19,name="Heat Volume",
                            code="HVO",
                            units="L",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=20,name="Power pulses",
                            code="POP",
                            units="p",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=21,name="Window Temperature 1",
                            code="WT1",
                            units="deg.C",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=22,name="Window Temperature 2",
                            code="WT2",
                            units="deg.C",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=23,name="Black Bulb",
                            code="BBT",
                            units="deg.C",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=24,name="Gas Pulse",
                            code="GPL",
                            units="p",
                            c0=0., c1=1., c2=0., c3=0.),
		 SensorType(id=99,name="Gas Consumption",
                            code="Gas",
                            units="kWh",
                            c0=0., c1=1., c2=0., c3=0.),
		SensorType(id=102,name="Outside Temperature",
                            code="ws_temp_out",
                            units="deg.C",
                            c0=0., c1=1., c2=0., c3=0.),   
		SensorType(id=103,name="Outside Humidity",
                            code="ws_hum_out",
                            units="deg.C",
                            c0=0., c1=1., c2=0., c3=0.),    
		SensorType(id=104,name="WS Inside Temperature",
                            code="ws_temp_in",
                            units="deg.C",
                            c0=0., c1=1., c2=0., c3=0.),   
		SensorType(id=105,name="WS Inside Humidity",
                            code="ws_hum_in",
                            units="deg.C",
                            c0=0., c1=1., c2=0., c3=0.),    
                 SensorType(id=106,name="Dew Point",
                            code="ws_dew",
                            units="deg.C",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=107,name="Apparent Temperature",
                            code="ws_apparent_temp",
                            units="deg.C",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=108,name="Wind Gust",
                            code="ws_wind_gust",
                            units="mph",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=109,name="Average Wind Speed",
                            code="ws_wind_ave",
                            units="mph",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=110,name="Wind Direction",
                            code="ws_wind_dir",
                            units="",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=111,name="Wind Chill",
                            code="ws_wind_chill",
                            units="deg.C",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=112,name="Rain Fall",
                            code="ws_rain",
                            units="mm",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=113,name="Absolute Pressure",
                            code="ws_abs_pressure",
                            units="hpa",
                            c0=0., c1=1., c2=0., c3=0.)])
            session.commit()
        session.close()    
                             
    # def update_settings(self):

    #     x = self.setting_session.query(NodeType).filter(NodeType.seq != NodeType.updated_seq).first()
    #     if x is not None:
    #         cm = ConfigMsg()
    #         max_nodetype = self.setting_session.query(func.max(NodeType.id)).one()[0] + 1
    #         max_nodetype = min(max_nodetype, Packets.NODE_TYPE_MAX)
    #         cm.set_typeCount(max_nodetype)
    #         for i in range(max_nodetype):
    #             nt = self.setting_session.query(NodeType).filter(NodeType.id==i).first()
    #             if nt is not None:
    #                 cm.setElement_byType_samplePeriod(i, nt.period)
    #                 if nt.blink:
    #                     cm.setElement_byType_blink(i, 1)
    #                 else:
    #                     cm.setElement_byType_blink(i, 0)
                    
    #                 for j in range(len(nt.configured.a)):
    #                     cm.setElement_byType_configured(i, j, nt.configured.a[j])
    #                 nt.updated_seq = nt.seq
    #             else:
    #                 logger.warning("no NodeType record for type %d - setting some default values" % (i))
    #                 cm.setElement_byType_samplePeriod(i, 300 * 1024) # 300 seconds
    #                 cm.setElement_byType_blink(i,1)
    #                 for j in range(cm.numElements_byType_configured(1)):
    #                     cm.setElement_byType_configured(i, j, 0)

    #         cm.set_special(Packets.SPECIAL)
    #         self.bif.sendMsg(cm)
    #         logger.debug("sending config: %s" % cm)

    #         self.setting_session.commit()

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
        if msg.get_special() != Packets.SPECIAL:
            raise Exception("Corrupted packet - special is %02x not %02x" % (msg.get_special(), Packets.SPECIAL))

        try:
            session = Session()
            t = datetime.utcnow()
            n = msg.getAddr()
            parent = msg.get_ctp_parent_id()
            localtime = msg.get_timestamp()

            node = session.query(Node).get(n)
            locId = None
            if node is None:
                #(houseId,roomId,nodeTypeId) = self.getNodeDetails(n)
                try:
                    session.add(Node(id=n,
                                     locationId=None,
                                     #nodeTypeId=(n / 4096)))
                                     nodeTypeId=None,
                                     )
                                )
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
                logger.info("duplicate packet %d->%d, %d %s" % (n, parent, localtime, str(msg)))
                return
                #raise Exception("duplicate packet: %s, %s" % (str(msg), msg.data))

            ns = NodeState(time=t,
                           nodeId=n,
                           parent=msg.get_ctp_parent_id(),
                           localtime=msg.get_timestamp())
            session.add(ns)

            j = 0
            mask = Bitset(value=msg.get_packed_state_mask())
            state = []
            for i in range(msg.totalSizeBits_packed_state_mask()):
                if mask[i]:
                    v = msg.getElement_packed_state(j)
                    state.append((i,v))
                    r = Reading(time=t,
                                nodeId=n,
                                typeId=i,
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
                      default="debug",
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
      
    # logging.basicConfig(filename="/var/log/ch/BaseLogger.log",
    #                     filemode="a",
    #                     format="%(asctime)s %(levelname)s %(message)s",
    #                     level=lvlmap[options.log_level])

    logging.basicConfig(filename="BaseLogger.log",
                        filemode="a",
                        format="%(asctime)s %(levelname)s %(message)s",
                        level=lvlmap[options.log_level])
    logger.info("Starting BaseLogger with log-level %s" % (options.log_level))
    lm = BaseLogger()
    lm.create_tables()
    
    lm.run()
		
