#
# ploggDatagather
#
# get data from ploggs via serial port and store in a database.
#
# Ross Wilkins

#DB_STRING = "mysql://test_user:test_user@127.0.0.1/testStore"
#DB_STRING = "sqlite:///test.db"
DB_STRING = "mysql://chuser@localhost/localCh"

import logging
connected = False


import serial, os
import time
from scan import scan
import binascii  
import sqlite3 as sqlite
from optparse import OptionParser,OptionGroup


import serial.tools.list_ports as list_ports

from datetime import datetime

#Do The Database Magic
import sqlalchemy

import cogent
import cogent.base.model as models
import cogent.base.model.meta as meta
import cogent.base.model.populateData as populateData

#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)

# def connect(n):
#     print "Connecting port"

#     try:
#         p = serial.Serial(port=n, baudrate=19200, timeout=30)
#     except serial.SerialException:
#         print "Error connecting to port"
#         return Null
#     print "Port {0} opened at baud({1})".format(p.portstr, p.getBaudrate())

#     return p

#Map Node Addresses to Serial Numbers
NODEMAP = {"000D6F000026B366":220295,
           "000D6F0000263A0F":200299,
           "0021ED00000463EF":200294,
           "0021ED0000035BC6":200301,
           "000D6F000026D4D0":200302,
           }
           
def toHex(s):
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
        lst.append(hv)
    return reduce(lambda x,y:x+y, lst)

def hexArray(s):
    shex=[]
    word=""
    for i in s:
        if len(word)==0:
            word+=i
        else:
            word+=i
            shex.append(word)
            word=""
    return shex

def uptimeProcess(d):
    t=time.strftime('%H:%M:%S', time.gmtime(d))
    return t           

class PloggCollector(object):
    """Class to collect data from Plogg Objects"""
    def __init__(self,sampleRate = 60,usbPort = None):
        """Initialise plogg collection object

        :var sampleRate: Sample Rate in Seconds
        :var usbPort: Serial port to connect to
        """
        self.log = logging.getLogger("PloggCollector")
        log = self.log

        #And Format the Log output a little nicer
        ch = logging.StreamHandler()
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        log.addHandler(ch)

        log.debug("initialising Plogg Data Gatherer")

        log.debug("SampleRate")
        self.sampleRate = sampleRate

        self.nodeMap = {}

        #Attempt to connect to the Dongle
        self.connect(usbPort)
        
        #Then we can sort out the database
        engine = sqlalchemy.create_engine(DB_STRING)
        #Create Models and Populate any Missing Base Data
        models.initialise_sql(engine)
        populateData.init_data()      

        #Scan for Ploggs
        #ploggList = self.ploggScan()
        #self.ploggList = ploggList
        self.ploggList = []
       
     
    def connect(self,thePort):
        """Connect to a Serial Port

        :var thePort: Id of Port to connect to
        :return: true on success, false otherwis
        """
        try:
            p = serial.Serial(port=thePort, baudrate=19200, timeout=10)
        except serial.SerialException:
            self.log.warning("Error connecting to port")
            return False
        self.log.debug("Port {0} opened at baud({1})".format(p.portstr, p.getBaudrate()))

        self.port = p
        return True

    def ploggScan(self,pid = []):
        """Scan for Plogg Nodes

        :var pid: List of Existing Ploggs
        """
        port = self.port        
        log = self.log

        log.debug("Scanning for Nodes") 

        port.write("AT+SN\r")
        #print "Scanning for Nodes, (5Sec sleep)"
        time.sleep(10)
        while port.inWaiting() > 0:
            text = port.readline()
            #check for no errors
            #log.debug("Reply Text {0}".format(text))
            text = text.rstrip('\n\r')
            if text[:5] == "ERROR":
                log.error("error received from scan:"+text)
                return False
            #check for FFD
            elif text[:4] == "FFD:":
                p=text[4:]
                log.debug("Plogg Id: {0} Discovered".format(p))
                if not p in pid:
                    pid.append(p)
            elif text == 'AT+SN' or text == 'OK' or text == '':
                pass
            else:
                log.error("unexpected line: "+text)

        return pid

    def run(self):
        """Run an iteration of the main loop"""
        log = self.log
        log.debug("Start Loop")
        
        pList = self.ploggList
        #Scan for new Ploggs
        pList = [] #Reset the list of ploggs each time
        pList = self.ploggScan(pList)

        log.info("Gathering Data for {0}".format(pList))
        for ploggId in pList:
            log.debug("-"*70)
            log.debug("Running Data Gathering for {0}".format(ploggId))
            values = self.ploggQuery(ploggId)
            log.debug("Values are {0}".format(values))
            if values:
                self.saveData(ploggId,values)
            

    def loop(self):
        """Run forever"""
        log = self.log

        log.debug("Entering Main Loop")
        while True:
            try:
                startTime = time.time()
                self.run()
                endTime = time.time()
                #Work out how long to sleep for
                loopTime = endTime - startTime
                sleepTime = self.sampleRate - loopTime
                log.info("Mainloop complete in {0} Sleeping for {1}".format(loopTime,sleepTime))
                if sleepTime > 0:
                    time.sleep(sleepTime)
            except KeyboardInterrupt:
                log.info("Exiting...")
                break

        #Shut Stuff Down Nicely
        self.port.close()
        log.info("Done")


    def ploggQuery(self,ploggId):
        """Ask a plogg for information

        :var ploggId: Hex Address of this Plogg
        """
        
        port = self.port
        log = self.log
        dFound = False
        readings= None
        failCount = 0
        sid =str(ploggId)
        port.write("AT+UCAST:"+sid+"=yv\r")
        time.sleep(2.5)  # really need to read with a timeout
        n = port.inWaiting()
        if n==0 or n==28:
            log.info("No Data for Node {0}".format(ploggId))
            port.flushInput()
            return 
        else:
            data=""
            while n != 0:
                log.debug(" --> Reading from Serial {0}".format(n))
                text = port.readline()
                #text = port.read(n)
                log.debug(" --> Read Complete >{0}<".format(text.strip()))
                if n == 45:
                    log.warning("Read of 45")
                    return

                if (text.count("NACK:")>0):
                    log.warning("NACK Recieved")
                    return
                if (text.strip() == ""):
                    log.debug("No Text Returned")
                    failCount += 1
                    if failCount == 5:
                        log.warning("Fail Count Reached")
                if(text.count(sid+",")>0 or dFound==True):
                    dFound=True
                    data=data+text
                    n=port.inWaiting()
                    log.debug("{0} Bytes Remain".format(n))
                #Otherwise assume there is a failiure in fteching the data
                #else:
                #    log.info("No Response from Node")
                #    log.debug("{0}".format(text.strip()))
                #    n=port.inWaiting()
                #    port.flushInput()
                #    return
            if len(data)>0:
                #self.ploggDebug(data)
                log.debug("Readings Collected: Parsing")
                readings = self.ploggParseValue(data)
                log.debug("Values for {0}: {1}".format(ploggId,readings))
                dFound=False

                return readings
        pass

    def ploggParseValue(self,text):
        """
        Parse useful data from plogg reply string.

        """
        log = self.log
        data = toHex(text)
        #I assume we Zap addresses etc here
        data = data[52:]
        ha = hexArray(data)

        if len(ha) == 57:
            #Plogg Uptime
            #Get Consumption
            #RMS Current
            #System Uptime
            timestamp = datetime.utcnow()
            watts=(float(int(str(ha[7]+ha[8]+ha[9]+ha[10]),16))/1000)
            kwhCon=(float(int(str(ha[15]+ha[16]+ha[17]+ha[18]),16))/10000)
            rmsc=(float(int(str(ha[27]+ha[28]+ha[29]+ha[30]),16))/1000)
            #log.debug("Time {0} Watts {1} KwH {2} A {3}".format(timestamp,watts,kwhCon,rmsc))
            return (timestamp,watts,kwhCon,rmsc)
        else:
            log.warning("Invalid packet Size")
        pass

    def saveData(self,nodeId,values):
        """Save a reading in the Database

        :var nodeId: String Containing the Current Cost Node Id
        :var values: Tuple containing sensor values as returned by ploggParseValue
        """
        log = self.log
        log.debug("Saving data for {0} {1}".format(nodeId,values))
        session = meta.Session()
        mappedId = NODEMAP[nodeId]
        theNode = session.query(models.Node).filter_by(id = mappedId).first()
        
        #Fetch Sensor Types
        wattSensor = session.query(models.SensorType).filter_by(name="Plogg Watts").first()
        log.debug("Watt Sensor {0}".format(wattSensor))
        kWhSensor = session.query(models.SensorType).filter_by(name="Plogg kWh").first()
        log.debug("kW Sensor {0}".format(kWhSensor))
        currentSensor = session.query(models.SensorType).filter_by(name="Plogg Current").first()
        log.debug("A Sensor {0}".format(currentSensor))
                                                          

        #Create if it doesnt Exist
        if not theNode:
            log.info("Node {0} / {1} does not exist, Creating".format(nodeId,mappedId))
            theNode = models.Node(id=mappedId,
                                  locationId=None)
            session.add(theNode)
            session.flush()
            log.debug("Node is {0}".format(theNode))
            #And we need to add a set of sensors
            for item in [wattSensor,kWhSensor,currentSensor]:
                theSensor = models.Sensor(sensorTypeId=item.id,
                                          nodeId = theNode.id,
                                          calibrationSlope = 1.0,
                                          calibrationOffset = 0.0)
                session.add(theSensor)
            session.flush()
        
        sampleTime,sampleWatts,samplekWh,sampleCurrent = values
        #Then Add the Readings
        theReading = models.Reading(time=sampleTime,
                                    nodeId = theNode.id,
                                    location = theNode.locationId,
                                    typeId = wattSensor.id,
                                    value = sampleWatts)
        session.add(theReading)
        
        theReading = models.Reading(time=sampleTime,
                                    nodeId = theNode.id,
                                    location = theNode.locationId,
                                    typeId = kWhSensor.id,
                                    value = samplekWh)
        session.add(theReading)

        theReading = models.Reading(time=sampleTime,
                                    nodeId = theNode.id,
                                    location = theNode.locationId,
                                    typeId = currentSensor.id,
                                    value = sampleCurrent)
        session.add(theReading)
        
        #And add a nodeState
        theNodeState = models.NodeState(time=sampleTime,
                                        nodeId=theNode.id,
                                        parent=theNode.id,
                                        localtime=sampleTime)

        session.add(theNodeState)
        session.flush()
        session.commit()
        session.close()

    def ploggDebug(self,text):
        """
        Parse the Data from a plogg into something useful and output it on the
        debug stream
        
        :var text: Data String to Parse
        """
        log = self.log
        data=toHex(text)
        log.debug("Hex {0}".format(data))
        data=data[52:]
        ha=hexArray(data)
        log.debug(ha)
        if len(ha)==57:
            #print "Node:",sid
            #print "Device Time", ha[1],ha[2],ha[3],ha[4] #is incorrect just use current time
            device_time= time.ctime()
            log.debug("Device Time {0}".format(device_time))
           
            ploggup = uptimeProcess((float(int(str(ha[5]+ha[6]),16))))
            log.debug("Plogg Uptime {0}".format(ploggup)) # strange one ignore for now, not really improtant

            watts=(float(int(str(ha[7]+ha[8]+ha[9]+ha[10]),16))/1000)
            log.debug("Watts {0}".format(watts))

            kwhGen=(float(int(str(ha[11]+ha[12]+ha[13]+ha[14]),16))/10000)
            log.debug("kWh Generated {0}".format(kwhGen))

            kwhCon=(float(int(str(ha[15]+ha[16]+ha[17]+ha[18]),16))/10000)
            log.debug("kWh Consumed {0}".format(kwhCon))

            freq=(float(int(str(ha[19]+ha[20]+ha[21]+ha[22]),16))/10)
            log.debug("Frequency {0}".format(freq))

            rmsv=(float(int(str(ha[23]+ha[24]+ha[25]+ha[26]),16))/1000)
            log.debug("RMS Voltage {0}".format(rmsv))

            rmsc=(float(int(str(ha[27]+ha[28]+ha[29]+ha[30]),16))/1000)
            log.debug("RMS Current {0}".format(rmsc))

            #check first byte ha[35] for 80 rest to float then /1000
            if int(ha[35])==80:
                #deals ith negative values
                rp=(float(int(str(ha[36]+ha[37]+ha[38]),16))/1000)
                rp=rp*-1
                log.debug("Reactive Power {0}".format(rp))
            else:
                rp=(float(int(str(ha[36]+ha[37]+ha[38]),16))/1000)
                log.debug("Reactive Power {0}".format(rp))

            varGen=(float(int(str(ha[39]+ha[40]+ha[41]+ha[42]),16))/10000)
            log.debug("VARh Generated {0}".format(varGen))

            varCon=(float(int(str(ha[43]+ha[44]+ha[45]+ha[46]),16))/10000)
            log.debug("VARh Consumed {0}".format(varCon))

            phase=(float(int(str(ha[47]+ha[48]+ha[49]+ha[50]),16)))
            log.debug("Phase Angle {0}".format(phase))

            equipup =uptimeProcess((float(int(str(ha[51]+ha[52]+ha[53]+ha[54]),16))/100))
            log.debug("Equip Up Time {0}".format(equipup))
            #print "\n\n"

if __name__ == '__main__':

    #logging.basicConfig(filename='plogg1.log',
    #                    filemode='a',
    #                    format='%(asctime)s %(levelname)s %(message)s')

    #log = logging.getLogger("plogg")

    logging.info("starting plogg data gather")

    parser = OptionParser()

    group = OptionGroup(parser,"Sets Sampling Rate:","Set the sampling rate of the plogg sensors")
    
    group.add_option("-r","--rate",dest="srate",help="Set plogg sampling rate in seconds",default=60,type='int')
    parser.add_option_group(group)


    group = OptionGroup(parser,"Sets Serial Port for USB Dongle")
    group.add_option("-p","--port",dest="port",help="Set Usb Port")
    parser.add_option_group(group)
    
    (options, args) = parser.parse_args()


    logging.debug("Options {0}".format(options))
    logging.debug("Args {0}".format(args))

    #sys.exit(0)
    ploggId=[]
    #print "Found ports:"
    
    #If a port is specified
    if options.port:
        thePort = options.port
    else:
        #Otherwise Scan for USB Dongle
        logging.debug("Scanning for Dongle")
        #We know the Dongle will be a USB Device and have the following vendor Id
        usbPorts = list_ports.grep('USB VID:PID=10c4:8293 SNR=010010C5')

        #There should only be one port here
        logging.debug("USB Ports {0}".format(usbPorts))
        usbPorts = list(usbPorts)
        if len(usbPorts) != 1:
            logging.warning("Error detecting usb Dongle")
            sys.exit(0)
        else:
            logging.debug("USB Port Scan Results: {0}".format(usbPorts))
            thePort = usbPorts[0][0]
   
    #Create Plogg Object
    plogger = PloggCollector(options.srate,thePort)
    #plogger.run()
    plogger.loop()
