import tos
import time
import sqlite3 as sqlite
import struct
import optparse
import subprocess
import pyparsing


def detectMote():
	#Open Subprocess to run motelist, if args put [<name>,arg]
	proc = subprocess.Popen(['motelist'],stdout=subprocess.PIPE)
	#Interact from the process As Array [0] == out [1] == in
	output = proc.communicate()[0]

	#Strip out what we want#
	regex = "/dev/ttyUSB" + pyparsing.Word(pyparsing.nums)
	found =  regex.searchString(output)
	#Hope we dont have more than one device connected
	if found:
		usbDev = "/dev/ttyUSB%s" %found[0][-1]
		return usbDev
	else:
		return False
	

if __name__ == "__main__":
    #Parse some command line options
    
    parser = optparse.OptionParser()
    parser.add_option("-d",
		      "--database",
		      dest="database",
		      help="Database Name",
		      default="Spanish.db")
    
    parser.add_option("-o",
		      "--autoOff",
		      dest="autodetect",
		      help="Dont Attempt autotetection of TTY",
		      action="store_false",
		      default=True
		      )
    parser.add_option("-u",
		      "--usb",
		      dest="usb",
		      help="USB tty",
		      default="USB0",
		      )
    

    #Get options (Above) args (Non Specified)
    options,args = parser.parse_args()

    dbName = options.database

    autodetect = options.autodetect
    if autodetect:
	    usbDev = detectMote()
	    if not usbDev:
		    usbDev = "/dev/tty%s" %(options.usb)
    else:
	    usbDev = "/dev/tty%s" %(options.usb)

    link = tos.SimpleSerialAM(usbDev,115200,flush=True)

    count=0
    while True:
#        try:
	    pkt = link.read_am()
	    ts = time.ctime()
	    if pkt.type == 10:
		count=count+1
		print "Count: ",count

    print "Done"

    print "Closing... ",
    allFil.close()
    modelFil.close()
    baseFil.close()
    link.close()
    print "Done"

