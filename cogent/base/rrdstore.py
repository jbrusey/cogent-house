"""
Class to store data from the cogent-house in RRD tables.
"""
import os
import os.path
import time
import datetime

import logging
LOG = logging.getLogger("RRDStore")
LOG.setLevel(logging.INFO)


import pyrrd.rrd as rrd

RRDPATH = "/usr/share/cogent-house/"
#RRDPATH "

class RRDStore(object):
    """
    Store data from nodes in an RRD
    """
    def __init__(self,nodeId,typeId,locationId,startTime = None):
        #thisPath = os.path.join(
        rrdname = "{0}_{1}_{2}.rrd".format(nodeId,locationId,typeId)
        LOG.debug("RRD File {0}".format(rrdname))
        
        rrdfd = os.path.join(RRDPATH,rrdname)

        LOG.debug("Full Path {0}".format(rrdfd))

        #Check if this exists
        if os.path.exists(rrdfd):
            #Open the RRD file
            LOG.debug("RRD file exists")
            #pass
            self.rrd = rrd.RRD(rrdfd, mode="r")
        else:
            LOG.debug("No such RRD, Creating")

            #Data Sources
            datasources = []
            #We Only need a single datasource
            ds = rrd.DataSource(dsName="reading",dsType="GAUGE",heartbeat=600)
            datasources.append(ds)
            
            #And archives
            archives = []
            #(288 samples per day)
            archives.append(rrd.RRA(cf="AVERAGE", xff=0.5, steps=1, rows=8064))  #5 Minute Samples for 1 month 
            archives.append(rrd.RRA(cf="AVERAGE", xff=0.5, steps=12, rows=2016)) #Every Hour for 3 months
            archives.append(rrd.RRA(cf="MIN", xff=0.5, steps=12, rows=2016)) 
            archives.append(rrd.RRA(cf="MAX", xff=0.5, steps=12, rows=2016)) 
            archives.append(rrd.RRA(cf="AVERAGE", xff=0.5, steps=288, rows=365)) #Every Day for a Year
            archives.append(rrd.RRA(cf="MIN", xff=0.5, steps=288, rows=365))
            archives.append(rrd.RRA(cf="MAX", xff=0.5, steps=288, rows=365))

            #Ensure URC and offset
            if startTime:
                if type(startTime) == datetime.datetime:
                    now = int(time.mktime(startTime.utctimetuple()) - 300)
                else:
                    now = startTime
            else:
                now = int(time.mktime(datetime.datetime.utcnow().utctimetuple()) - 300)
            #Create the RRD itself
            theRRD = rrd.RRD(rrdfd, ds=datasources, rra=archives, step=300,start = now)
            theRRD.create()
            self.rrd = theRRD


    def update(self,timestamp,value):
        """Store a reading in the RRD file"""
        LOG.debug("Timestamp is {0} {1}".format(timestamp,type(timestamp)))
        if type(timestamp) == datetime.datetime:
            timestamp = time.mktime(timestamp.utctimetuple())
        LOG.debug("Storing {0} {1} in RRD".format(timestamp,value))
        self.rrd.bufferValue(timestamp,value)
        self.rrd.update()

    def getInfo(self):
        print self.rrd.info()


if __name__ == "__main__":
    if not os.path.exists(RRDPATH):
        print "Attemptoing to create directory"
        print os.makedirs(RRDPATH)

    foo = RRDStore(1000,1000,1000)
    #print foo
