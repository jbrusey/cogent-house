#
# ploggDatagather
#
# get data from ploggs via serial port and store in a database.
#
# Ross Wilkins

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

def disconnect(p):
    print "disconnecting port {0}".format(p.portstr)
    
    p.close()
    
    print "Port {0} disconnected".format(p.portstr)

def tidy(p):
    disconnect(p)

def allindices(string, sub="FFD:", listindex=[], offset=0):
    i = string.find(sub, offset)
    while i >= 0:
        listindex.append(i)
        i = string.find(sub, i + 1)
    return listindex

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
            

# def ploggScan():
#     pid=[]
#     port.write("AT+SN\r")
#     #print "Scanning for Nodes, (5Sec sleep)"
#     time.sleep(10)
#     while port.inWaiting() > 0:
#         text = port.readline()
#         #check for no errors

#         text = text.rstrip('\n\r')
#         if text[:5] == "ERROR":
#             logging.error("error received from scan:"+text)
#             return False
#         #check for FFD
#         elif text[:4] == "FFD:":
#             p=text[4:]
#             pid.append(p)
#         elif text == 'AT+SN' or text == 'OK' or text == '':
#             pass
#         else:
#             logging.error("unexpected line: "+text)
#     return pid

def processData(text):
    #find 3d this is where the interesting data starts
    data=toHex(text)
    data=data[52:]
    ha=hexArray(data)

    if len(ha)==57:
        print "Node:",sid
        #print "Device Time", ha[1],ha[2],ha[3],ha[4] #is incorrect just use current time
        device_time= time.ctime()
        print "Device Time",device_time
    
        #ploggup = uptimeProcess((float(int(str(ha[5]+ha[6]),16))))
        #print "Plogg Uptime",ploggup # strange one ignore for now, not really improtant
                                
        watts=(float(int(str(ha[7]+ha[8]+ha[9]+ha[10]),16))/1000)
        print "Watts",watts
        
        kwhGen=(float(int(str(ha[11]+ha[12]+ha[13]+ha[14]),16))/10000)
        print "kWh Generated",kwhGen
        
        kwhCon=(float(int(str(ha[15]+ha[16]+ha[17]+ha[18]),16))/10000)
        print "kWh Consumed",kwhCon
        
        freq=(float(int(str(ha[19]+ha[20]+ha[21]+ha[22]),16))/10)
        print "Frequency",freq
        
        rmsv=(float(int(str(ha[23]+ha[24]+ha[25]+ha[26]),16))/1000)
        print "RMS Voltage",rmsv
    
        rmsc=(float(int(str(ha[27]+ha[28]+ha[29]+ha[30]),16))/1000)
        print "RMS Current",rmsc
    
        #check first byte ha[35] for 80 rest to float then /1000
        if int(ha[35])==80:
            #deals ith negative values
            rp=(float(int(str(ha[36]+ha[37]+ha[38]),16))/1000)
            rp=rp*-1
            print "Reactive Power",rp
        else:
            rp=(float(int(str(ha[36]+ha[37]+ha[38]),16))/1000)
            print "Reactive Power",rp

        varGen=(float(int(str(ha[39]+ha[40]+ha[41]+ha[42]),16))/10000)
        print "VARh Generated",varGen
    
        varCon=(float(int(str(ha[43]+ha[44]+ha[45]+ha[46]),16))/10000)
        print "VARh Consumed",varCon
    
        phase=(float(int(str(ha[47]+ha[48]+ha[49]+ha[50]),16)))
        print "Phase Angle",phase
    
        equipup =uptimeProcess((float(int(str(ha[51]+ha[52]+ha[53]+ha[54]),16))/100))
        print "Equip Up Time",equipup
        print "\n\n"
            
        # try block needed with rollback
        cursor.execute('INSERT INTO data VALUES ("'+ str(sid) +'","'+ device_time +'",'+str(watts)+','+str(kwhCon)+','+str(kwhGen)+','+str(freq)+','+str(rmsv)+','+str(rmsc)+','+str(rp)+','+str(varGen)+','+str(varCon)+','+str(phase)+',"'+str(equipup)+'")')
        connection.commit()
        
        return True

class PloggCollector(object):
    """Class to collect data from Plogg Objects"""
    def __init__(self,sampleRate = 60,usbPort = None):
        """Initialise plogg collection object

        :var sampleRate: Sample Rate in Seconds
        :var usbPort: Serial port to connect to
        """
        self.log = logging.getLogger("PloggCollector")
        log = self.log
        log.debug("initialising Plogg Data Gatherer")

        self.sampleRate = sampleRate

        #Attempt to connect to the Dongle
        self.connect(usbPort)
        
        #We also need to write some code to connect to the Database here
      

        #Scan for Ploggs
        ploggList = self.ploggScan()
        self.ploggList = ploggList

        #And that should be that

     
    def connect(self,thePort):
        """Connect to a Serial Port

        :var thePort: Id of Port to connect to
        :return: true on success, false otherwis
        """
        try:
            p = serial.Serial(port=thePort, baudrate=19200, timeout=30)
        except serial.SerialException:
            self.log.warning("Error connecting to port")
            return False
        self.log.debug("Port {0} opened at baud({1})".format(p.portstr, p.getBaudrate()))

        self.port = p
        return True

    def ploggScan(self):
        """Scan for Plogg Nodes"""
        port = self.port        
        log = self.log

        log.debug("Scanning for Nodes")
        
        pid=[]
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
                pid.append(p)
            elif text == 'AT+SN' or text == 'OK' or text == '':
                pass
            else:
                log.error("unexpected line: "+text)

        return pid


    def run(self):
        """Run an iteration of the main loop"""

        log = self.log

        for ploggId in self.ploggList:
            log.debug("-"*70)
            log.debug("-"*70)
            log.debug("Running Data Gathering for {0}".format(ploggId))
            self.ploggQuery(ploggId)

    def ploggQuery(self,ploggId):
        """Ask a plogg for information

        :var ploggId: Hex Address of this Plogg
        """
        
        port = self.port
        log = self.log
        dFound = False

        sid =str(ploggId)
        port.write("AT+UCAST:"+sid+"=yv\r")
        time.sleep(2.5)  # really need to read with a timeout
        n = port.inWaiting()
        if n==0 or n==28:
            port.flushInput()
            return 
        else:
            data=""
            while n != 0:
                text = port.readline()
                if(text.count(sid+",")>0 or dFound==True):
                    dFound=True
                    data=data+text
                    n=port.inWaiting()
                    
            if len(data)>0:
                #self.ploggDebug(data)
                readings = self.ploggParseValue(data)
                log.debug("Values for {0}: {1}".format(ploggId,readings))
                dFound=False

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
            timestamp = datetime.now()
            watts=(float(int(str(ha[7]+ha[8]+ha[9]+ha[10]),16))/1000)
            kwhCon=(float(int(str(ha[15]+ha[16]+ha[17]+ha[18]),16))/10000)
            rmsc=(float(int(str(ha[27]+ha[28]+ha[29]+ha[30]),16))/1000)
            #log.debug("Time {0} Watts {1} KwH {2} A {3}".format(timestamp,watts,kwhCon,rmsc))
            return (timestamp,watts,kwhCon,rmsc)
            
        pass

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
            print "\n\n"

if __name__ == '__main__':

    #logging.basicConfig(filename='plogg1.log',
    #                    filemode='a',
    #                    format='%(asctime)s %(levelname)s %(message)s')

    #log = logging.getLogger("plogg")

    logging.info("starting plogg data gather")

    parser = OptionParser()

    group = OptionGroup(parser,"Sets Sampling Rate:","Set the sampling rate of the plogg sensors")
    
    group.add_option("-r","--rate",dest="srate",help="Set plogg sampling rate in seconds")
    parser.add_option_group(group)


    group = OptionGroup(parser,"Sets Serial Port for USB Dongle")
    group.add_option("-p","--port",dest="port",help="Set Usb Port")
    parser.add_option_group(group)
    
    (options, args) = parser.parse_args()


    logging.debug("Options {0}".format(options))
    logging.debug("Args {0}".format(args))

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
        usbPorts = list(usbPorts)
        if len(usbPorts) != 1:
            logging.warning("Error detecting usb Dongle")
            sys.exit(0)
        else:
            logging.debug("USB Port Scan Results: {0}".format(usbPorts))
            thePort = usbPorts[0][0]
   
    #Create Plogg Object
    plogger = PloggCollector(options.srate,thePort)
    plogger.run()

    sys.exit(0)
    port = connect(thePort)


    logging.debug("Scanning for Ploggs")
    #scan for ploggs try 3 times just in case of errors
    for s in range(3):
       ploggId=ploggScan()
       if ploggId != False:        
           break

    logging.debug("List of Plogg ID's")
    logging.debug(ploggId)

    #create db
    connection = sqlite.connect('plogg.db')
    
    cursor = connection.cursor()

    try:
        cursor.execute('CREATE TABLE plogg (pid String PRIMARY KEY)')
        cursor.execute('CREATE TABLE data (pid TEXT, Data_Time TEXT, Watts REAL, kWh_Consumed REAL, kWh_Generated REAL, Frequency REAL, RMS_Voltage REAL, RMS_Current REAL, Reactive_Power REAL, VARh_Generated REAL, VARh_Consumed REAL, Phase_Angle REAL, Equip_Up_Time TEXT);')
    except:
        print "Tables already Exist\n"


    #store all found id's try/except to deal with id's which have prev been found
    for pid in ploggId:
        try:
            cursor.execute('INSERT INTO plogg VALUES ("'+str(pid)+'")')
            connection.commit()
        except:
            continue

    if options.srate:
        sampleRate=float(options.srate)
        print "Sampling rate set to: "+str(sampleRate)+"s"
    else:
        sampleRate=60.0
        print "Sampling rate set to: "+str(sampleRate)+"s"

    #infinate loop to collate data
    dFound=False
    try:
        lastRun=time.time()
        while True:
            #loop through plogg id's
            for pid in ploggId:
                # request data from plogg
                logging.debug("Dealing with PID {0}".format(pid))
                sid =str(pid)
                logging.debug("Sending {0}".format("AT+UCAST:"+sid+"=yv\r"))
                port.write("AT+UCAST:"+sid+"=yv\r")
                time.sleep(2.5)  # really need to read with a timeout
                n = port.inWaiting()
                if n==0 or n==28:
                    port.flushInput()
                    continue
                else:
                    data=""
                    while n != 0:
                        text = port.readline()
                        if(text.count(sid+",")>0 or dFound==True):
                            dFound=True
                            data=data+text
                        n=port.inWaiting()
                
                if len(data)>0:
                    processData(data)
                dFound=False
    
            ploggId=[]
            #scan for ploggs try 3 times just in case of errors                                                             
            for s in range(3):
                ploggId=ploggScan()
                if ploggId != False:
                    break
            print ploggId

            runTime=time.time()-lastRun
            sleepTime=sampleRate-runTime
            if sleepTime > 0:
		print "sleep", sleepTime,"\n\n"
                time.sleep(sleepTime)
            lastRun=time.time()
        tidy(port)
                
    except KeyboardInterrupt:
        tidy(port)


    #disconnect com port
    tidy(port)
    port_no = raw_input("Exit: ")


