
"""
Modified version of the push script that will fetch all items,
convert to JSON and (eventually) transfer across REST

This replaces the ssh tunnel database access currently used to transfer samples.

However, for the moment synchronising the Locations etc (or the complex bit) is
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
       duplicate nodestates turning up if there is a failure

    .. since 0.4::

       Overhaul of the system to make use of REST to upload samples rather than
       transfer data across directly.

    .. since 0.4.1::

       Make use of an .ini style config file to set everything up

       Split functionality into a Daemon, and Upload classes.  This should
       make maintenance of any local mappings a little easier to deal with.


    .. since 0.4.2::

       Store any mappings as a pickled object.

   .. since 0.5.0::
       
       New Functionality to manually sync a database from scratch
       Some Changes to logging functionality

   .. since 0.6.0::
   
      Changed to upload readings by house.
      Modified initialisation to be a little more same
   
   .. since 0.7.0::
   
      Mapping configuration file added

"""

import logging
logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.INFO,filename="pushCogentee.log")
#logging.basicConfig(level=logging.WARNING)

__version__ = "0.7.0"

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

        self.log = logging.getLogger(__name__)
        log = self.log
        log.setLevel(logging.DEBUG)
        log.info("Initialising Push Server")

        #Load and Read the Configuration files
        configParser = configobj.ConfigObj("synchronise.conf")
        self.configParser = configParser

        #Process General Configuration Options and Initialise Local Database connection.
        log.info("Processing Global Configuration options")
        generalOptions = configParser["general"]
        
        #Local Database Connection
        if not localURL:
            localURL = generalOptions["localUrl"]
        
        log.debug("Connecting to local database at {0}".format(localURL))

        #Initialise the local database connection
        engine = sqlalchemy.create_engine(localURL)
        models.initialise_sql(engine)
        localSession = sqlalchemy.orm.sessionmaker(bind=engine)
        self.localSession = localSession
        log.info("Database Connection to {0} OK".format(localURL))
        # #DEBUG: And test this connection reporting total number of houses
        # session = localSession()
        # theQry = session.query(models.House).count()
        # log.debug("Total of {0} houses in database".format(theQry))

        #We also need to know the "Limit" on items to push
        pushLimit = generalOptions["pushlimit"]
        log.debug("Push Limit is {0}".format(pushLimit))

        #Open / Build a config object to store mappings for this location
        mappingName = "{0}_Map.conf".format(localURL.split("@")[-1])
        mappingName = mappingName.replace("/","-")
        log.debug("Open Config Object for {0}".format(mappingName))
        mappingConfig = configobj.ConfigObj(mappingName)
        #mappingConfig.filename = mappingName
        #Append a warning to the start of the config file
        mappingConfig.initial_comment = ["This file holds details of mappings between local and remote objects",
                                         "It is strongly recommended that you do not edit!!",
                                         "I take no responsibility for Bad Things(TM) happening if changes are made",
                                         ""]

        #Next we want to queue up all the remote URLS we wish to push to.
        syncList = []
        #Locations in the config File
        locations = configParser["locations"]
        #print locations
        
        for item in locations:
            #Check if we need to synchronise to this location.
            needSync = locations.as_bool(item)
            log.debug("Location {0} Needs Sync {1}".format(item,needSync))

            if needSync:
                #Enque
                thisLoc = configParser[item]
                log.info("Adding {0} to synchronise Queue".format(thisLoc))
                thePusher = Pusher(localSession, #Session
                                   thisLoc["resturl"], #Url to Push to
                                   mappingConfig, #Mapping Configuration file
                                   pushLimit,                                   
                                   )
                syncList.append(thePusher)

        self.syncList = syncList
        #locationQueue = self.readConfig(configParser)
        #print locationQueue
        #Read the Configuration File
        # generalConf, locationConfig = self.readConfig()
        # log.debug("General Configuation")
        # log.debug(generalConf)

        # log.debug("---- Location Configuration ----")
        # log.debug(locationConfig)

        #Store the config
        #self.generalConf = generalConf

        #if not localURL:
        #    localURL = generalConf["localUrl"]

        #log.info("Connecting to local database at {0}".format(localURL))

        # #Initalise the local database connection
        # engine = sqlalchemy.create_engine(localURL)
        # models.initialise_sql(engine)
        # localSession = sqlalchemy.orm.sessionmaker(bind=engine)
        # self.localSession = localSession

        # #And test this connection reporting total number of houses
        # session = localSession()
        # theQry = session.query(models.House).count()
        # log.debug("Total of {0} houses in database".format(theQry))

        #Create a new Pusher object for this each item given in the config
        # syncList = []
        # for item in locationConfig.values():
        #     log.debug("")
        #     log.info("--> Initalising pusher for {0} {1} {2}".format(localSession,generalConf,item))
        #     thePusher = Pusher(localSession,
        #                        item["resturl"], #Rest URL
        #                        item["lastupdate"], #Last Update Time
        #                        generalConf["pushlimit"], #Pusg Limit
        #                        self.confParser #The Config File Itself
        #                        )
            
        #     thePusher.checkConnection()
        #     #thePusher.validateData()

        #     syncList.append(thePusher)

        # self.syncList = syncList
        #self.theConfig = theConfig

    # def readConfig(self,configParser):
    #     """Read configuration from the config file.

    #     This will parse the synchronise.conf file, and produce a local
    #     dictionary of all objects that need synchronising.

    #     :var configParser: The config Parser object we are reading from
    #     :return: A dictionary of parameters (as a list) where syncronisation is
    #     required
    #     """
    #     log = self.log
    #     #confParser = self.configParser
    #     log.info("Reading Config File for locations to update")

    #     #Dictionary to return
    #     syncDict = {}

    #     #generalOpts = confParser["general"]


    #     #Get the Locations
    #     locations = confParser["locations"]

    #     for loc in locations:
    #         isBool = locations.as_bool(loc)
    #         #log.debug("--> Processing Location {0} {1}".format(loc, isBool))
    #         if isBool:
    #             items = confParser[loc]
    #             if items.get("lastupdate", None) in [None, "None"]:
    #                 items["lastupdate"] = None
    #             else:
    #                 #We need to parse the last time
    #                 theTime = dateutil.parser.parse(items["lastupdate"])
    #                 items["lastupdate"] = theTime
    #             syncDict[loc] = items

    #     self.confParser = confParser
    #     return generalOpts, syncDict


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

    def __init__(self, localSession,restUrl,dbConfig,pushLimit=5000):
        """Initalise a pusher object

        :param localSession: A SQLA session, connected to the local database
        :param restUrl: URL of rest interface to upload to
        :param dbConfig: Config Parser that holds details of mappings for the DB we are synching
        :param pushLimit: Number of samples to transfer in each "Push"
        """

        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)
        #self.log.setLevel(logging.WARNING)
        log = self.log
        

        log.debug("Initialising Push Object")
        #Save the Parameters
        self.localSession = localSession
        self.pushLimit = pushLimit

        log.debug("Starting REST connection for {0}".format(restUrl))
        self.restUrl = restUrl
        self.restSession = restful_lib.Connection(restUrl)
        self.dbConfig = dbConfig

        #And get the individual mappings for this particaular Remote URLS
        mappingConfig = dbConfig.get(restUrl,None)
        if mappingConfig is None:
            log.info("No Mapping in ConfigFile for URL {0}".format(restUrl))
            mappingConfig = {"lastupdate":{}}
            dbConfig[restUrl] = mappingConfig
            dbConfig.write()

        self.mappingConfig = mappingConfig
        #self.mappingConfig = dbConfig[restUrl]

        #Load the relevant sections from the config file
        #self.mappedDeployments = mappingConfig.get("deployment",{})
        #for item in deployments:
        #    log.debug(item)

        # Storage for mappings between local -> Remote
        self.mappedDeployments = {}
        self.mappedHouses = {}
        self.mappedRooms = {}
        self.mappedLocations = {}
        self.mappedRoomTypes = {}

        dbConfig[restUrl] = mappingConfig
        dbConfig.write()
        

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
        #return

        self.syncNodes()

        #log.setLevel(logging.DEBUG)
        #I think we should do this by House, Keeps things a little tidier
        session = self.localSession()
        houses = session.query(models.House)
        
        mappingConfig = self.mappingConfig

        #FIXME
        for item in houses[1:2]:
            log.debug("Synchronising Readings for House {0}".format(item))
            #Look for the Last update
            self.uploadReadings(item)

        self.saveMappings()
        #log.setLevel(logging.INFO)
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
        """Load known mappings from the config file,
        then update with new mappings"""
        log = self.log
        log.info("--- Loading Mappings ---")

        log.debug("Load from Config file")
        #restUrl = self.restUrl
        session = self.localSession()
        
        #Map Id's etc in the remote datbase to the local DB
        self.mapSensors()
        self.mapRooms()

        self.mapDeployments()
        self.mapHouses() #Then houses

        self.mapLocations()

        self.saveMappings()
        #return

    def saveMappings(self):
        """Save mappings to a file"""
        mappingConfig = self.mappingConfig
        #print mappingConfig
        mappingConfig["deployment"] = dict([(str(k),v) for k,v in self.mappedDeployments.iteritems()])
        mappingConfig["house"] = dict([(str(k),v) for k,v in self.mappedHouses.iteritems()])
        mappingConfig["location"] = dict([(str(k),v) for k,v in self.mappedLocations.iteritems()])

        # print "-"*50
        # print mappingConfig
        # print "-"*50
        self.dbConfig[self.restUrl] = self.mappingConfig
        self.dbConfig.write()

    def uploadItem(self,theUrl,theBody):
        """Helper function to Add / Fetch a single item from the Database
        """
        #It would be nice to add "reverse" Synchronisation here (i.e. reflect changes on main server).
        log = self.log
        restSession = self.restSession
        restQry = restSession.request_get(theUrl)
        
        #Check if this item exists on the remote server
        #Response of 200 indicates item not found.
        if restQry["body"] == '[]':
            log.debug("Creating new objct on remote server")
            #log.debug(json.dumps(theBody))
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
        This is a bi-directional sync method, room types should also be global (although ID's may vary)
        """
        
        log = self.log
        session = self.localSession()
        restSession = self.restSession
        log.info("Mapping Rooms")
        #First we need to map room Types

        #Fetch the room types from the remote Database
        theUrl = "roomtype/"

        remoteTypes = {}
        localTypes = {}

        #Fetch All room Types the Remote Database knows about
        remoteQry = restSession.request_get(theUrl)
        jsonBody = json.loads(remoteQry['body'])
        restItems = models.clsFromJSON(jsonBody)

        #Build a dictionary
        for item in restItems:
            remoteTypes[item.name] = item

        #Fetch Local Version of room types
        roomTypes = session.query(models.RoomType)
        for item in roomTypes:
            localTypes[item.name] = item

        #And Merge, 
        mergedRooms = {}
        #First add new Remote types
        for key,value in localTypes.iteritems():
            rValue = remoteTypes.get(key,None)
            if rValue is None:
                #Add a new remote Room Types
                log.info("Adding Room Type {0} to Remote Database".format(value))
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

        #We next need to sync the other way, and add new Local Room Types.
        for key,value in remoteTypes.iteritems():
            log.info("Adding Remote RoomType {0} to local Database".format(value))
            value.id = None
            session.add(value)
            session.flush()
        session.commit()

        self.mappedRoomTypes = mergedRooms

        #Now we have room types, we can map the rooms themselves.
        theQry = session.query(models.Room)
        theUrl = "room/"
        mergedRooms = {}

        for item in theQry:
            params = {"name":item.name}
            theUrl = "room/?{0}".format(urllib.urlencode(params))            

            theBody = item.toDict()
            del theBody["id"]

            newItem = self.uploadItem(theUrl,theBody) 
            mergedRooms[item.id] = newItem

        self.mappedRooms = mergedRooms
 


    def mapSensors(self):
        """Function to map Sensors and Sensor types between the two databases.
        This is a bi-directional sync method as Sensor Types should EXACTLY match in ALL databases.
        """
        
        #First we need to map room Types
        log = self.log
        log.info("Mapping Sensors between databases")
        session = self.localSession()
        restSession = self.restSession

        #Fetch the sensor types from the remote Database
        theUrl = "sensortype/"

        remoteTypes = {}
        localTypes = {}

        remoteQry = restSession.request_get(theUrl)
        jsonBody = json.loads(remoteQry['body'])
        restItems = models.clsFromJSON(jsonBody)

        for item in restItems:
            remoteTypes[item.name] = item

        itemTypes = session.query(models.SensorType)
        for item in itemTypes:
            localTypes[item.name] = item

        mergedItems = {}
        #Mrege Item Tpyes

        #Add any new sensors to the remote database
        for key,value in localTypes.iteritems():
            rValue = remoteTypes.get(key,None)
            if rValue is None:
                #Add a new remote Item Types
                log.debug("Adding Sensor Type {0} to remote DB".format(value))
                params = {"name":value.name}
                theUrl = "sensortype/?{0}".format(urllib.urlencode(params))            
            
                theBody = value.toDict()
                #del theBody["id"]
                rValue = self.uploadItem(theUrl,theBody)                    
            else:
                #Remove this from the lookup
                del(remoteTypes[key])
                    
            #Then update the mapping dictionary
            mergedItems[value.id] = rValue

        #We next need to pull any new types from the remote database
        for key,value in remoteTypes.iteritems():
            #log.debug("{0} {1}".format(key,value))
            log.debug("Adding Remote SensorType {0} to local Database".format(value))
            session.add(value)
            session.flush()
            log.debug(value)
        session.commit()
        self.mappedSensorTypes = mergedItems

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

        #Fetch deployments we know about from config file
        log.debug("Loading Known mappings from config file")
        mappingConfig = self.mappingConfig
        configDeployments = mappingConfig.get("deployment",{})
        mappedDeployments.update(dict([(int(k),v) for k,v in configDeployments.iteritems()]))

        depQuery = lSess.query(models.Deployment)
       
        #TODO:  Load / Save mappings. Work if there are changes to deployment name on remote server

        for item in depQuery:
            log.debug("Checking Mapping for Deployment {0}".format(item))
            if item.id in mappedDeployments:
                log.debug("--> Deployment {0} Exists in config file".format(item))
                continue
            #Look for this deployment on the remote server
            params = {"name":item.name}
            theUrl = "deployment/?{0}".format(urllib.urlencode(params))            

            theBody = item.toDict()
            del theBody["id"]

            newItem = self.uploadItem(theUrl,theBody)            
            log.debug("--> Deployment {0} Mapped to {1} ({2}:{3})".format(item,newItem,item.id,newItem.id))
            #deploymentMap[item.id] = newItem
            mappedDeployments[item.id] = newItem.id
            
        log.debug("Mapped Deps: {0}".format(mappedDeployments))
        #print mappedDeployments
        #And Save this in out Local Version
        #self.mappedDeployments = deploymentMap

    def mapHouses(self):
        """Map houses on the Local Database to those on the Remote Database"""
        log = self.log
        log.debug("----- Mapping Houses ------")
        mappedDeployments = self.mappedDeployments
        mappedHouses = self.mappedHouses
        lSess = self.localSession()
        restSession = self.restSession

        log.debug("Loading Known Houses from config file")
        mappingConfig = self.mappingConfig
        configHouses = mappingConfig.get("house",{})
        mappedHouses.update(dict([(int(k),v) for k,v in configHouses.iteritems()]))

        #Get the list of deployments that may need updating
        #Deployment = models.Deployment
        theQry = lSess.query(models.House)

        #theMap = {}

        for item in theQry:
            log.debug("Check Mapping for {0}".format(item))
            #if item.address is None:                
            #    continue
            if item.id in mappedHouses:
                log.debug("--> House {0} Exists in config file".format(item))
                continue
            #We need to make sure the deployment is mapped correctly
            mapDep = mappedDeployments[int(item.deploymentId)]
            params = {"address":item.address,
                      "deploymentId":mapDep}
            theUrl = "house/?{0}".format(urllib.urlencode(params))                            

            #Look for the item
            theBody = item.toDict()
            theBody["deploymentId"] = mapDep
            del theBody["id"]
            newItem = self.uploadItem(theUrl,theBody)
            log.debug("House {0} maps to {1} ({2}:{3})".format(item,newItem,item.id,newItem.id))
            mappedHouses[item.id] = newItem.id
            
        log.debug("Map House: {0}".format(mappedHouses))
        #And Save this in out Local Version
        #self.mappedHouses = theMap

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
        print "-"*30, mappedHouses
        mappedRooms = self.mappedRooms
        mappedLocations = self.mappedLocations
        
        mappingConfig = self.mappingConfig
        configLoc = mappingConfig.get("location",{})
        mappedLocations.update(dict([(int(k),v) for k,v in configLoc.iteritems()]))
        #theMap = {}

        for item in theQry:
            #log.debug(item)
            if item.id in mappedLocations:
                log.debug("Location Exists in Config File {0}".format(item))
                continue
            print item
            print "HID: ",item.houseId
            hId = mappedHouses[int(item.houseId)]
            rId =mappedRooms[int(item.roomId)]
            #We need to make sure the deployment is mapped correctly
            params = {"houseId":hId,
                      "roomId":rId.id}
            theUrl = "location/?{0}".format(urllib.urlencode(params))                            
            #Look for the item
            theBody = item.toDict()
            theBody["houseId"] = hId
            theBody["roomId"] = rId.id
            #log.debug("LOCATION {0}={1}".format(item,theBody))
            del(theBody["id"])
            newItem = self.uploadItem(theUrl,theBody)
            #theMap[item.id] = newItem
            mappedLocations[item.id] = newItem.id

        #self.mappedLocations = theMap

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
        #log.setLevel(logging.DEBUG)
        log.info("--- Upload for house {0} ----".format(theHouse))

        #Load the Mapped items to the local namespace
        mappedLocations = self.mappedLocations
        mappedTypes = self.mappedSensorTypes
        
        #Mapping Config
        mappingConfig = self.mappingConfig

        #Load the last upload Date from config file [Not Implemented at the moment]
        # uploadDates = mappingConfig.get("lastupdate",{})
        # lastUpload = uploadDates.get(str(theHouse.id),None)
        # log.debug("Last Upload is {0}".format(lastUpload))
        # if lastUpload is not None:
        #     #Process the last upload Date
        #     lastUpload = dateutil.parser.parse(lastUpload)
        #     log.debug("--> Processed last Upload is {0}".format(lastUpload))


        #Get the last reading for this House
        session = self.localSession()
        restSession =self.restSession
        log.setLevel(logging.DEBUG)
        #Sanity check query for last update
        log.info("--> Requesting date of last reading in Remote DB")
        params = {"house":theHouse.address}
        theUrl = "lastSync/"
        restQuery = restSession.request_get(theUrl,args=params)
        #log.debug(restQuery)
        
        strDate = json.loads(restQuery['body'])
        log.debug("Str Date {0}".format(strDate))
        if strDate is None:
            log.info("--> --> No Readings")
            lastDate = None
        else:
            lastDate = dateutil.parser.parse(strDate)
            log.info("--> Last Upload Date {0}".format(lastDate))
        #if lastDate != lastUpload:
        #    log.warning("Config / Remote last Updates do not match !! {0} {1}".format(lastUpload,lastDate))

        #uploadDates[str(theHouse.id)] = lastDate
        #mappingConfig["lastupdate"] = uploadDates

        #Get locations associated with this House
        theLocations = [x.id for x in theHouse.locations]
        #log.debug("House Locations {0}".format(theLocations))

        #Fetch some readings
        theReadings = session.query(models.Reading).filter(models.Reading.locationId.in_(theLocations))
        if lastDate:
            theReadings = theReadings.filter(models.Reading.time > lastDate)
        theReadings = theReadings.order_by(models.Reading.time)
        origCount = theReadings.count()
        log.info("--> Total of {0} samples to transfer".format(origCount))
        rdgCount = origCount
        transferCount = 0
                           #FIXME
                           
        for x in range(5):
        #while rdgCount > 0:
        #while True:
            theReadings = session.query(models.Reading).filter(models.Reading.locationId.in_(theLocations))
            if lastDate:
                theReadings = theReadings.filter(models.Reading.time > lastDate)
            theReadings = theReadings.order_by(models.Reading.time)
            theReadings = theReadings.limit(self.pushLimit)
            rdgCount = theReadings.count()
            if rdgCount <= 0:
                log.info("No Readings Remain")
                return True

            transferCount += rdgCount
            #print theReadings
            log.info("--> Transfer {0}/{1} Readings to remote DB".format(transferCount,origCount))
            jsonList = [] #Blank Object to hold readings
            for reading in theReadings:
                #log.debug(reading)

                #Convert our Readings to REST, and remap to the new locations
                dictReading = reading.toDict()

                dictReading['locationId'] = mappedLocations[reading.locationId]
                dictReading['typeId'] = mappedTypes[reading.typeId].id
                #log.debug("--> {0}".format(dictReading))            
                jsonList.append(dictReading)
                lastSample = reading.time


             #And then try to bulk upload them
            restQry = restSession.request_post("/bulk/",
                                               body=json.dumps(jsonList))
            log.debug(restQry)

            if restQry["headers"]["status"] == '404':
                print "==="*80
                log.warning("Upload Fails")
                log.warning(restQry)
                raise Exception ("Upload Fails")            

            log.info("--> Readings up to {0} transferred successfully".format(lastSample))
            lastDate = lastSample
                     
        #Return True if we need to upload more
        return rdgCount > 0
            

        
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
