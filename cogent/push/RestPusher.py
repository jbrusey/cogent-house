
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

   .. since 0.6.0::
   
      Changed to upload readings by house.
"""

import logging
logging.basicConfig(level=logging.INFO)
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
            item.sync()
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


    def sync(self):
        """
        Perform one synchronisation step for this Pusher object

        :return: True if the sync is successfull, False otherwise
        """

        log = self.log
        #log.setLevel(logging.DEBUG)
        log.info("Performing sync")
        #Load our Stored Mappings
        #TODO: update the Load Mappings Script
        self.loadMappings()
        #self.loadMappings() 

        self.syncNodes()

        log.setLevel(logging.DEBUG)
        #I think we should do this by House, Keeps things a little tidier
        session = self.localSession()
        houses = session.query(models.House)

        for item in houses[:2]:
            log.debug("Synchronising Readings for House {0}".format(item))
            self.uploadReadings(item)

        log.setLevel(logging.INFO)
        #session = self.localSession()
        #deployments = session.query(models.Deployment).all()
        
        #log.debug("---- Deployments -----")
        #for item in deployments:
        #    log.debug(item)
        #return

        #config = self.config
        #log.debug("Sync with config {0}".format(config))
        #self.lastUpdate = config.get("lastupdate", None)
        #log.debug("Last Update Was {0}".format(self.lastUpdate))


        #Syncronise Sensor Types
        #self.syncSensorTypes()

        #Synchronise Nodes
        #nodes = self.syncNodes()

        #Start to map the rest
        #deployments = self.mapDeployments()

        #Houses
        #houses = self.mapHouses(deploymentIds = deployments)

        #And Locations


        #self.mapLocations(houseIds = houses)



        #log.setLevel(logging.DEBUG)
        #self.updateNodeLocations()
        #log.setLevel(logging.INFO)
        #Print some Debugging Information
        #self.debugMappings()

        #log.setLevel(logging.DEBUG)
        


        #log.setLevel(logging.INFO)

        
        #log.debug("Last update {0}".format(self.lastUpdate))
        #Synchronise Readings
        #return
        #samples, lastTime = self.syncReadings()

        #log.debug("Remaining Samples {0}".format(samples))
        #log.debug("Last Sample Time {0}".format(lastTime))
        #self.dumpMappings()
        #Finally update the config file. (Add an tiny Offset to avoid issues
        #with milisecond rounding)
        #self.config['lastupdate'] = lastTime + timedelta(seconds = 1)
        #self.lastUpdate = lastTime + timedelta(seconds = 1)

        
        #return samples, lastTime

    def loadMappings(self):
        """Load known mappings from a JSON file"""
        log = self.log
        log.debug("Loading Mappings")

        #restUrl = self.restUrl
        
        #Map Id's etc in the remote datbase to the local DB
        self.mapSensors()
        self.mapRooms()
        self.mapDeployments()
        self.mapHouses() #Then houses
        self.mapLocations()


        return

    def uploadItem(self,theUrl,theBody):
        """Helper function to Add / Fetch a single item from the Database
        """
        #It would be nice to add "reverse" Synchronisation here (i.e. reflect changes on main server).
        log = self.log
        restSession = self.restSession
        restQry = restSession.request_get(theUrl)
        log.debug(restQry)    
        
        #Check if this item exists on the remote server
        #Response of 200 indicates item not found.
        if restQry["body"] == '[]':
            log.debug("Creating new objct on remote server")
            log.debug(json.dumps(theBody))
            restQry = restSession.request_post(theUrl,
                                               body=json.dumps(theBody))                

            #The Query should now hold the Id of the item on the remote DB
            log.debug(restQry)

        jsonBody = json.loads(restQry["body"])    
        restItem = models.clsFromJSON(jsonBody).next()
        #log.debug("Rest --> {0}".format(restItem))
        return restItem

    def mapRooms(self):
        """Function to map Rooms and Room types between the two databases.
        This is a bi-directional sync method    
        """
        
        #First we need to map room Types
        log = self.log
        #log.setLevel(logging.DEBUG)
        session = self.localSession()
        restSession = self.restSession

        #Fetch the room types from the remote Database
        theUrl = "roomtype/"

        remoteTypes = {}
        localTypes = {}


        remoteQry = restSession.request_get(theUrl)
        jsonBody = json.loads(remoteQry['body'])
        log.debug(jsonBody)
        restItems = models.clsFromJSON(jsonBody)

        for item in restItems:
            remoteTypes[item.name] = item

        roomTypes = session.query(models.RoomType)
        for item in roomTypes:
            localTypes[item.name] = item

        mergedRooms = {}
        #Mrege Room Tpyes
        for key,value in localTypes.iteritems():
            rValue = remoteTypes.get(key,None)
            #log.debug("Key({0}) = {1} : {2}".format(key,value,rValue))
            if rValue is None:
                #Add a new remote Room Types
                params = {"name":value.name}
                theUrl = "roomtype/?{0}".format(urllib.urlencode(params))            
            
                theBody = value.toDict()
                del theBody["id"]

                rValue = self.uploadItem(theUrl,theBody)                    
            else:
                #Remove this from the lookup
                del(remoteTypes[key])
                    
            #Then update the mapping dictionary
            mergedRooms[value.id] = rValue

        #We next need to sync the other way.
        log.debug("--> Remote <--")
        for key,value in remoteTypes.iteritems():
            log.debug("{0} {1}".format(key,value))
            log.info("Adding Remote RoomType {0} to local Database".format(value))
            value.id = None
            session.add(value)
            session.flush()
            log.debug(value)
        session.commit()

        self.mappedRoomTypes = mergedRooms

        #Now we have room types, we can map the rooms themselves.
        #log.setLevel(logging.DEBUG)
        theQry = session.query(models.Room)
        theUrl = "room/"

        mergedRooms = {}
        
        for item in theQry:
            #log.debug(item)

            params = {"name":item.name}
            theUrl = "room/?{0}".format(urllib.urlencode(params))            

            theBody = item.toDict()
            del theBody["id"]

            newItem = self.uploadItem(theUrl,theBody) 
            mergedRooms[item.id] = newItem

        self.mappedRooms = mergedRooms



    def mapSensors(self):
        """Function to map Rooms and Room types between the two databases.
        This is a bi-directional sync method    
        """
        
        #First we need to map room Types
        log = self.log
        #log.setLevel(logging.DEBUG)
        session = self.localSession()
        restSession = self.restSession

        #Fetch the room types from the remote Database
        theUrl = "sensortype/"

        remoteTypes = {}
        localTypes = {}


        remoteQry = restSession.request_get(theUrl)
        jsonBody = json.loads(remoteQry['body'])
        log.debug(jsonBody)
        restItems = models.clsFromJSON(jsonBody)

        for item in restItems:
            remoteTypes[item.name] = item

        roomTypes = session.query(models.SensorType)
        for item in roomTypes:
            localTypes[item.name] = item

        mergedRooms = {}
        #Mrege Room Tpyes
        for key,value in localTypes.iteritems():
            rValue = remoteTypes.get(key,None)
            log.debug("Key({0}) = {1} : {2}".format(key,value,rValue))
            if rValue is None:
                #Add a new remote Room Types
                params = {"name":value.name}
                theUrl = "sensortype/?{0}".format(urllib.urlencode(params))            
            
                theBody = value.toDict()
                #del theBody["id"]

                rValue = self.uploadItem(theUrl,theBody)                    
            else:
                #Remove this from the lookup
                del(remoteTypes[key])
                    
            #Then update the mapping dictionary
            mergedRooms[value.id] = rValue

        #We next need to sync the other way.
        log.debug("--> Remote <--")
        for key,value in remoteTypes.iteritems():
            #log.debug("{0} {1}".format(key,value))
            log.info("Adding Remote RoomType {0} to local Database".format(value))
            session.add(value)
            session.flush()
            log.debug(value)
        session.commit()
        self.mappedSensorTypes = mergedRooms

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
        #Deployment = models.Deployment
        depQuery = lSess.query(models.Deployment)

        deploymentMap = {}
        
        #TODO:  Load / Save mappings. Work if there are changes to deployment name on remote server

        for item in depQuery:
            log.debug("Checking Mapping for Deployment {0}".format(item))

            #Look for this deployment on the remote server
            params = {"name":item.name}
            theUrl = "deployment/?{0}".format(urllib.urlencode(params))            

            theBody = item.toDict()
            del theBody["id"]

            newItem = self.uploadItem(theUrl,theBody)            

            deploymentMap[item.id] = newItem

        #And Save this in out Local Version
        self.mappedDeployments = deploymentMap

    def mapHouses(self):
        """Map houses on the Local Database to those on the Remote Database"""
        log = self.log
        log.debug("----- Mapping Houses ------")
        mappedDeployments = self.mappedDeployments
        lSess = self.localSession()
        restSession = self.restSession

        #Get the list of deployments that may need updating
        #Deployment = models.Deployment
        theQry = lSess.query(models.House)

        theMap = {}

        for item in theQry:
            if item.address is None:                
                continue
            #We need to make sure the deployment is mapped correctly
            mapDep = mappedDeployments[int(item.deploymentId)]
            log.debug("{0} maps to {1}".format(item,mapDep))
            params = {"address":item.address,
                      "deploymentId":mapDep.id}
            theUrl = "house/?{0}".format(urllib.urlencode(params))                            

            #Look for the item
            theBody = item.toDict()
            theBody["deploymentId"] = mapDep.id
            del theBody["id"]
            newItem = self.uploadItem(theUrl,theBody)
            theMap[item.id] = newItem
            
        #And Save this in out Local Version
        self.mappedHouses = theMap

    def mapLocations(self):
        #Synchronise Locations
        log = self.log
        log.info("----- Syncing Locations ------")
        lSess = self.localSession()
        restSession = self.restSession

        #Get the list of deployments that may need updating
        #Deployment = models.Deployment
        theQry = lSess.query(models.Location)

        mappedHouses = self.mappedHouses
        mappedRooms = self.mappedRooms
        theMap = {}

        for item in theQry:
            log.debug(item)
            hId = mappedHouses[int(item.houseId)]
            rId =mappedRooms[int(item.roomId)]
            #We need to make sure the deployment is mapped correctly
            params = {"houseId":hId.id,
                      "roomId":rId.id}
            theUrl = "location/?{0}".format(urllib.urlencode(params))                            
            #Look for the item
            theBody = item.toDict()
            theBody["houseId"] = hId.id
            theBody["roomId"] = rId.id
            log.debug("LOCATION {0}={1}".format(item,theBody))
            del(theBody["id"])
            newItem = self.uploadItem(theUrl,theBody)
            theMap[item.id] = newItem

        self.mappedLocations = theMap

    def syncNodes(self):
        """Synchronise Nodes between databases
        This will not 'pull' new nodes down 
        #Currently the node 'Location' field is not updated,  we need to work out how to do this
        while avoiding overwriting a node with an out of date location.

        TODO:  A Couple of potential issues here,  1) no Sych of Location,  No Sync of Sensor Types (calibration)
        """
        log = self.log
        log.debug("----- Syncing Nodes ------")
        lSess = self.localSession()
        restSession = self.restSession

        #Get the list of deployments that may need updating
        #Deployment = models.Deployment
        theQry = lSess.query(models.Node)

        theMap = {}

        for item in theQry:
            log.debug(item)
            #We need to make sure the deployment is mapped correctly
            params = {"id":item.id}
            theUrl = "node/?{0}".format(urllib.urlencode(params))                            

            #Look for the item
            theBody = item.toDict()
            del(theBody["locationId"])
            newItem = self.uploadItem(theUrl,theBody)

        
    def uploadReadings(self,theHouse):
        """
        Syncronise Readings between two databases,
        modified to upload by House
        """
        log = self.log
        log.debug("--- Upload for house {0} ----")
        
        #Load the Mapped items to the local namespace
        mappedLocations = self.mappedLocations
        mappedTypes = self.mappedSensorTypes

        #Get the last reading for this House
        session = self.localSession()
        restSession =self.restSession
        params = {"house":theHouse.address}
        theUrl = "lastSync/"
        restQuery = restSession.request_get(theUrl,args=params)
        log.debug(restQuery)
        
        strDate = json.loads(restQuery['body'])
        log.debug("Str Date {0}".format(strDate))
        lastDate = dateutil.parser.parse(strDate)
        log.debug("Last Upload Date {0}".format(lastDate))

        #Get locations associated with this House
        theLocations = [x.id for x in theHouse.locations]
        log.debug("House Locations {0}".format(theLocations))

        #Fetch some readings
        theReadings = session.query(models.Reading).filter(models.Reading.locationId.in_(theLocations))
        theReadings = theReadings.filter(models.Reading.time > lastDate)
        theReadings = theReadings.order_by(models.Reading.time)
        theReadings = theReadings.limit(5)
        print theReadings
        log.debug("Readings")
        jsonList = [] #Blank Object to hold readings
        for reading in theReadings:
            log.debug(reading)
        
            #Convert our Readings to REST, and remap to the new locations
            dictReading = reading.toDict()

            dictReading['locationId'] = mappedLocations[reading.locationId].id
            dictReading['typeId'] = mappedTypes[reading.typeId].id
            log.debug("--> {0}".format(dictReading))            
            jsonList.append(dictReading)

         #And then try to bulk upload them
        restQry = restSession.request_post("/bulk/",
                                           body=json.dumps(jsonList))
        log.debug(restQry)
    #     if restQry["headers"]["status"] == '404':
    #         print "==="*80
    #         log.warning("Upload Fails")
    #         log.warning(restQry)

    #         sys.exit(0)
    #         raise Exception ("Bad Things Happen")            

        
    # def syncReadings(self, theHouse):
    #     """Synchronise readings between two databases

    #     :param DateTime cutTime: Time to start the Sync from
    #     :return: (Number of Readings that remain to be synchronised,
    #               Timestamp of last reading)

    #     This assumes that Sync Nodes has been called.

    #     The Algorithm for this is:

    #     Initialise Temporary Storage, (Location = {})

    #     #. Get the time of the most recent update from the local database
    #     #. Get all Local Readings after this time.
    #     #. For Each Reading

    #         #. If !Location in TempStore:
    #             #. Add Location()
    #         #. Else:
    #             #. Add Sample

    #     # If Sync is successful, fix the last update timestamp and return
    #     """

    #     log = self.log
    #     lSess = self.localSession()
    #     restSession = self.restSession

    #     mappedLocations = self.mappedLocations

    #     #Time stamp to check readings against
    #     if not cutTime:
    #         cutTime = self.lastUpdate

    #     log.info("Synchronising Readings from {0}".format(cutTime))

    #     #Get the Readings
    #     readings = lSess.query(models.Reading).order_by(models.Reading.time)
    #     if cutTime:
    #         log.debug("Filter all readings since {0}".format(cutTime))
    #         readings = readings.filter(models.Reading.time >= cutTime)

    #     #Skip Sensor Type of 14
    #     readings = readings.filter(models.Reading.typeId != 14)
            
    #     remainingReadings = readings.count()



    #     if remainingReadings == 0:
    #         log.info("No More Readings to Sync")
    #         return (remainingReadings, cutTime)
    #     #Limit by the number of items specified in the Config file
    #     #readings = readings.limit(self.pushLimit)

    #     #Its a bit of a pain in the Arse, but having this cutoff date makes life a tad tricky.
    #     #Therefore we find the date of the last sample up to the limit.
    #     log.setLevel(logging.DEBUG)
    #     cutoffTime = readings.offset(self.pushLimit).first()
    #     log.debug("Date of {1}th Reading is {0}".format(cutoffTime,self.pushLimit))
        
    #     #We can then rebuild our query to go up to this Date 
        
    #     readings = lSess.query(models.Reading).order_by(models.Reading.time)
    #     readings = readings.filter(models.Reading.typeId != 14)
    #     if cutTime:
    #         readings = readings.filter(models.Reading.time >= cutTime)
    #     if cutoffTime:
    #         readings = readings.filter(models.Reading.time <= cutoffTime.time)
    #         log.debug("Transfer a total of {0} Readings to {1}".format(readings.count(),cutoffTime.time))
        
    #     #sys.exit(0)
    #     log.setLevel(logging.WARNING)



    #     jsonList = []
    #     for reading in readings:
    #         #Convert to a JSON and remap the location
    #         dictReading = reading.toDict()
    #         #dictReading['locationId'] = mappedLocations[reading.locationId]
    #         dictReading['locationId'] = mappedLocations.get(reading.locationId,None)
    #         jsonList.append(dictReading)

    #     #And then try to bulk upload them
    #     restQry = restSession.request_post("/bulk/",
    #                                        body=json.dumps(jsonList))
    #     #log.debug(restQry)
    #     if restQry["headers"]["status"] == '404':
    #         print "==="*80
    #         log.warning("Upload Fails")
    #         log.warning(restQry)

    #         sys.exit(0)
    #         raise Exception ("Bad Things Happen")
    

    #     #We also want to update the Node States
    #     lastSample = readings[-1].time
    #     log.debug("Last Sample Time {0}".format(lastSample))

    #     nodeStates = lSess.query(models.NodeState)
    #     if cutTime:
    #         nodeStates = nodeStates.filter(models.NodeState.time >= cutTime)
    #     nodeStates = nodeStates.filter(models.NodeState.time <= lastSample)

    #     restStates = [x.toDict() for x in nodeStates]
    #     for item in restStates:
    #         item["id"] = None

    #     log.debug("Rest States {0}".format(restStates))
    #     if restStates:
    #         restQry = restSession.request_post("/bulk/",
    #                                            body=json.dumps(restStates))

    #         if restQry["headers"]["status"] == '404':
    #             print "==="*80
    #             log.warning("Upload Fails")
    #             log.warning(restQry)

    #             sys.exit(0)

    #     log.debug("Node States")

    #     return remainingReadings, lastSample


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
