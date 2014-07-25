"""
Alternate implmentation of the Baselogger to deal with code
from the Contiki Testbed version of the Application
"""


import logging
import serial
import datetime

import sqlalchemy

import cogent.base.model as models
import cogent.base.model.meta as meta

#DBFILE = "sqlite:///test.db"
DBFILE = "mysql://chuser@localhost/testbed"

#Some local defines for sensor types
HOPS = 1001
TX_PWR = 1002
N_COUNT = 1003
CTP_SEQ = 1004

class SerialListner(object):
    """Base object for listening on serial"""
    def __init__(self):
        log = logging.getLogger(__name__)
        self.log = log
        log.debug("Starting Serial connection")
        self.con = serial.Serial("/dev/ttyUSB0", 115200, timeout=10)
        log.debug("Starting Database Connection")
        engine = sqlalchemy.create_engine(DBFILE, echo=False)
        #Actually not that fussed in this test code about creating stuff propery

        meta.Base.metadata.bind = engine
        meta.Base.metadata.create_all(engine)

        meta.Session.configure(bind=engine)

        log.debug("Populating Data")
        #Populate with our intial dataset
        models.populateData.init_data()

        #And add our local sensor types
        session = meta.Session()
        sensortype = models.SensorType(id=HOPS, name="CTP hops")
        session.merge(sensortype)
        sensortype = models.SensorType(id=TX_PWR, name="Tx Power")
        session.merge(sensortype)
        sensortype = models.SensorType(id=N_COUNT, name="Neighbor Count")
        session.merge(sensortype)
        sensortype = models.SensorType(id=CTP_SEQ, name="CTP Sequence")
        session.merge(sensortype)
        sensortype = models.SensorType(id=2000, name="Neigh0")
        session.merge(sensortype)
        sensortype = models.SensorType(id=2001, name="Neigh1")
        session.merge(sensortype)
        sensortype = models.SensorType(id=2002, name="Neigh2")
        session.merge(sensortype)
        sensortype = models.SensorType(id=2003, name="Neigh3")
        session.merge(sensortype)
        
        session.flush()
        session.commit()
        
        

    def run(self):
        """Single iteration of the mainloop"""
        #Wait for 
        data = self.con.readline()
        log = self.log
        if data:
            session = meta.Session()
            log.debug("> {0}".format(data.strip()))
            if "PKT:" in data:
                now = datetime.datetime.now()
                pktdata = data.strip().split(":") #Get the main packet data
                pktitems = [int(x) for x in pktdata[1].split(",")]
                log.debug(">>PKT. {0}".format(pktitems))
                
                (nodeid,
                 time,
                 ctp_seq,
                 hops,
                 tx_pwr,
                 msg_seq,
                 parent,
                 n_count,
                 temp,
                 hum) = pktitems

                #Temperature / Humidity conversion
                temp = float(temp)
                temp = -39.6 + 0.01*temp
                hum = float(hum)
                hum = -4 + 0.0405*hum - 0.0000028 * (hum*hum)

                qry = session.query(models.Node).filter_by(id = nodeid)
                thenode = qry.first()
                if thenode is None:
                    log.info("No such node {0}".format(nodeid))
                    thenode = models.Node(id=nodeid)
                    session.add(thenode)
                    session.flush()
                
                #Then we can create a nodestate            
                ns = models.NodeState(time=now,
                                      nodeId = nodeid,
                                      localtime = time,
                                      seq_num = msg_seq,
                                      parent = parent)
                session.add(ns)

                #And Readings
                rdg = models.Reading(time=now,
                                     nodeId = nodeid,
                                     typeId = HOPS,
                                     locationId = thenode.locationId,
                                     value = hops)
                session.add(rdg)

                rdg = models.Reading(time=now,
                                     nodeId = nodeid,
                                     typeId = TX_PWR,
                                     locationId = thenode.locationId,
                                     value = tx_pwr)
                session.add(rdg)

                rdg = models.Reading(time=now,
                                     nodeId = nodeid,
                                     typeId = N_COUNT,
                                     locationId = thenode.locationId,
                                     value = n_count)
                session.add(rdg)

                rdg = models.Reading(time=now,
                                     nodeId = nodeid,
                                     typeId = CTP_SEQ,
                                     locationId = thenode.locationId,
                                     value = ctp_seq)
                session.add(rdg)

                #Temperature
                rdg = models.Reading(time=now,
                                     nodeId = nodeid,
                                     typeId = 0,
                                     locationId = thenode.locationId,
                                     value = temp)
                session.add(rdg)

                rdg = models.Reading(time=now,
                                     nodeId = nodeid,
                                     typeId = 2,
                                     locationId = thenode.locationId,
                                     value = hum)
                session.add(rdg)
                session.commit()

                #Now neighbor table info
                print pktdata
                if len(pktdata) > 2:
                    neighinfo = pktdata[2:]
                    log.info("Neighbor Table is {0}".format(neighinfo))
                    for idx,item in enumerate(neighinfo):
                        print item, idx
                        vals = item.split(",")
                        rdg = models.Reading(time=now,
                                             nodeId = nodeid,
                                             typeId = 2000+idx,
                                             locationId = thenode.locationId,
                                             value = vals[0])
                        session.add(rdg)
                session.commit()
                        

    def mainloop(self):
        """Run the mainloop continuously"""
        while True:
            try:
                self.run()
            except KeyboardInterrupt:
                self.log.info("Exiting")
                break
            
        self.con.close()
        self.log.info("Shutdown")
        


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)    
    logging.debug("Starting App")
    sf = SerialListner()
    sf.mainloop()
