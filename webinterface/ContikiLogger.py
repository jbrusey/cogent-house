"""
Alternate implmentation of the Baselogger to deal with code
from the Contiki Testbed version of the Application
"""


import logging
import serial
import datetime

import json

import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker


import transaction

import cogentviewer.models as models
import cogentviewer.models.meta as meta

#DBFILE = "sqlite:///test.db"
DBFILE = "mysql://chuser@localhost/testbed"

#Some local defines for sensor types
HOPS = 1001
TX_PWR = 1002
N_COUNT = 1003
CTP_SEQ = 1004
CTP_BEACON = 1005

ADC0 = 1100
ADC1 = 1101
ADC2 = 1102
ADC3 = 1103

ENERGEST_CPU = 2010
ENERGEST_LPM = 2011
ENERGEST_TX = 2012
ENERGEST_RX = 2013
ENERGEST_F_READ = 2014
ENERGEST_F_WRITE = 2015

BAUDRATE=115200 #Telos

#Object for conversion of readings in (str,typeId) form
READLIST = [('hops',HOPS),
            ('txpwr',TX_PWR),
            ('ncount',N_COUNT),
            ('seq_no',CTP_SEQ),
            ('beacon',CTP_BEACON),
            ('e_cpu',ENERGEST_CPU),
            ('e_lpm',ENERGEST_LPM),
            ('e_tx',ENERGEST_TX),
            ('e_rx',ENERGEST_RX),
            ('e_fr',ENERGEST_F_READ),
            ('e_fw',ENERGEST_F_WRITE),
            ('strain',ADC0),
            ('excitation',ADC2),
            ]

class SequenceList(object):
    """Ring buffer to hold recent packets.
    
    Idea here is to hold a fixed number of packet sequence numbers

    """
    def __init__(self, limit = 5):
        self.index = 0
        self.array = [None for x in range(5)]
        self.limit = 5

    def add(self,item):
        """Add a new item to the array"""
        self.array[self.index] = item
        self.index += 1
        if self.index >= 5:
            self.index = 0

    def contains(self,item):
        return item in self.array

    def __str__(self):
        return str(self.array)

class SerialListner(object):
    """Base object for listening on serial"""
    def __init__(self):
        log = logging.getLogger(__name__)
        self.log = log
        log.debug("Starting Serial connection")
        self.con = serial.Serial("/dev/ttyUSB0", 115200, timeout=30)
        self.con.flush()
        log.debug("Starting Database Connection")
        engine = sqlalchemy.create_engine(DBFILE, echo=False)
        #Actually not that fussed in this test code about creating stuff propery

        self.recentpackets = {} #Dictionary of node / packets to keep track of duplicates

        meta.Base.metadata.bind = engine
        #meta.Base.metadata.create_all(engine)

        Session = scoped_session(sessionmaker())
        self.Session = Session

        log.debug("Populating Data")
        #Populate with our intial dataset
        #models.populateData.init_data()

        #And add our local sensor types
        session = self.Session()
        sensortype = models.SensorType(id=HOPS, name="CTP hops")
        session.merge(sensortype)
        sensortype = models.SensorType(id=TX_PWR, name="Tx Power")
        session.merge(sensortype)
        sensortype = models.SensorType(id=N_COUNT, name="Neighbor Count")
        session.merge(sensortype)
        sensortype = models.SensorType(id=CTP_SEQ, name="CTP Sequence")
        session.merge(sensortype)
        sensortype = models.SensorType(id=CTP_BEACON, name="CTP Beacon")
        session.merge(sensortype)

        sensortype = models.SensorType(id=ADC0, name="ADC 0")
        session.merge(sensortype)
        sensortype = models.SensorType(id=ADC1, name="ADC 1")
        session.merge(sensortype)
        sensortype = models.SensorType(id=ADC2, name="ADC 2")
        session.merge(sensortype)
        sensortype = models.SensorType(id=ADC3, name="ADC 3")
        session.merge(sensortype)



        sensortype = models.SensorType(id=2000, name="Neigh0")
        session.merge(sensortype)
        sensortype = models.SensorType(id=2001, name="Neigh1")
        session.merge(sensortype)
        sensortype = models.SensorType(id=2002, name="Neigh2")
        session.merge(sensortype)
        sensortype = models.SensorType(id=2003, name="Neigh3")
        session.merge(sensortype)
        sensortype = models.SensorType(id=2004, name="Neigh4")
        session.merge(sensortype)
        sensortype = models.SensorType(id=2005, name="Neigh5")
        session.merge(sensortype)
        sensortype = models.SensorType(id=2006, name="Neigh6")
        session.merge(sensortype)


        sensortype = models.SensorType(id=ENERGEST_CPU, name="Energest_CPU")
        session.merge(sensortype)
        sensortype = models.SensorType(id=ENERGEST_LPM, name="Energest_LPM")
        session.merge(sensortype)
        sensortype = models.SensorType(id=ENERGEST_TX, name="Energest_TX")
        session.merge(sensortype)
        sensortype = models.SensorType(id=ENERGEST_RX, name="Energest_RX")
        session.merge(sensortype)
        sensortype = models.SensorType(id=ENERGEST_F_READ, name="Energest_F_READ")
        session.merge(sensortype)
        sensortype = models.SensorType(id=ENERGEST_F_WRITE, name="Energest_F_WRITE")
        session.merge(sensortype)



        session.flush()      
        transaction.commit()
        session.close()

    def _convert_temp(self, value):
        """Convert the integer value given for temperature
        into an actual temperature value"""
        val = float(value)
        temp = -39.8 + (0.01*val)
        return temp

    def _convert_hum(self, value):
        """Convert the integer value given for humidity into
        an acutal humidity value"""
        val = float(value)
        hum =  -4 + 0.0405*val - 0.0000028 * (val*val)
        return hum

    def _convert_batt(self, value):
        """Convert the interger battery voltage to a proper value"""
        return value

    def run(self):
        """Single iteration of the mainloop"""
        #Wait for 
        print "Waiting on Data"
        data = self.con.readline()
        log = self.log
        print "Recv ",data
        if data:
            session = self.Session()
            log.debug("Pkt Received> {0}".format(data.strip()))
            if "FOO:" in data:
                now = datetime.datetime.utcnow()
                pktdata = data[4:].strip().replace("'","\"") #Json only likes "'s
                js = json.loads(pktdata) 
              
                
                #First Part is to update the Node / Node State
                nodeid = js["nodeid"]
                msg_seq = js["msg_seq"]
                localtime = js["localtime"]
                parent = js["parent"]

                qry = session.query(models.Node).filter_by(id = nodeid)
                thenode = qry.first()
                if thenode is None:
                    thenode = models.Node(id=nodeid)
                    session.add(thenode)
                    session.flush()
                
                    

                #Check for duplicate packet
                pktlist = self.recentpackets.get(nodeid, SequenceList())
                prev = pktlist.contains(msg_seq)
                if prev:
                    log.warning("Duplicate Packet Detected")
                    return
                else:
                    pktlist.add(msg_seq)
                    self.recentpackets[nodeid] = pktlist

                #Then we can create a nodestate            
                ns = models.NodeState(time=now,
                                      nodeId = nodeid,
                                      localtime = localtime,
                                      seq_num = msg_seq,
                                      parent = parent)

                session.add(ns)


                # ------------- WORK THROUGH READINGS ------------------
                # == Stuff that needs converting ==
                
                val = js.get("temp",None)
                #Falls over on return of 0
                if val:
                    val = self._convert_temp(val)
                    rdg = models.Reading(time=now,
                                         nodeId = nodeid,
                                         typeId = 0,
                                         locationId = thenode.locationId,
                                         value = val)
                    log.debug("Temperature {0}".format(rdg))
                    session.add(rdg)
                

                val = js.get("hum",None)
                if val:
                    val = self._convert_hum(val)
                    rdg = models.Reading(time=now,
                                         nodeId = nodeid,
                                         typeId = 2,
                                         locationId = thenode.locationId,
                                         value = val)
                    #log.debug("Humidity {0}".format(rdg))
                    session.add(rdg)

                val = js.get("battery",None)
                if val:
                    val = self._convert_batt(val)
                    rdg = models.Reading(time=now,
                                         nodeId = nodeid,
                                         typeId = 6,
                                         locationId = thenode.locationId,
                                         value = val)
                    #log.debug("Battery {0}".format(rdg))
                    session.add(rdg)

                # ======== AND SOME AUTOMAGIC CONVERTIONS
                for item in READLIST:
                    val = js.get(item[0],None)
                    #log.debug("Getting item {0} = {1}".format(item,val))
                    if val is None:
                        log.warning("No Such Item")
                        continue
                    rdg = models.Reading(time=now,
                                         nodeId = nodeid,
                                         typeId = item[1],
                                         locationId = thenode.locationId,
                                         value = val)
                    #log.debug("Reading {0}".format(rdg))
                    session.add(rdg)
                    session.flush()


                #Finally deal with any neighbors
                nb = js.get("neighbors",None)
                if nb:
                    for idx,item in enumerate(nb):
                        val = item["address"]
                        rdg = models.Reading(time=now,
                                             nodeId = nodeid,
                                             typeId = 2000+idx,
                                             locationId = thenode.locationId,
                                             value = val)

                        session.add(rdg)                
                        session.flush()

                try:
                    session.flush()
                    session.commit()
                except sqlalchemy.exc.IntegrityError, e:
                    log.warning("Error saving item {0}".format(e))

                                
            session.close()

                        

    def mainloop(self):
        """Run the mainloop continuously"""
        print "Starting Application"
        while True:
            try:
                self.run()
            except KeyboardInterrupt:
                self.log.info("Exiting")
                break
            except ValueError, e:
                self.log.warning("VALUE ERROR {0}".format(e))
                pass
            except sqlalchemy.exc.IntegrityError, e:
                self.log.warning("Intergerty Error {0}".format(e))
                pass
            
        self.con.close()
        self.log.info("Shutdown")
        


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)    
    logging.debug("Starting App")
    sf = SerialListner()
    sf.mainloop()
