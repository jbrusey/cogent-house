"""Script to merge data from two seperate databases.
Like the push script but much more detailed
"""

import logging
import urllib
import json
import zlib
import os
import sys
import urlparse

import sqlalchemy
import requests

import configobj

REQUESTS_LOG = logging.getLogger("requests")
REQUESTS_LOG.setLevel(logging.WARNING)

import cogent.base.model as models
from cogent.push.dictdiff import DictDiff

MAINURL = "mysql://chuser@localhost/salford"
MERGEURL = "mysql://chuser@localhost/salford1"
RESTURL = "http://127.0.0.1:6543/rest"

MAIN = 0
MERGE = 1

class DBMerge(object):
    """Object to handle the merge"""
    def __init__(self, mainurl=MAINURL, mergeurl=MERGEURL):
        #We want a local and remote version of the database
        self.log = logging.getLogger(__name__)
        log = self.log
        #Connect to the engines
        #First the main engine
        log.info("Connecting to Main Engine at {0}".format(mainurl))
        mainengine = sqlalchemy.create_engine(mainurl)
        mainsession = sqlalchemy.orm.sessionmaker(bind=mainengine)
        self.mainsession = mainsession

        log.info("Connecting to Merge Engine at {0}".format(mergeurl))
        mergeengine = sqlalchemy.create_engine(mergeurl)
        mergesession = sqlalchemy.orm.sessionmaker(bind=mergeengine)
        self.mergesession = mergesession

        self.locationmap = {} #Mapping dictionary for locations

    def getcounts(self, nodeid,
                  thesession=MERGE,
                  startdate=None,
                  enddate=None,
                  typeid = None):
        """Get daily counts of the number of samples for a given
        node.

        This function summarises the number of samples each day for a given node
        and returns the values as a list of {<date> : <count>} pairs.


        :param nodeId: Node Id to get counts for
        :param thesession: Which session (MEREGE / MAIN) to get data for
        :param startdate: Optional startdate
        :param enddate: Optional enddate
        :param typeid: Limit to a specific sensor type
        :return: List of (<date>, <count>) pairs
        """

        log = self.log
        if thesession == MAIN:
            session = self.mainsession()
        elif thesession == MERGE:
            session = self.mergesession()
        else:
            log.warning("No Such Session")
            return False

        #Work out the query
        qry = session.query(models.Reading,
                            sqlalchemy.func.date(models.Reading.time),
                            sqlalchemy.func.count(models.Reading),
                            ).filter_by(nodeId = nodeid)
        #qry = qry.filter_by(typeId = 0) #All nodes have temperature
        if startdate:
            qry = qry.filter(models.Reading.time >= startdate)
        if enddate:
            qry = qry.filter(models.Reading.time <= enddate)
        if typeid:
            qry = qry.filter_by(typeid = typeid)

        qry = qry.filter(models.Reading.locationId != None)
        qry = qry.group_by(sqlalchemy.func.date(models.Reading.time))
        qry = qry.order_by(sqlalchemy.func.date(models.Reading.time))

        outdata = [[x[1].isoformat(), x[2]] for x in qry]
        return outdata


    def runnode(self, nodeid):
        """Run an instance for a given node

        This will run the checks for a given node
        """

        log = self.log

        log.info("Running checks for Node: {0}".format(nodeid))

        mainsession = self.mainsession()
        mergesession = self.mergesession()

        #First we fetch counts of all data for these items
        log.debug("--> Fetching remote counts")
        mergecounts = self.getcounts(nodeid)

        log.debug("--> Fetching Main counts")
        maincounts = self.getcounts(nodeid,
                                     MAIN)

        #Next convert to a dictionary and run a dictdiff
        maindict = dict(maincounts)
        mergedict = dict(mergecounts)

        ddiff = DictDiff(maindict, mergedict)

        #Items that are in the Main but not in the Merged
        added = ddiff.added()
        #Items that are completely missing from the Merged
        removed = ddiff.removed()
        #Items where there is a different count than in the merged
        changed = ddiff.changed()

        log.debug("--> Added Items {0}".format(added))
        log.debug("--> Removed Items {0}".format(removed))
        log.debug("--> Changed Items {0}".format(changed))

        #The first nice and simple changes are to add the "removed" data as this
        #does not exist in the remote database

        if removed:
            log.info("--- {0} Complete days that need adding ---"
                     .format(len(removed)))
            for thedate in removed:
                maincount = maindict.get(thedate, 0)
                mergecount = mergedict.get(thedate)
                log.debug("--> {0} {1}/{2} Samples in main".format(thedate,
                                                                   maincount,
                                                                   mergecount))


                #Get the readings themselves
                qry = (mergesession.query(models.Reading)
                       .filter_by(nodeId = nodeid))
                qry = qry.filter(sqlalchemy.func.date(models.Reading.time) ==
                                 thedate)

                for reading in qry:
                    #Check if we have mapped the location
                    if reading.locationId == None:
                        log.warning("Reading {0} has no location !!!!!"
                                    .format(reading))
                        continue

                    maploc = self.locationmap.get(reading.locationId, None)
                    if maploc is None:
                        log.debug("Location {0} Has not been mapped"
                                  .format(reading.locationId))
                        maploc = self._maplocation(reading)

                    #log.debug("New Location is {0}.".format(maploc))
                    #make a copy and add to the new session
                    mainsession.add(models.Reading(time = reading.time,
                                                   nodeId = reading.nodeId,
                                                   locationId = maploc,
                                                   typeId = reading.typeId,
                                                   value = reading.value))

                #We also want to transfer the relevant nodestates
                log.info("Transfering NodeStates")
                qry = (mergesession.query(models.NodeState)
                       .filter_by(nodeId = nodeid))
                qry = qry.filter(sqlalchemy.func.date(models.NodeState.time) ==
                                 thedate)
                log.debug("{0} Nodestates to transfer".format(qry.count()))
                for nodestate in qry:
                    mainsession.add(models.NodeState(time = nodestate.time,
                                                     nodeId = nodestate.nodeId,
                                                     parent = nodestate.parent,
                                                     localtime = nodestate.localtime,
                                                     seq_num = nodestate.seq_num,
                                                     rssi = nodestate.rssi))
                #Close our sessions
                mainsession.flush()
                mainsession.close()

        if changed:
            log.debug("---- Dealing with changed items ----")
            #For the moment I dont really care about merging and duplicates
            #We can fix the problem up later (nodestate table bugfix)
            log.info("--- {0} days that need merging ---"
                     .format(len(changed)))
            for thedate in changed:
                maincount = maindict.get(thedate, 0)
                mergecount = mergedict.get(thedate)
                log.debug("--> {0} {1}/{2} Samples in main".format(thedate,
                                                                   maincount,
                                                                   mergecount))


                if maincount > mergecount:
                    log.warning("For Some Reason there are more items in the main db")
                    continue

                #Get the readings themselves
                qry = (mergesession.query(models.Reading)
                       .filter_by(nodeId = nodeid)
                       )
                qry = qry.filter(models.Reading.locationId != None)
                qry = qry.filter(sqlalchemy.func.date(models.Reading.time) ==
                                 thedate)


                log.debug("--> Total of {0} readings to merge"
                          .format(qry.count()))

                for reading in qry:
                    #Check if we have mapped the location
                    if reading.locationId == None:
                        log.warning("Reading {0} has no location !!!!!"
                                    .format(reading))
                        continue

                    maploc = self.locationmap.get(reading.locationId, None)
                    if maploc is None:
                        log.debug("Location {0} Has not been mapped"
                                  .format(reading.locationId))
                        maploc = self._maplocation(reading)

                    #log.debug("New Location is {0}.".format(maploc))
                    #make a copy and add to the new session
                    mainsession.merge(models.Reading(time = reading.time,
                                                   nodeId = reading.nodeId,
                                                   locationId = maploc,
                                                   typeId = reading.typeId,
                                                   value = reading.value))

                #We also want to transfer the relevant nodestates
                log.info("Transfering NodeStates")
                qry = (mergesession.query(models.NodeState)
                       .filter_by(nodeId = nodeid))
                qry = qry.filter(sqlalchemy.func.date(models.NodeState.time) ==
                                 thedate)
                log.debug("{0} Nodestates to transfer".format(qry.count()))
                for nodestate in qry:
                    mainsession.merge(models.NodeState(time = nodestate.time,
                                                     nodeId = nodestate.nodeId,
                                                     parent = nodestate.parent,
                                                     localtime = nodestate.localtime,
                                                     seq_num = nodestate.seq_num,
                                                     rssi = nodestate.rssi))
                #Close our sessions
                mainsession.flush()
                mainsession.close()

    def _maplocation(self, reading):
        """Map a location id for a reading.

        This method will map the location of a sample to be merged to the
        equivilent location in the main database.

        Additionally, if no such location exists, then it will be created

        :param reading: A reading object that has a location
        :return: The equivilent location id in the main database
        """

        log = self.log

        log.debug("-- Mapping Location {0} --".format(reading))

        theloc = reading.location
        thehouse = reading.location.house
        theroom = reading.location.room

        log.debug("--> Loc {0}".format(theloc))
        log.debug("--> House {0}".format(thehouse))
        log.debug("--> Room {0}".format(theroom))

        mainsession = self.mainsession()

        qry  = mainsession.query(models.House)
        qry = qry.filter_by(address = thehouse.address)
        if qry.count() > 1:
            log.warning("-->--> More than one house with this address in Main")
        mainhouse = qry.first()
        if mainhouse is None:
            log.warning("-->-->No House {0} on Main Database".format(thehouse))
            #TODO: code to add house here


        qry = mainsession.query(models.Room).filter_by(name=theroom.name)
        mainroom = qry.first()
        if qry.count() > 1:
            log.warning("-->-->More than one room with this room in Main DB")
        if mainroom is None:
            log.warning("-->-->No Room {0} on Main Database".format(theroom))

        log.debug("-->-->Main House {0} Room {1}".format(mainhouse, mainroom))

        #We can now workout the locationId
        qry = mainsession.query(models.Location)
        qry = qry.filter_by(houseId = mainhouse.id,
                            roomId = mainroom.id)
        if qry.count() > 1:
            log.warning("-->--> More than one matching location in Main")
        theloc = qry.first()
        if theloc is None:
            log.warning("-->-->No such location on Main Database")

        self.locationmap[reading.locationId] = theloc.id
        log.debug("Location maps to {0}".format(theloc))
        mainsession.close()
        return theloc.id

    def runall(self):
        """Run merger for all nodes in the database"""
        log = self.log
        mergesession = self.mergesession()
        qry = mergesession.query(models.Node)
        qry = qry.filter(models.Node.locationId != None)
        nodelist = [x.id for x in qry]
        log.debug("List of nodes with location {0}".format(nodelist))

        #And possibly work out nodes without a location
        qry = mergesession.query(models.NodeState)
        qry = qry.filter(sqlalchemy.not_(models.NodeState.nodeId.in_(nodelist)))
        qry = qry.group_by(models.NodeState.nodeId)
        if qry.count() > 0:
            log.info("Nodes that have data but no location")
            log.info(qry.all())

        for item in nodelist:
            log.debug("Processing {0}".format(item))
            merger.runnode(item)

class RestDBMerge(DBMerge):
    """Version of the DB Merge function that uses the local DB
    and exisiting Rest interfaces"""
    def __init__(self, mergeurl=MERGEURL):
        """Modified Init  to only use local version of the database

        TODO:  It may be a good idea to read the mergeurl from the
        synchronise.conf file
        """
        #We want a local and remote version of the database
        self.log = logging.getLogger(__name__)
        log = self.log
        #Connect to the engines

        #Read the configuration file
        if sys.prefix  == "/usr":
            conf_prefix = "" #If its a standard "global" instalation
        else :
            conf_prefix = "{0}/".format(sys.prefix)

        configpath = os.path.join(conf_prefix,
                                  "etc",
                                  "cogent-house",
                                  "push-script")

        configfile = os.path.join(configpath,
                                  "synchronise.conf")
        if os.path.exists(configfile):
            log.debug("Read config file from {0}".format(configfile))
            configparser = configobj.ConfigObj(configfile)
        else:
            log.warning("No Config file specified Falling back on local copy")
            configfile = "synchronise.conf"

            configparser = configobj.ConfigObj(configfile)

        #Get the merge url
        generaloptions = configparser["general"]
        mergeurl = generaloptions["localurl"]

        log.info("Connecting to Merge Engine at {0}".format(mergeurl))
        mergeengine = sqlalchemy.create_engine(mergeurl)
        mergesession = sqlalchemy.orm.sessionmaker(bind=mergeengine)
        self.mergesession = mergesession

        #And the Rest url (Just the first active location)
        locations = configparser["locations"]
        for item in locations:
            #Check if we need to synchronise to this location.
            needsync = locations.as_bool(item)
            log.debug("Location {0} Needs Sync >{1}".format(item, needsync))

            if needsync: #Enqueue
                thisloc = configparser[item]["resturl"]
                break

        log.info("Rest URL is {0}".format(thisloc))
        self.resturl = thisloc


        self.locationmap = {}

    def getremotecounts(self, nodeid):
        """Fetch the counts from the remote database"""
        log = self.log
        theurl = "{0}counts/{1}".format(self.resturl, nodeid)
        log.debug("Fetching remote counts from {0}".format(theurl))

        therequest = requests.get(theurl)
        log.debug("Request is {0}".format(therequest))
        output = therequest.json()
        return output

    def _maplocation(self, reading):
        """Map a location id for a reading.

        This method will map the location of a sample to be merged to the
        equivilent location in the main database.

        Additionally, if no such location exists, then it will be created

        :param reading: A reading object that has a location
        :return: The equivilent location id in the main database
        """

        log = self.log
        #For a quick debug

        log.debug("-- Mapping Location {0} --".format(reading))

        theloc = reading.location
        thehouse = reading.location.house
        theroom = reading.location.room

        log.debug("--> Loc {0}".format(theloc))
        log.debug("--> House {0}".format(thehouse))
        log.debug("--> Room {0}".format(theroom))

        params = urllib.urlencode({"address" : thehouse.address})
        houseurl = "{0}house/?{1}".format(self.resturl, params)
        restqry = requests.get(houseurl)

        mainhouse = restqry.json()
        log.debug(mainhouse)
        if not mainhouse:
            log.warning("-->--> No House {0} on Main Database".format(thehouse))

        #Work out the Room
        params = urllib.urlencode({"name" : theroom.name})
        roomurl = "{0}room/?{1}".format(self.resturl, params)
        restqry = requests.get(roomurl)
        mainroom = restqry.json()

        # qry = mainsession.query(models.Room).filter_by(name=theroom.name)
        # mainroom = qry.first()
        if mainroom is None:
            log.warning("-->-->No Room {0} on Main Database".format(theroom))

        log.debug("-->-->Main House {0} Room {1}".format(mainhouse, mainroom))


        #We can now workout the locationId
        params = urllib.urlencode({"houseId" : mainhouse[0]["id"],
                                   "roomId" : mainroom[0]["id"]})
        locurl = "{0}location/?{1}".format(self.resturl, params)
        restqry = requests.get(locurl)
        theloc = restqry.json()
        if theloc is None:
            log.warning("-->-->No such location on Main Database")

        self.locationmap[reading.locationId] = int(theloc[0]["id"])
        log.debug("Location maps to {0}".format(theloc))
        return theloc[0]["id"]

    def runnode(self, nodeid):
        """Run an instance for a given node

        This will run the checks for a given node
        """

        log = self.log

        log.info("Running checks for Node: {0}".format(nodeid))

        mergesession = self.mergesession()

        #First we fetch counts of all data for these items
        log.debug("--> Fetching remote counts")
        mergecounts = self.getcounts(nodeid)

        log.debug("--> Fetching Main counts")
        maincounts = self.getremotecounts(nodeid)

        #Next convert to a dictionary and run a dictdiff
        maindict = dict(maincounts)
        mergedict = dict(mergecounts)

        ddiff = DictDiff(maindict, mergedict)

        #Items that are in the Main but not in the Merged
        added = ddiff.added()
        #Items that are completely missing from the Merged
        removed = ddiff.removed()
        #Items where there is a different count than in the merged
        changed = ddiff.changed()

        log.debug("--> Added Items {0}".format(added))
        log.debug("--> Removed Items {0}".format(removed))
        log.debug("--> Changed Items {0}".format(changed))

        #For this version I dont really care that the removed and changed
        #require a merge etc,  higher level code takes care of it
        #:warning: If the bulk merge functionality changes this may break

        removed = removed.union(changed)

        if removed:
            log.info("--- {0} Complete days that need adding ---"
                     .format(len(removed)))
            for thedate in removed:
                maincount = maindict.get(thedate, 0)
                mergecount = mergedict.get(thedate)
                log.debug("--> {0} {1}/{2} Samples in main".format(thedate,
                                                                   maincount,
                                                                   mergecount))

                if maincount > mergecount:
                    log.warning("For Some Reason there are more items in the main db. Assuming all is well")
                    continue
                #Get the readings themselves
                qry = (mergesession.query(models.Reading)
                       .filter_by(nodeId = nodeid))
                qry = qry.filter(sqlalchemy.func.date(models.Reading.time) ==
                                 thedate)

                datalist = []
                for reading in qry:
                    #Check if we have mapped the location
                    if reading.locationId == None:
                        log.warning("Reading {0} has no location !!!!!"
                                    .format(reading))
                        continue

                    maploc = self.locationmap.get(reading.locationId, None)
                    if maploc is None:
                        log.debug("Location {0} Has not been mapped"
                                  .format(reading.locationId))
                        maploc = self._maplocation(reading)

                    #log.debug("New Location is {0}.".format(maploc))
                    dictitem = reading.dict()
                    dictitem["locationId"] = maploc
                    datalist.append(dictitem)

                #log.debug("Data List {0}".format(datalist))
                #log.debug(datalist[:5])
                jsonStr = json.dumps(datalist)
                gzStr = zlib.compress(jsonStr)

                #And then try to bulk upload them
                theurl = "{0}bulk/".format(self.resturl)
                restqry = requests.post(theurl, data = gzStr)
                #log.debug(restqry)

                #We also want to transfer the relevant nodestates
                log.info("Transfering NodeStates")
                qry = (mergesession.query(models.NodeState)
                       .filter_by(nodeId = nodeid))
                qry = qry.filter(sqlalchemy.func.date(models.NodeState.time) ==
                                 thedate)
                #log.debug("{0} Nodestates to transfer".format(qry.count()))
                datalist = []
                for nodestate in qry:
                    dictitem = nodestate.dict()
                    dictitem["id"] = None
                    datalist.append(dictitem)

                jsonStr = json.dumps(datalist)
                gzStr = zlib.compress(jsonStr)

                #And then try to bulk upload them
                theurl = "{0}bulk/".format(self.resturl)
                restqry = requests.post(theurl, data = gzStr)
                log.debug(restqry)

        return

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    #merger = DBMerge()


    merger = RestDBMerge()
    merger.runall()
    #print merger.getcounts(33)
    #print merger.getremotecounts(33)

    #md = models.Reading(nodeId = 33,
    #                    locationId = 3)
    #merger._maplocation(md)
    #merger.runnode(33)
    #merger.getcounts(33)
    #merger.testmain()
    #print "="*40
    #merger.testremote()
