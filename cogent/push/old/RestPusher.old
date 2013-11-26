
"""
Modified version of the push script that will fetch all items,
convert to JSON and (eventually) transfer across REST

This replaces the ssh tunnel database access curretly used to transfer samples.

However, for the moment syncronising the Locations etc (or the complex bit) is
still done via SQLA. As this takes a fraction of the transfer time its probably
a good idea to leave it.

    .. note::

        I currently add 1 second to the time the last sample was transmitted,
        this means that there is no chance that the query to get readings will
        return an item that has all ready been synced, leading to an integrity
        error.

        I have tried lower values (0.5 seconds) but this pulls the last synced
        item out, this is possibly a error induced by mySQL's datetime not
        holding microseconds.

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

    .. since 0.4.1::

       Make use of an .ini style config file to set everything up

       Split functionalility into a Daemon, and Upload classes.  This should
       make maintainance of any local mappings a little easier to deal with.


    .. since 0.4.2::

       Store any mappings as a pickled object.

   .. since 0.5.0::
       
       New Functionality to manually sync a database from scratch
       Some Changes to logging functionality

"""

import logging
logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO,filename="pushCogentee.log")
#logging.basicConfig(level=logging.WARNING)

__version__ = "0.5.0"

import sqlalchemy
#import remoteModels

import cogent
import cogent.base.model as models
import cogent.base.model.meta as meta
#from datetime import datetime
from datetime import timedelta

import time

import os.path

#import ConfigParser
#To Parse Configuration files

import configobj


import dateutil.parser

import restful_lib
import json
import urllib
        
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

        self.log = logging.getLogger("__name__")
        log = self.log
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
        engine = sqlalchemy.create_engine(localURL)
        models.initialise_sql(engine)
        localSession = sqlalchemy.orm.sessionmaker(bind=engine)
        self.localSession = localSession

        session = localSession()
        theQry = session.query(models.House).count()
        log.debug("Total of {0} houses in database".format(theQry))

        #Create a new Pusher object for this each item given in the config
        syncList = []
        for item in locationConfig.values():
            log.debug("")
            log.info("--> Initalising pusher for {0} {1} {2}".format(localSession,generalConf,item))
            thePusher = Pusher(localSession,
                               item["resturl"],
                               item["lastupdate"],
                               generalConf["pushlimit"],
                               item
                               )
            
            thePusher.checkConnection()
            #thePusher.validateData()

            syncList.append(thePusher)

        self.syncList = syncList
        #self.theConfig = theConfig

    def readConfig(self):
        """Read configuration from the config file.

        This will parse the synchronise.conf file, and produce a local
        dictionary of all objects that need synchronising.

        :return: A dictionary of parameters (as a list) where syncronisation is
        required
        """
        log = self.log
        confParser = self.configParser
        log.debug("Processing Config File")

        #Dictionary to return
        syncDict = {}

        generalOpts = confParser["general"]


        #Get the Locations
        locations = confParser["locations"]

        for loc in locations:
            isBool = locations.as_bool(loc)
            #log.debug("--> Processing Location {0} {1}".format(loc, isBool))
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

        log = self.log
        loopStart = time.time()
        avgTime = None
        log.info("Running Full Syncronise Cycle")

        for item in self.syncList:
            log.debug("Synchronising {0}".format(item))
            samples = 1

            #samples,lastTime = item.sync()
            
            # #return
            # while samples > 0:
            #     t1 = time.time()
            #     samples, lastTime = item.sync()
            #     t2 = time.time()
            #     log.info("Sync cycle complete to in {0:.2f}s {1} samples remain from {2}".format(t2-t1,
            #                                                                                      samples,
            #                                                                                      lastTime))

            #     if avgTime is None:
            #         avgTime = t2-t1
            #     else:
            #         avgTime = (avgTime + (t2-t1)) / 2.0
                
            #     self.confParser.write()

        loopEnd = time.time()
        log.info("Total Time Taken {0} Avg {1}".format(loopEnd-loopStart,avgTime))

class Pusher(object):
    """Class to push updates to a remote database.

    This class contains the code to deal with the nuts and bolts of syncronising
    remote and local databases

    """

    def __init__(self, localSession, restUrl,lastUpdate=None, pushLimit=5000,configFile = None):
        """Initalise a pusher object

        :param localSession: A SQLA session, connected to the local database
        :param restUrl: URL of rest interface to upload to
        #:param config: Config File options for this particular pusher object
        :param lastUpdate: Time of last Update
        #:param generalConf: Global Configuration file for all Push Objest
        #:param configObj: Config Parser Object (To allow Writes)
        :param configFile: Link to the Configuration file for this database
        """

        self.log = logging.getLogger(__name__)
        #self.log.setLevel(logging.INFO)
        self.log.setLevel(logging.WARNING)
        log = self.log
        

        log.debug("Initialising Push Object")
        #Save the Parameters
        self.localSession = localSession
        self.lastUpdate = lastUpdate
        self.configFile = configFile
        #self.generalConf = generalConf
        self.pushLimit = pushLimit

        # Storage for mappings between local -> Remote
        self.mappedDeployments = {} #DONE
        self.mappedHouses = {} #DONE
        self.mappedRooms = {}
        self.mappedLocations = {}
        self.mappedRoomTypes = {}

        #restUrl = config["resturl"]
        log.debug("Starting REST connection for {0}".format(restUrl))
        self.restUrl = restUrl
        #self.restSession = restful_lib.Connection("http://127.0.0.1:6543/rest/")
        self.restSession = restful_lib.Connection(restUrl)


    def checkConnection(self):
        #Do we have a connection to the server
        log = self.log

        restSession = self.restSession
        restQry = restSession.request_get("/deployment/0")
        if restQry["headers"]["status"] == "503":
            log.warning("No Connection to server available")
            return False
        log.debug("Connection to rest server OK")
        return True

    def validateData(self):
        """
        Do Some Basic Validation of the Data

        For example, Looking for Samples without Nodes
        """

        log = self.log
        log.info("Performing Basic Database Validation")

        badTypes = []
        badNodes = []
        
        session = self.localSession()
        restSession = self.restSession

        #Our bigest problem is readings for Nodes etc that do not exist.
        theQry = session.query(models.Deployment)

        if theQry.count() == 0:
            log.warning("WARNING: No Deployments on the Local Database")

        #Look for missing sensor types
            
        #SELECT * FROM Reading LEFT OUTER JOIN SensorType ON Reading.type = SensorType.id WHERE SensorType.id IS null 
        #Grows to SELECT DISTINCT type FROM ....

        #mTypes = session.query(models.Reading)
        mTypes = session.query(sqlalchemy.distinct(models.Reading.typeId))
        mTypes = mTypes.outerjoin(models.SensorType)
        mTypes = mTypes.filter(models.SensorType.id == None)


        if mTypes.count() > 0:
            badTypes = [x[0] for x in mTypes.all()]
            log.warning("WARNING: Readings in local database found without corresponding sensor type")#: {0}".format(badTypes))
            for item in badTypes:
                #Perform some extra validation here
                theQry = session.query(models.Reading).filter_by(typeId = item)
                
                log.warning("--> Missing Sensor Type is {0} A Total of {1} records affected".format(item,theQry.count()))
               

        #And Missing Nodes
        mNodes = session.query(sqlalchemy.distinct(models.Reading.nodeId))
        mNodes = mNodes.outerjoin(models.Node)
        mNodes = mNodes.filter(models.Node.id == None)

        if mNodes.count() > 0:
            badNodes = [x[0] for x in mNodes.all()]
            log.warning("WARNING: Readings in local databsae without corresponding node: {0}".format(badNodes))

            for item in badNodes:
                theQry = session.query(models.Reading).filter_by(nodeId=item)
                log.warning("--> Missing Node is {0} A Total of {1} records affected".format(item,theQry.count()))              
                
                #We need to add this Node to the local Database otherwise it can cause problems later on 
                newNode = models.Node(id=item)
                session.add(newNode)

        #TODO (UNCOMMENT THIS)
        session.flush()
        session.commit()
        session.close()

    def sync(self):
        """
        Perform one synchronisation step for this Pusher object

        :return: True if the sync is successfull, False otherwise
        """

        log = self.log
        log.info("Performing sync")
        #Load our Stored Mappings
        self.loadMappings()        

        #config = self.config
        #log.debug("Sync with config {0}".format(config))
        #self.lastUpdate = config.get("lastupdate", None)
        log.debug("Last Update Was {0}".format(self.lastUpdate))


        #Syncronise Sensor Types
        self.syncSensorTypes()

        #Synchronise Nodes
        nodes = self.syncNodes()

        #Start to map the rest
        deployments = self.mapDeployments()

        #Houses
        houses = self.mapHouses(deploymentIds = deployments)

        #And Locations


        self.mapLocations(houseIds = houses)



        #log.setLevel(logging.DEBUG)
        self.updateNodeLocations()
        #log.setLevel(logging.INFO)
        #Print some Debugging Information
        #self.debugMappings()

        #log.setLevel(logging.DEBUG)
        


        #log.setLevel(logging.INFO)

        
        #log.debug("Last update {0}".format(self.lastUpdate))
        #Synchronise Readings
        #return
        samples, lastTime = self.syncReadings()

        log.debug("Remaining Samples {0}".format(samples))
        log.debug("Last Sample Time {0}".format(lastTime))
        self.dumpMappings()
        #Finally update the config file. (Add an tiny Offset to avoid issues
        #with milisecond rounding)
        #self.config['lastupdate'] = lastTime + timedelta(seconds = 1)
        self.lastUpdate = lastTime + timedelta(seconds = 1)

        
        return samples, lastTime

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
        log = self.log
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
                #log.debug(restQry)

                if restQry["headers"]["status"] == '404':
                    log.warning("Error Creating Deployment Item")
                    raise Exception ("Error Creating Deplyment Item")


                #Then map the local and Remote Id's
                restBody = json.loads(restQry['body'])
                log.info("Deployment {0} mapped to {1}".format(mapDep.id,
                                                               restBody['id']))
                mappedDeployments[mapDep.id] = restBody['id']

        lSess.flush()
        lSess.close()
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
        log = self.log
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
        else:
            #If we dont have either of these, fetch any Houses that are "current"
            log.warning("No Out of date Deployments Found, Checking Houses")
            if self.lastUpdate:
                houseQuery = houseQuery.filter(sqlalchemy.or_(House.endDate >= self.lastUpdate,
                                                              House.endDate == None))


        log.debug("Sycnhronising Houses")
        for mapHouse in houseQuery:
            log.debug("--> Mapping House {0}".format(mapHouse))

            theHouse = mappedHouses.get(mapHouse.id, None)
            if theHouse is None:
                #Get the mapped deployment Id
                log.debug("--> --> House Not Mapped")

                #Start to build our Query
                #depId = mappedDeployments[mapHouse.deploymentId]
                depId = mappedDeployments.get(mapHouse.deploymentId,None)
                log.debug("--> Mapped Deployment Is {0}".format(depId))
                params = {"address":mapHouse.address,
                          "deploymentId":depId}

                theUrl = "house/?{0}".format(urllib.urlencode(params))

                theBody = mapHouse.toDict()
                del theBody["id"] #Remove Id
                theBody["deploymentId"] = depId #Ensure we use the correct deployment Ids
                log.debug("The URL {0}".format(theUrl))
                restQry = restSession.request_put(theUrl, body=json.dumps(theBody))
                #log.debug(restQry)

                if restQry["headers"]["status"] == '404':
                    log.warning("Error Creating Deployment Item")
                    raise Exception ("Error Creating Deplyment Item")


                #Then map the local and Remote Id's
                restBody = json.loads(restQry['body'])
                log.info("House {0} mapped to {1}".format(mapHouse.id,
                                                          restBody['id']))
                mappedHouses[mapHouse.id] = restBody['id']

        lSess.flush()
        lSess.close()
        #After that we want to get all locations assoicated with a House
        return [x.id for x in houseQuery]

    def mapRooms(self, roomId):
        """
        Map a room between the Local and Remote Database

        :param roomId: local Room Id to Map
        :return: The remote version of this room
        """
        log = self.log
        mappedRoomTypes = self.mappedRoomTypes
        mappedRooms = self.mappedRooms

        #rSess = self.remoteSession()
        lSess = self.localSession()
        restSession = self.restSession

        #log.debug("Mapping Room {0}".format(roomId))
        log.info("Mapping Room {0}".format(roomId))

        theRoom = lSess.query(models.Room).filter_by(id=roomId).first()
        #log.debug("Mapping Room {0} ({1})".format(theRoom,roomId))
        if theRoom is None:
            log.warning("WTF,No such Room !!!")

        if theRoom.roomType:
            #WE also need to double check that the room type exists
            mapType = mappedRoomTypes.get(theRoom.roomTypeId, None)
            log.debug("Mapped Room Type {0}".format(mapType))
            if mapType is None:
                roomType = theRoom.roomType
                log.debug("--> RoomType {0} not mapped".format(roomType))


                params = {"name":roomType.name}
                theUrl = "roomType/?{0}".format(urllib.urlencode(params))

                theBody = roomType.toDict()
                del theBody["id"]

                restQry = restSession.request_put(theUrl, body=json.dumps(theBody))
                #log.debug(restQry)
                restBody = json.loads(restQry['body'])
                mapType = restBody['id']
                log.info("Room Type {0} mapped to {1}".format(roomType.id,
                                                              mapType))
                mappedRoomTypes[roomType.id] = mapType
        else:
            mapType = None

        #Then Create the Room
        params = {"name":theRoom.name,
                  'roomTypeId':mapType}
        log.debug("Creating Room with Parameters {0}".format(params))
        theUrl = "room/?{0}".format(urllib.urlencode(params))
        theBody = theRoom.toDict()
        del theBody["id"]
        theBody["roomTypeId"] = mapType

        restQry = restSession.request_put(theUrl, body=json.dumps(theBody))
        #log.debug(restQry)

        restBody = json.loads(restQry['body'])
        mapRoom = restBody['id']

        log.info("Room {0} Mapped to {1}".format(theRoom.id,
                                                 mapRoom))

        mappedRooms[theRoom.id] = mapRoom

        lSess.close()
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
        log = self.log
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


        log.debug("Local Ids {0}".format(localIds))
        log.debug("House Ids {0}".format(houseIds))


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

                log.debug("### Location to Map {0}".format(mapLoc))
                log.debug("### ROOM {0}".format(mapLoc.roomId))

                if mapRoom is None:
                    log.info("--> ## Mapping Room {0}".format(mapLoc.roomId))
                    mapRoom = self.mapRooms(mapLoc.roomId)

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

        #log.debug(mappedLocations)
        lSess.flush()
        lSess.close()

    def updateNodeLocations(self):
        """Update Nodes, to take account of the latest Locations"""
        log = self.log
        log.info("---- Updating Node Locations -----")
        #for key,item in self.mappedLocations.iteritems():
        #    log.debug("{0} {1}".format(key,item))
        mappedLocations = self.mappedLocations
        restSession = self.restSession

        #Get a list of locations to update
        locIds = mappedLocations.keys()
        log.debug(locIds)
        session = self.localSession()
        theQry = session.query(models.Node).filter(models.Node.locationId.in_(locIds))
        for item in theQry:
            #theNode = session.query(models.Node).filter_by(id=item).first()
            theDict = item.toDict()
            #Update the Location Id with a mapped location Id
            theDict['locationId'] = mappedLocations[item.locationId]
            #And for the moment remove the node types
            theDict['nodeTypeId'] = None

            

            log.info("Updating Node {0} {1}".format(item,theDict))            
            #Then Update
            theUrl  = "node/{0}".format(item.id)
            restQry = restSession.request_put(theUrl,body=json.dumps(theDict))
            log.debug(restQry)
            if restQry["headers"]["status"] == "500":
                sys.exit()
            

        log.info("Done")

    def debugMappings(self):
        """
        Helper Debug function to print mappings
        """
        return
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

    def dumpMappings(self):
        """Dump all our known mappings to a JSON file"""
        # Storage for mappings between local -> Remote
        log = self.log
        return
        dumpDict = {"dep":self.mappedDeployments.items(),
                    "house":self.mappedHouses.items(),
                    "room":self.mappedRooms.items(),
                    "loc":self.mappedLocations.items(),
                    "rType":self.mappedRoomTypes.items()}
        log.debug("-- ORIG -- ")
        log.debug(dumpDict)
        #log.debug(json.dumps(dumpDict))
        
        #fileStr = "{0}.json".format(self.restUrl)
        fileStr = "forceDump.json"
        with open(fileStr,"wb") as fd:
            json.dump(dumpDict,fd)

    def loadMappings(self):
        """Load known mappings from a JSON file"""
        log = self.log
        log.debug("Loading JSON Mappings")

        restUrl = self.restUrl
        
        #fileStr = "{0}.json".format(self.restUrl)
        fileStr = "forceDump.json"        
        return

        if not os.path.isfile(fileStr):
            log.debug("No Mappings Found")
            return 

        with open(fileStr,"rb") as fd:
            dumpDict = json.load(fd)
            log.debug(dumpDict)
            self.mappedDeployments.update(dict(dumpDict["dep"]))
            self.mappedHouses.update(dict(dumpDict["house"]))
            self.mappedRooms.update(dict(dumpDict["room"]))
            self.mappedLocations.update(dict(dumpDict["loc"]))
            self.mappedRoomTypes.update(dict(dumpDict["rType"]))

        #log.debug(self.mappedHouses)
        #log.debug(dumpDict)

                      
    def syncSensorTypes(self):
        """
        Synchronise Sensor Types with the remote server

        Sensor types should also be the same on all databases.  If this is not
        the case this method attempts to rewrite sensor types to the correct
        (those on the remote server) values
        """

        log = self.log
        log.debug("Synchronising sensor types")

        session = self.localSession()
        remoteSession = self.restSession

        #First Fetch the List of sensor types from the remote server

        remoteQry = remoteSession.request_get("sensortype/")
        remoteItems = json.loads(remoteQry["body"]) 

        #Store for bad items
        matchedItems = {}
        badItems = {}
              

        for item in remoteItems:
            #log.debug("Processing Remote {0} {1}".format(item["id"],item["name"]))
            theQry = session.query(models.SensorType).filter_by(name=item["name"]).first()
            #print theQry
            if theQry is None:
                log.debug("Sensor Type {0} Missing".format(item))
                #badItems[item["id"]] = (item,None)
                #Add this sensor type to the list
                newSensor = models.SensorType(id=item["id"],
                                              name=item["name"],
                                              code=item["code"],
                                              units=item["units"],
                                              c0 = item["c0"],
                                              c1 = item["c1"],
                                              c2 = item["c2"],
                                              c3 = item["c3"])
                session.add(newSensor)
                session.flush()
            else:
                if not item["id"] == theQry.id:
                    badItems[item["id"]] = (item,theQry)
                else:
                    matchedItems[theQry.id] = (item,theQry)

        session.commit()
        #We need to do it this way to avoid a problem in the iterator
        keys = badItems.keys()
        print "Keys ",keys

        switchedItems = ()
                
        #for key,value in badItems.iteritems():
        for key in keys:
            value = badItems[key]
            #print 
            print key,value

            remote,local = value

            targetKey = remote["id"]
            localKey = local.id
            #If we have managed to switch keys over
            if localKey in badItems:
               log.warning("SOME KEYS HAVE BEEN SWITCHED {0} {1}".format(remote,local))
               #TODO  Work out what to do if keys have been switched
               sys.exit(0)

            else:
                #Update with the proper key
                log.debug("Updating sensor type {0} to have key {1}".format(local,targetKey))
                local.id = targetKey
                session.flush()
                del badItems[key]
                matchedItems[key] = local
                
                #And update any Readings
                theReadings = session.query(models.Reading).filter_by(typeId = key)
                theReadings.update({"type": targetKey})
                session.flush()

        session.commit()
                    
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
        log = self.log
        lSess = self.localSession()
        #rSess = self.remoteSession()
        restSession = self.restSession

        log.info("Synchronising Nodes")

        #Get the Rest Objects
        restQuery = restSession.request_get("Node/")

        #Then filter out just ID's
        restBody = json.loads(restQuery["body"])
        rQuery = [x['id'] for x in restBody]

        #log.debug("Remote Nodes :{0}".format(rQuery))
        log.debug("Total of {0} Remote Nodes found".format(len(rQuery)))

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

        bulkUpload = []
        for node in lQuery:
            #log.debug("--> --> Node {0} does not exist on remote server".format(node.id))

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

                #log.debug("Creating Sensor {0}".format(newSensor))
                bulkUpload.append(newSensor)

        jsonBody = json.dumps([x.toDict() for x in bulkUpload])

        #return
        restQuery = restSession.request_post("Bulk/",
                                             body=jsonBody)

        lSess.flush()
        lSess.close()

        if restQuery['headers']['status'] == '201':
            return True
        else:
            log.warning("Error Uploading Nodes {0}".format(restQuery['headers']))
            raise Exception("Error Uploading Nodes")
        

    def syncReadings(self, cutTime=None):
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

        log = self.log
        lSess = self.localSession()
        restSession = self.restSession

        mappedLocations = self.mappedLocations

        #Time stamp to check readings against
        if not cutTime:
            cutTime = self.lastUpdate

        log.info("Synchronising Readings from {0}".format(cutTime))

        #Get the Readings
        readings = lSess.query(models.Reading).order_by(models.Reading.time)
        if cutTime:
            log.debug("Filter all readings since {0}".format(cutTime))
            readings = readings.filter(models.Reading.time >= cutTime)

        #Skip Sensor Type of 14
        readings = readings.filter(models.Reading.typeId != 14)
            
        remainingReadings = readings.count()



        if remainingReadings == 0:
            log.info("No More Readings to Sync")
            return (remainingReadings, cutTime)
        #Limit by the number of items specified in the Config file
        #readings = readings.limit(self.pushLimit)

        #Its a bit of a pain in the Arse, but having this cutoff date makes life a tad tricky.
        #Therefore we find the date of the last sample up to the limit.
        log.setLevel(logging.DEBUG)
        cutoffTime = readings.offset(self.pushLimit).first()
        log.debug("Date of {1}th Reading is {0}".format(cutoffTime,self.pushLimit))
        
        #We can then rebuild our query to go up to this Date 
        
        readings = lSess.query(models.Reading).order_by(models.Reading.time)
        readings = readings.filter(models.Reading.typeId != 14)
        if cutTime:
            readings = readings.filter(models.Reading.time >= cutTime)
        if cutoffTime:
            readings = readings.filter(models.Reading.time <= cutoffTime.time)
            log.debug("Transfer a total of {0} Readings to {1}".format(readings.count(),cutoffTime.time))
        
        #sys.exit(0)
        log.setLevel(logging.WARNING)



        jsonList = []
        for reading in readings:
            #Convert to a JSON and remap the location
            dictReading = reading.toDict()
            #dictReading['locationId'] = mappedLocations[reading.locationId]
            dictReading['locationId'] = mappedLocations.get(reading.locationId,None)
            jsonList.append(dictReading)

        #And then try to bulk upload them
        restQry = restSession.request_post("/bulk/",
                                           body=json.dumps(jsonList))
        #log.debug(restQry)
        if restQry["headers"]["status"] == '404':
            print "==="*80
            log.warning("Upload Fails")
            log.warning(restQry)

            sys.exit(0)
            raise Exception ("Bad Things Happen")
    

        #We also want to update the Node States
        lastSample = readings[-1].time
        log.debug("Last Sample Time {0}".format(lastSample))

        nodeStates = lSess.query(models.NodeState)
        if cutTime:
            nodeStates = nodeStates.filter(models.NodeState.time >= cutTime)
        nodeStates = nodeStates.filter(models.NodeState.time <= lastSample)

        restStates = [x.toDict() for x in nodeStates]
        for item in restStates:
            item["id"] = None

        log.debug("Rest States {0}".format(restStates))
        if restStates:
            restQry = restSession.request_post("/bulk/",
                                               body=json.dumps(restStates))

            if restQry["headers"]["status"] == '404':
                print "==="*80
                log.warning("Upload Fails")
                log.warning(restQry)

                sys.exit(0)

        log.debug("Node States")

        return remainingReadings, lastSample

class PushManual(object):
    """
    Manually initiate a Push Cycle
    """

    def __init__(self,localURL,remoteServer="http://127.0.0.1:6543/rest/",stTime=None):
        """Initilalise a Push Session

        :var localURL: sqlalchemy URL to use for Sync
        :var remoteServer: Base URL of the remote server
        """

        self.log = logging.getLogger("__name__")
        log = self.log
        log.debug("Creating Manual Push session for database {0} to {1}".format(localURL,remoteServer))

        #Initalise the local database connection
        engine = sqlalchemy.create_engine(localURL)
        models.initialise_sql(engine)
        localSession = sqlalchemy.orm.sessionmaker(bind=engine)
        self.localSession = localSession
        
        #Create the Server
        thePusher = Pusher(localSession,
                           remoteServer,
                           stTime,
                           10000,
                           #10,
                           #1,
                           )

        thePusher.checkConnection()
        thePusher.validateData()

        self.thePusher = thePusher

    def sync(self,fileStr,dumpDict,item):
        """Synchronise the server"""

        #ThePusher.sync()
        samples = 10
        while samples > 0:
        #for x in range(5):
            samples, lastTime = self.thePusher.sync()
            print "Last Update {0}".format(lastTime)
            dumpDict[item] = lastTime 

            with open(fileStr,"wb") as fd:
                pickle.dump(dumpDict,fd)

            #print "Total Samples ",samples
            #samples = -1
        return lastTime,dumpDict

    

def compareReadings(localURL):
    """Do a Quick bit of error checking across databases
    To see where a previous update has been succesful
    """
    engine = sqlalchemy.create_engine("mysql://root:Ex3lS4ga@localhost/Gauss")
    #models.initialise_sql(engine)
    LocalSession = sqlalchemy.orm.sessionmaker(bind=engine)
    
    engineTwo = sqlalchemy.create_engine("mysql://root:Ex3lS4ga@localhost/ch")
    #models.initialise_sql(engineTwo)
    RemoteSession = sqlalchemy.orm.sessionmaker(bind=engine)

    """
    SELECT * FROM Gauss.Reading AS Otto INNER JOIN ch.Reading As Ch ON (Otto.nodeId = Ch.nodeId AND Otto.time = Ch.time AND Otto.type = Ch.type)
WHERE Otto.nodeId = 69 AND Otto.type = 0 ORDER BY Otto.time DESC
 LIMIT 10
    """


    localSession = LocalSession()
    remoteSession = RemoteSession()
    #Really its just readings we want to compare.
    
    #Get unique nodestates from the local database

    theQry = localSession.query(sqlalchemy.distinct(models.NodeState.nodeId))
    distinctNodes = theQry.all()
    print "Distinct Node States"
    print distinctNodes

    #Then fetch the last node state for each node
    for node in distinctNodes[:1]:
        #Last Local
        print "Checking Node {0}".format(node)
        lastLocal = localSession.query(models.NodeState).filter_by(nodeId=node[0]).order_by(models.NodeState.time.desc())
        
        print lastLocal
        print lastLocal.first()

        lastRemote = remoteSession.query(models.NodeState).filter_by(nodeId=node[0]).order_by(models.NodeState.time.desc())
        print lastRemote.first()

        # serverState = remoteSession.query(models.NodeState).
        # print "Last Nodestate for this node on server is"


    #For each node get the last reading.
    
    

    
    
    

if __name__ == "__main__":
    import datetime
    import pickle
    logging.debug("Testing Push Classes")

    server = PushServer()
    server.sync()

    #theUrl = "mysql://root:Ex3lS4ga@localhost/{0}".format("Gauss")
    #compareReadings(theUrl)
    #import sys
    #sys.exit(0)
    
    #server = PushManual("mysql://root:Ex3lS4ga@localhost/Einstein")
    #server = PushManual("mysql://root:Ex3lS4ga@localhost/Otto")
    # dumpDict = {}
    # #Push Mappings 
    # fileStr = "manualPush.pickle"
    # try:
    #     with open(fileStr,"rb") as fd:
    #         dumpDict = pickle.load(fd)
    # except:
    #     print "NO PICKELED FILE"
        

    

    # print dumpDict

    # servers = ["Einstein","Euclid","Euler","Gauss","Otto","Tesla"]
    # servers = ["Euclid"]

    # for item in servers:
    #     print "Dealing with {0}".format(item)
    #     theUrl = "mysql://root:Ex3lS4ga@localhost/{0}".format(item)

    #     startTime = dumpDict.get(item,None)
    #     if startTime:
    #         startTime = startTime + datetime.timedelta(seconds=1)
    #     startTime = datetime.datetime(2012,3,2,11,13,50)
    #     server = PushManual(theUrl,stTime=startTime)
    #     lastTime,dumpDict = server.sync(fileStr,dumpDict,item)

#    dumpDict["Otto"] = datetime.datetime.now()
    


    #servers = ["Einstein","Euclid","Euler","Gauss","Tesla"]
    
    #for server in servers:

    #server = PushManual("mysql://root:Ex3lS4ga@localhost/localCh")
    #server.sync()
    #print "Done"
