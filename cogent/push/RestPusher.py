
"""
Modified version of the push script that will fetch all items,
convert to JSON and (eventually) transfer across REST

This replaces the ssh tunnel database access curretly used to transfer samples.

However, for the moment syncronising the Locations etc (or the complex bit) is
still done via SQLA. As this takes a fraction of the transfer time its probably
a good idea to leave it.



    .. warning::

        This will fail if the database type is SQ-Lite, currently a connection
        cannot issue a statement while another is open.  Therefore the loop
        through the readings, appending new items fails with a DATABASE LOCKED
        error.

        I am at a loss of what to do to fix this.  However, as we will be
        pushing to mySQL, its not really a problem except for some test cases

    .. note::

        I currently add 1 second to the time the last sample was transmitted,
        this means that there is no chance that the query to get readings will
        return an item that has all ready been synced, leading to an integrity
        error.

        I have tried lower values (0.5 seconds) but this pulls the last synced
        item out, this is possibly a error induced by mySQL's datetime not
        holding microseconds.

    .. warning::

       In My experience you may need to bugger about with connection strings
       Checking either Localhost or 127.0.0.1 Localhost worked on my machine, my
       connecting to Cogentee wanted 127.0.0.1

    .. since 0.1::

       Moved ssh port forwarding to paramiko (see sshclient class) This should
       stop the errors when there is a connection problem.

    .. since 0.2::

       * Better error handling
       * Pagination for sync results, transfer at most PUSH_LIMIT items at a
         time.

    .. since 0.3::

       Moved Nodestate Sync into the main readings sync class, this should stop
       duplicate nodestates turning up if there is a failiure

    .. since 0.4::

       Overhall of the system to make use of REST to upload samples rather than
       transfer data across directly.

    .. since 0.5::

       Make use of an .ini style config file to set everything up

       Split functionalility into a Daemon, and Upload classes.  This should
       make maintainance of any local mappings a little easier to deal with.
"""

import logging
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)

__version__ = "0.5.0"

import sqlalchemy
import remoteModels

import cogent
import cogent.base.model as models
import cogent.base.model.meta as meta
from datetime import datetime
from datetime import timedelta

import subprocess

import paramiko
import sshClient
import threading
import socket

import time

import ConfigParser
#To Parse Configuration files
#import cfgparse
import configobj
import os

import dateutil.parser

import restful_lib
import json
import urllib

log = logging.getLogger(__name__)
#log.setLevel(logging.DEBUG)
log.setLevel(logging.INFO)

#Reset Paramiko logging to reduce output cruft.
plogger = paramiko.util.logging.getLogger()
plogger.setLevel(logging.WARNING)

#URL of local database to connect to
LOCAL_URL = 'mysql://test_user:test_user@localhost/pushSource'
PUSH_LIMIT = 5000 #Limit on samples to transfer at any one time
SYNC_TIME = 60*10  #How often we want to call the sync (Every 10 Mins)

#RSA KEY
RSA_KEY = None
#RSA_KEY = "/home/dang/.ssh/id_rsa.pub"
RSA_KEY = "/home/dang/.ssh/work_key.pub"

#Knwon Hosts file
KNOWN_HOSTS = None
KNOWN_HOSTS = "/home/dang/.ssh/known_hosts"

REST_URL = "127.0.0.1:6543/rest/"

class PushServer(object):
    """
    Class to deal with pushing updates to a group of remote databases

    This class is designed to be run as a daemon, managing a group of individual
    pusher objects, and facilitating the transfer of data between remote and
    local DB's
    """

    def __init__(self, localURL=None):
        """Initialise the push server object

        This should:

        #. Create a connection to the local database,
        #. Read the Configuration files.
        #.Setup Necessary Pusher objects for each database that needs
          synchronising.

        :var localURL:  The DBString used to connect to the local database.
                        This can be used to overwrite the url in the config file
        """

        log.info("Initialising Push Server")

        self.configParser = configobj.ConfigObj("synchronise.conf")

        #Read the Configuration File
        generalConf, locationConfig = self.readConfig()

        #Store the config
        self.generalConf = generalConf

        if not localURL:
            localURL = generalConf["localUrl"]

        log.info("Connecting to local database at {0}".format(localURL))

        #Initalise the local database connection
        log.debug("Initalise Session for {0}".format(localURL))
        engine = sqlalchemy.create_engine(localURL)
        models.initialise_sql(engine)
        localSession = sqlalchemy.orm.sessionmaker(bind=engine)
        self.localSession = localSession



        #Create a new Pusher object for this each item given in the config
        syncList = []
        for item in locationConfig.values():
            syncList.append(Pusher(localSession,
                                   item,
                                   generalConf,
                                   self.configParser))

        self.syncList = syncList
        #self.theConfig = theConfig

    def readConfig(self):
        """Read configuration from the config file.

        This will parse the synchronise.conf file, and produce a local
        dictionary of all objects that need synchronising.

        :return: A dictionary of parameters (as a list) where syncronisation is
        required
        """

        confParser = self.configParser
        log.debug("Processing Config File")

        #Dictionary to return
        syncDict = {}

        generalOpts = confParser["general"]


        #Get the Locations
        locations = confParser["locations"]

        for loc in locations:
            isBool = locations.as_bool(loc)
            log.debug("--> Processing Location {0} {1}".format(loc, isBool))
            if isBool:
                items = confParser[loc]
                if items.get("lastupdate", None) in [None, "None"]:
                    items["lastupdate"] = None
                else:
                    #We need to parse the last time
                    theTime = dateutil.parser.parse(items["lastupdate"])
                    items["lastupdate"] = theTime
                syncDict[loc] = items

        self.confParser = confParser
        return generalOpts, syncDict


    def sync(self):
        """
        Run one instance of the synchroniseation mechnism,

        For each item in the config file, perform synchronisation.

        :return: True on success,  False otherwise
        """

        log.info("Running Full Syncronise Cycle")
        for item in self.syncList:
            log.debug("Synchronising {0}".format(item))
            tempcount = 0
            samples = 1
            while samples > 0 and tempcount < 5:
                t1 = time.time()
                samples,lastTime = item.sync()
                t2 = time.time()
                log.info("Sync cycle complete to in {0:.2f}s {1} samples remain from {2}".format(t2-t1,
                                                                                                 samples,
                                                                                                 lastTime))
                tempcount+=1
                self.confParser.write()

class Pusher(object):
    """Class to push updates to a remote database.

    This class contains the code to deal with the nuts and bolts of syncronising
    remote and local databases

    """

    def __init__(self, localSession, config,generalConf,configObj):
        """Initalise a pusher object

        :param localSession: A SQLA session, connected to the local database
        :param config: Config File options for this particular pusher object
        :param generalConf: Global Configuration file for all Push Objest
        :param configObj: Config Parser Object (To allow Writes)
        """

        self.localSession = localSession
        self.config = config
        self.generalConf = generalConf
        self.configObj = configObj

        # Storage for mappings between local -> Remote
        self.mappedDeployments = {} #DONE
        self.mappedHouses = {} #DONE
        self.mappedRooms = {}
        self.mappedLocations = {}
        self.mappedRoomTypes = {}

        self.restSession = restful_lib.Connection("http://127.0.0.1:6543/rest/")

    def sync(self):
        """
        Perform one synchronisation step for this Pusher object

        :return: True if the sync is successfull, False otherwise
        """

        config = self.config
        log.debug("Sync with config {0}".format(config))
        self.lastUpdate = config.get("lastupdate", None)
        log.debug("Last Update Was {0}".format(self.lastUpdate))

        #Start to map the rest
        #log.setLevel(logging.INFO)
        deployments = self.mapDeployments()

        # #Houses
        houses = self.mapHouses(deploymentIds = deployments)

        # #And Locations
        self.mapLocations(houseIds = houses)
        #log.setLevel(logging.DEBUG)

        #Pring some Debugging Information
        #self.debugMappings()

        #log.debug("Last update {0}".format(self.lastUpdate))
        #Synchronise Readings
        samples,lastTime = self.syncReadings()

        log.debug("Remaining Samples {0}".format(samples))
        log.debug("Last Sample Time {0}".format(lastTime))

        
        #Finally update the config file. (Add an tiny Offset to avoid issues
        #with milisecond rounding)
        self.config['lastupdate'] = lastTime + timedelta(seconds=1)

        return samples,lastTime


    def mapDeployments(self, localIds = None):
        """
        Map deployments in the local database to those in the remote database

        If localIds are given, this will map the supplied Ids.
        Otherwise, deployments with an endDate later than the last update,
        or no endDate will be mapped.

        .. warning::

            We assume that deployments all have a unique name.

        :var localIds:  List of Id's for local database objects
        :return: A List of delployment ID's that have been updated
        """
        log.debug("----- Mapping Deployments ------")
        mappedDeployments = self.mappedDeployments
        lSess = self.localSession()
        restSession = self.restSession

        #Get the list of deployments that may need updating
        Deployment = models.Deployment
        depQuery = lSess.query(models.Deployment)
        lastUpdate = self.lastUpdate

        #Firstly if we are given a list of localIds:
        if localIds:
            depQuery = depQuery.filter(Deployment.id.in_(localIds))
        elif lastUpdate:
            #Filter based on the last Update
            log.debug("Filter Based on {0}".format(lastUpdate))
            depQuery = depQuery.filter(sqlalchemy.or_(Deployment.endDate >= lastUpdate,
                                                      Deployment.endDate == None))


        for mapDep in depQuery:
            log.debug("--> Syncronising Deployment {0}".format(mapDep))

            theDeployment = mappedDeployments.get(mapDep.id, None)
            if theDeployment is None:
                log.debug("--> -->  Deployment Not Mapped")


                #And Build the Query
                params = {"name":mapDep.name}
                theUrl = "deployment/?{0}".format(urllib.urlencode(params))

                #If we are updating an item, sending the orignial dict overwrites
                #The ID, therefore we remove it from the request body
                theBody = mapDep.toDict()
                del theBody["id"]

                #Then we can ask the system to update / create this object
                restQry = restSession.request_put(theUrl,
                                                  body=json.dumps(theBody))
                log.debug(restQry)

                if restQry["headers"]["status"] == '404':
                    log.warning("Error Creating Deployment Item")
                    raise Exception ("Error Creating Deplyment Item")


                #Then map the local and Remote Id's
                restBody = json.loads(restQry['body'])
                log.info("Deployment {0} mapped to {1}".format(mapDep.id,
                                                               restBody['id']))
                mappedDeployments[mapDep.id] = restBody['id']

        return [x.id for x in depQuery]


    def mapHouses(self, localIds=None, deploymentIds=None):
        """
        Map between houses in local and remote database

        If localIds are provided then this will map just those Id's

        If deploymentIds are specified then only houses linked to these
        deploymeents will be mapped Otherwise all houses will be mapped

        We assume that houses are unique based on Address and deployment Id

        :param localIds: Id of house objects to synchronise
        :param deploymentIds: Sync houses attached to these deployments
        :return: List of (local) houseId's that have been sync
        """
        log.debug("Mapping Houses")

        mappedHouses = self.mappedHouses
        mappedDeployments = self.mappedDeployments

        lSess = self.localSession()
        restSession = self.restSession
        #rSess = self.remoteSession()

        log.debug("Local Id Specified {0}".format(localIds))
        log.debug("Deploymet Id's: {0}".format(deploymentIds))

        House = models.House

        #Find the Houses we need to update
        houseQuery = lSess.query(House)

        if localIds:
            houseQuery = houseQuery.filter(House.id.in_(localIds))
        elif deploymentIds:
            houseQuery = houseQuery.filter(House.deploymentId.in_(deploymentIds))


        log.debug("Sycnhronising Houses")
        for mapHouse in houseQuery:
            log.debug("--> Mapping House {0}".format(mapHouse))

            theHouse = mappedHouses.get(mapHouse.id, None)
            if theHouse is None:
                #Get the mapped deployment Id
                log.debug("--> --> House Not Mapped")

                #Start to build our Query
                depId = mappedDeployments[mapHouse.deploymentId]
                log.debug("--> Mapped Deployment It {0}".format(depId))
                params = {"address":mapHouse.address,
                          "deploymentId":depId}

                theUrl = "house/?{0}".format(urllib.urlencode(params))

                theBody = mapHouse.toDict()
                del theBody["id"] #Remove Id
                theBody["deploymentId"] = depId #Ensure we use the correct deployment Ids

                restQry = restSession.request_put(theUrl, body=json.dumps(theBody))
                log.debug(restQry)

                if restQry["headers"]["status"] == '404':
                    log.warning("Error Creating Deployment Item")
                    raise Exception ("Error Creating Deplyment Item")


                #Then map the local and Remote Id's
                restBody = json.loads(restQry['body'])
                log.info("House {0} mapped to {1}".format(mapHouse.id,
                                                          restBody['id']))
                mappedHouses[mapHouse.id] = restBody['id']

        #After that we want to get all locations assoicated with a House
        return [x.id for x in houseQuery]

    def mapRooms(self, roomId):
        """
        Map a room between the Local and Remote Database

        :param roomId: local Room Id to Map
        :return: The remote version of this room
        """

        mappedRoomTypes = self.mappedRoomTypes
        mappedRooms = self.mappedRooms

        #rSess = self.remoteSession()
        lSess = self.localSession()
        restSession = self.restSession

        #log.debug("Mapping Room {0}".format(roomId))

        theRoom = lSess.query(models.Room).filter_by(id=roomId).first()
        log.debug("Mapping Room {0}".format(theRoom))
        #WE also need to double check that the room type exists
        mapType = mappedRoomTypes.get(theRoom.roomTypeId, None)
        log.debug("Mapped Room Type {0}".format(mapType))
        if mapType is None:
            roomType = theRoom.roomType
            log.debug("--> RoomType {0} not mapped".format(roomType))

            #Upload new room types
            params = {"name":roomType.name}
            theUrl = "roomType/?{0}".format(urllib.urlencode(params))

            theBody = roomType.toDict()
            del theBody["id"]

            restQry = restSession.request_put(theUrl, body=json.dumps(theBody))
            log.debug(restQry)
            restBody = json.loads(restQry['body'])
            mapType = restBody['id']
            log.info("Room Type {0} mapped to {1}".format(roomType.id,
                                                          mapType))
            mappedRoomTypes[roomType.id] = mapType

        #Then Create the Room
        params = {"name":theRoom.name,
                  'roomTypeId':mapType}
        log.debug("Creating Room with Parameters {0}".format(params))
        theUrl = "room/?{0}".format(urllib.urlencode(params))
        theBody = theRoom.toDict()
        del theBody["id"]
        theBody["roomTypeId"] = mapType

        restQry = restSession.request_put(theUrl, body=json.dumps(theBody))
        log.debug(restQry)

        restBody = json.loads(restQry['body'])
        mapRoom = restBody['id']

        log.info("Room {0} Mapped to {1}".format(theRoom.id,
                                                 mapRoom))

        mappedRooms[theRoom.id] = mapRoom

        return mapRoom

    def mapLocations(self, localIds=None, houseIds=None):
        """
        Map between houses in local and remote database

        If localIds are provided then this will map just those Id's

        If HouseIds are specified then only locations linked to these
        houses will be mapped

        :param localIds: Id of Location objects to synchronise
        :param houseIds:  Houses attached to these deployments
        :return: List of (local) locationId's that have been sync
        """
        log.debug("Mapping Locations")

        #mappedHouses = self.mappedHouses
        #mappedDeployments = self.mappedDeployments

        lSess = self.localSession()
        restSession = self.restSession

        mappedLocations = self.mappedLocations
        mappedRooms = self.mappedRooms
        mappedHouses = self.mappedHouses

        log.debug("=====> ROOMS {0}".format(mappedRooms))
        log.debug("=====> HOUSES {0}".format(mappedHouses))

        Location = models.Location

        locQuery = lSess.query(Location)

        if localIds:
            locQuery = locQuery.filter(Location.id.in_(localIds))
        elif houseIds:
            locQuery = locQuery.filter(Location.houseId.in_(houseIds))

        for mapLoc in locQuery:
            log.debug("Mapping Location {0}".format(mapLoc))

            # #Check we dont allready know about this
            theLocation = mappedLocations.get(mapLoc.id, None)

            if theLocation is None:
                log.debug("--> Location not Known")

                #The first thing we want to do is to see if we have a mapped
                # Rooms / Houses for this location, Houses should have been
                # taken care of above

                mapHouse = mappedHouses[mapLoc.houseId]
                mapRoom = mappedRooms.get(mapLoc.roomId, None)
                log.debug("--> Mapped House {0}".format(mapHouse))
                log.debug("--> Mapped Room {0}".format(mapRoom))

                if mapRoom is None:
                    mapRoom = self.mapRooms(mapLoc.room.id)

                log.debug("--> MAPPED ROOM {0}".format(mapRoom))

                #We can then get on with creating the Location

                params = {"houseId":mapHouse,
                          'roomId':mapRoom}

                log.debug("Creating Location with Parameters {0}".format(params))
                theUrl = "location/?{0}".format(urllib.urlencode(params))

                theBody = mapLoc.toDict()

                del theBody["id"]
                theBody["houseId"] = mapHouse
                theBody["roomId"] = mapRoom

                restQry = restSession.request_put(theUrl, body=json.dumps(theBody))
                log.debug(restQry)

                restBody = json.loads(restQry['body'])
                restLoc = restBody['id']
                mappedLocations[mapLoc.id] = restLoc


    def debugMappings(self):
        """
        Helper Debug function to print mappings
        """

        log.debug("---- Mapped Deloyments ---")
        log.debug(self.mappedDeployments)
        for key, item in self.mappedDeployments.iteritems():
            log.debug("{0} : {1}".format(key, item))

        log.debug("---- Mapped Houses ----")
        log.debug(self.mappedHouses)
        for key, item in self.mappedHouses.iteritems():
            log.debug("{0} -> {1}".format(key, item))

        log.debug("--- MAPPED ROOM TYPES----")
        log.debug(self.mappedRoomTypes)
        for key, item in self.mappedRoomTypes.iteritems():
            log.debug("{0} {1}".format(key, item))

        log.debug("--- Mapped Rooms ---")
        log.debug(self.mappedRooms)
        for key, item in self.mappedRooms.iteritems():
           log.debug("{0} -> {1}".format(key, item))

        log.debug("--- Mapped Locations --")
        log.debug(self.mappedLocations)
        for key, item in self.mappedLocations.iteritems():
           log.debug("{0} {1}".format(key, item))
        log.debug("------------")

        return


    def syncNodes(self):
        """Syncronise nodes:

        Check if we need to syncronise Nodes If there are any nodes missing,
        make sure they are created along with the relevant sensors.

        Currently this is a one way syncronisation. with only those nodes not
        existing on the remote server uploaded. Given that node ID's are unique,
        this should not be a problem.


        .. warning::

            This method currently relies on the fact that all nodes will have a
            unique ID,  if this ceases to be the case (for example if we replace
            a node with a new node of the same ID, then it may be possible that
            Calibration data etc, starts to fall apart.
            Hopefully, this situation never arises.

            Additionally, it relies on the fact that sensor types will also be
            static between the local and remote databases, as these are created
            using a global configuration file, this should also not be a problem

            We also need to consider what happens if a new sensor is added to a
            node. Currently our code doesn't support this, if a node exists then
            we assume then there has been no change to the node itself.

        """
        lSess = self.localSession()
        #rSess = self.remoteSession()
        restSession = self.restSession

        log.info("Synchronising Nodes")

        #Get the Rest Objects
        restQuery = restSession.request_get("Node/")

        #Then filter out just ID's
        restBody = json.loads(restQuery["body"])
        rQuery = [x['id'] for x in restBody]
        #log.debug(restBody)
        log.debug("Remote Nodes :{0}".format(rQuery))

        #Map these against our Local Nodes
        #Have a check here, if the remote DB is empty, then using _in throws a
        #Error
        if rQuery:
            lQuery = lSess.query(models.Node)
            lQuery = lQuery.filter(~models.Node.id.in_(rQuery))
        else:
            lQuery = lSess.query(models.Node)

        lQuery = lQuery.all()

        if lQuery is None:
            log.debug("--> No Nodes to Synchronise")
            return False
        else:
            log.debug("--> {0} Nodes to Synchronise".format(len(lQuery)))
            log.debug(lQuery)

        bulkUpload = []
        for node in lQuery:
            log.debug("--> --> Node {0} does not exist on remote server".format(node))

            #Create the Node
            newNode = models.Node(id=node.id)

            bulkUpload.append(newNode)

            #And Any attached Sensors
            for sensor in node.sensors:
                #We shouldn't have to worry about sensor types as they should be
                #global
                newSensor = models.Sensor(sensorTypeId=sensor.sensorTypeId,
                                          nodeId = node.id,
                                          calibrationSlope = sensor.calibrationSlope,
                                          calibrationOffset = sensor.calibrationOffset)

                log.debug("Creating Sensor {0}".format(newSensor))
                bulkUpload.append(newSensor)

        jsonBody = json.dumps([x.toDict() for x in bulkUpload])
        restQuery = restSession.request_post("Bulk/",
                                             body=jsonBody)

        return restQuery['headers']['status'] == 201


    def syncReadings(self,cutTime=None):
        """Synchronise readings between two databases

        :param DateTime cutTime: Time to start the Sync from
        :return: (Number of Readings that remain to be synchronised,
                  Timestamp of last reading)

        This assumes that Sync Nodes has been called.

        The Algorithm for this is:

        Initialise Temporary Storage, (Location = {})

        #. Get the time of the most recent update from the local database
        #. Get all Local Readings after this time.
        #. For Each Reading

            #. If !Location in TempStore:
                #. Add Location()
            #. Else:
                #. Add Sample

        # If Sync is successful, fix the last update timestamp and return
        """


        lSess = self.localSession()
        restSession = self.restSession

        mappedLocations = self.mappedLocations

        #Time stamp to check readings against
        if not cutTime:
            cutTime = self.lastUpdate

        log.info("Synchronising Readings from {0}".format(cutTime))

        fetchLast = time.time()
        #Update Node States

        #Get the Readings
        readings = lSess.query(models.Reading).order_by(models.Reading.time)
        if cutTime:
            log.debug("Filter all readings since {0}".format(cutTime))
            readings = readings.filter(models.Reading.time >= cutTime)

        remainingReadings = readings.count()

        if remainingReadings == 0:
            log.info("No More Readings to Sync")
            return (remainingReadings,cutTime)
        #Limit by the number of items specified in the Config file
        readings = readings.limit(self.generalConf['pushlimit'])
        #print readings.all()
        #return

        #allReadings = json.dumps([x.toDict() for x in allReadings])
        #log.debug(allReadings)
        #import sys
        #log.debug(sys.getsizeof(allReadings))

        jsonList = []
        for reading in readings:
            #Convert to a JSON and remap the location
            dictReading = reading.toDict()
            dictReading['locationId'] = mappedLocations[reading.locationId]
            #log.debug("{0} -> {1}".format(reading,dictReading))
            jsonList.append(dictReading)


        #log.debug(jsonList)
        #And then try to bulk upload them
        restQry = restSession.request_post("/bulk/",body=json.dumps(jsonList))
        #log.debug(restQry)
        if restQry["headers"]["status"] == '404':
            log.warning("Upload Fails")
            raise Exception ("Bad Things Happen")

        #We also want to update the Node States
        lastSample = readings[-1].time
        log.debug("Last Sample Time {0}".format(lastSample))

        nodeStates = lSess.query(models.NodeState)
        if cutTime:
            nodeStates = nodeStates.filter(models.NodeState.time >= cutTime)
        nodeStates = nodeStates.filter(models.NodeState.time <= lastSample)

        restStates = [x.toDict() for x in nodeStates]
        log.debug("Rest States {0}".format(restStates))
        if restStates:
            restQry = restSession.request_post("/bulk/",
                                               body=json.dumps(restStates))
            log.debug(restQry)

        log.debug("Node States")

        return remainingReadings,lastSample

    def syncState(self,cutTime=None,endTime=None):
        """
        Synchronise any node state information

        Currently this just syncronises the node state table based on a given start date.
        Actually this is pretty easy, as our constaints on unique node names mean that 
        We dont have to do any error checking.

        :param DateTime startTime: Time to start filtering the states from
        """
        lSess = self.LocalSession()
        session = self.RemoteSession()

        nodeStates = lSess.query(models.NodeState).order_by(models.NodeState.time)
        log.debug("Total Nodestates {0}".format(nodeStates.count()))
        if cutTime:
            nodeStates = nodeStates.filter(models.NodeState.time >= cutTime)
        if endTime:
            nodeStates = nodeStates.filter(models.NodeState.time <= endTime)

        log.debug("Total NodeStates to Sync {0}".format(nodeStates.count()))
        stateCount = 0
        for item in nodeStates:
            newState = remoteModels.NodeState(time=item.time,
                                              nodeId = item.nodeId,
                                              parent = item.parent,
                                              localtime = item.localtime)
            session.add(newState)
            #log.info("--> Adding State {0}".format(newState))
        session.flush()
        session.commit()
        session.close()

        lSess.close()

if __name__ == "__main__":
    logging.debug("Testing Push Classes")
    
    #import time

    server = PushServer()
    server.sync()
    #log.debug("{0}".format("="*50))
    #log.debug("{0}".format("="*50))
    #server.sync()
    #push = Pusher()
    #push.sync()
    #for x in range(10):
    #    push.sync()
                       
    #while True: #Loop for everything
    #    t1= time.time()
    #    log.info("----- Synch at {0}".format(datetime.now()))
        #push.sync()
        #log.info("---- Total Time Taken for Sync {0}".format(time.time() - t1))
        #time.sleep(SYNC_TIME)
    #push.sync()
