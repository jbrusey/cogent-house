#
# ploggDatagather
#
# get data from ploggs via serial port and store in a database.
#
# Ross Wilkins

import logging
connected = False


def connect(n):
    print "Connecting port"

    try:
        p = serial.Serial(port=n, baudrate=19200, timeout=30)
    except serial.SerialException:
        print "Error connecting to port"
        return Null
    print "Port {0} opened at baud({1})".format(p.portstr, p.getBaudrate())

    return p

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
            

def ploggScan():
    pid=[]
    port.write("AT+SN\r")
    #print "Scanning for Nodes, (5Sec sleep)"
    time.sleep(10)
    while port.inWaiting() > 0:
        text = port.readline()
        #check for no errors

        text = text.rstrip('\n\r')
        if text[:5] == "ERROR":
            logging.error("error received from scan:"+text)
            return False
        #check for FFD
        elif text[:4] == "FFD:":
            p=text[4:]
            pid.append(p)
        elif text == 'AT+SN' or text == 'OK' or text == '':
            pass
        else:
            logging.error("unexpected line: "+text)
    return pid

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


if __name__ == '__main__':
    import serial, os
    import time
    from scan import scan
    import binascii  
    import sqlite3 as sqlite
    from optparse import OptionParser,OptionGroup

    #logging.basicConfig(filename='plogg1.log',
    #                    filemode='a',
    #                    format='%(asctime)s %(levelname)s %(message)s')
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("plogg")

    logger.info("starting plogg data gather")

    parser = OptionParser()

    group = OptionGroup(parser,"Sets Sampling Rate:","Set the sampling rate of the plogg sensors")
    
    group.add_option("-r","--rate",dest="srate",help="Set plogg sampling rate in seconds")

    parser.add_option_group(group)
    
    (options, args) = parser.parse_args()


    ploggId=[]
    #print "Found ports:"

    #if(os.name == "posix"):
    #    port = connect("/dev/ttyUSB0")
    #else:
    #    print "Found ports:"
    #    for s in scan():
    #        print "{0[0]:0>3d} - {0[1]}".format(s)
    return


    #scan for ploggs try 3 times just in case of errors
    for s in range(3):
       ploggId=ploggScan()
       if ploggId != False:        
           break

    logger.debug("List of Plogg ID's")
    logger.debug(ploggId)

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
                logger.debug("Dealing with PID {0}".format(pid))
                sid =str(pid)
                logger.debug("Sending {0}".format("AT+UCAST:"+sid+"=yv\r"))
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


