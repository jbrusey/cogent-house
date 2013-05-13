"""
Class to store data from the cogent-house in RRD tables.
"""
import os
import os.path
import time
import datetime

import logging
LOG = logging.getLogger("")

import pyrrd.rrd as rrd
#from pyrrd.rrd import DataSource, RRA, RRD

class RRDStore(object):
    """
    Store data from nodes in an RRD
    """
    def __init__(self,nodeId,typeId,locationId):
        #thisPath = os.path.join(
        rrdfd = "{0}_{1}_{2}.rrd".format(nodeId,locationId,typeId)
        LOG.debug("RRD File {0}".format(rrdfd))

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
            ds = rrd.DataSource(dsName="reading",dsType="GAUGE",heartbeat=600)
            datasources.append(ds)
            
            #And archives
            archives = []
            rra = rrd.RRA(cf="AVERAGE", xff=0.5, steps=1, rows=24) #Every 5 mins
            archives.append(rra)
            rra = rrd.RRA(cf="AVERAGE", xff=0.5, steps=6, rows=24) #Every 1/2 Hour
            archives.append(rra)

            #Ensure URC and offset
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
