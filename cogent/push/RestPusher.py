"""
Modified version of the push script that will fetch all items,
convert to JSON and (eventually) transfer across REST

This replaces the ssh tunnel database access currently used to transfer samples.

    .. note::

        I currently add 1 second to the time the last sample was transmitted,
        this means that there is no chance that the query to get readings will
        return an item that has all ready been synced, leading to an integrity
        error.

        I have tried lower values (0.5 seconds) but this pulls the last synced
        item out, this is possibly a error induced by mySQL's datetime not
        holding microseconds.

    .. since 0.1.0::

       Moved ssh port forwarding to paramiko (see sshclient class) This should
       stop the errors when there is a connection problem.

    .. since 0.1.1::

       * Better error handling
       * Pagination for sync results, transfer at most PUSH_LIMIT items at a
         time.

    .. since 0.1.2::

       Moved Nodestate Sync into the main readings sync class, this should stop
       duplicate nodestates turning up if there is a failure

    .. since 0.2.0::

       Overhaul of the system to make use of REST to upload samples rather than
       transfer data across directly.

    .. since 0.2.1::

       Make use of an .ini style config file to set everything up

       Split functionality into a Daemon, and Upload classes.  This should
       make maintenance of any local mappings a little easier to deal with.

   .. since 0.2.2::
       
       New Functionality to manually sync a database from scratch
       Some Changes to logging functionality

   .. since 0.3.0::
   
      Changed to upload readings by house.
      Modified initialisation to be a little more same
   
   .. since 0.3.1::
   
      Mapping configuration file added
      0.7.1  Update so logging also goes to file
      0.7.2  Bigfix for Null items in HouseId etc
   
   .. since 0.3.2::

      Some Code broken into seperate functions, to make interitance for the Samson Pusher class a little easier.
      Examples of this include Pusher.CreateEngine() and Pusher.Queue()

   .. since 0.3.3::
   
      Moved from rest_client to requests,  This should avoid the "broken pipe" error.

   .. since 0.3.4::
   
      Now use GZIP compression for bulk uploads
   
"""

import logging
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(name)-10s %(levelname)-8s %(message)s",
                    datefmt = "%m-%d-%Y %H:%M",
                    )
#Add a File hander
#fh = logging.FileHandler("push_out.log")
logsize = (1024*1024) * 5 #5Mb Logs

import logging.handlers
fh = logging.handlers.RotatingFileHandler("push_test.log",maxBytes=logsize,backupCount = 5)
fh.setLevel(logging.INFO)

fmt = logging.Formatter("%(asctime)s %(name)-10s %(levelname)-8s %(message)s")
fh.setFormatter(fmt)

__version__ = "0.3.4"

import sqlalchemy

import cogent

import cogent.base.model as models

import cogent.base.model.meta as meta
from datetime import timedelta

import time

import os.path
import configobj
import zlib

import dateutil.parser
import json
import urllib

import requests
#Disable Requests Logging
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

import sys

#Class to compare dictionary obejcts
class DictDiff(object):
    """
    Check two dictionarys and calculate differences between them
    """
    def __init__(self,mine,other):
        self.mine, self.other = mine,other 
        #Set of keys in each dict
        self.set_mine = set(mine.keys())
        self.set_other = set(other.keys())
        #Intersection between keys
        self.intersect = self.set_mine.intersection(self.set_other)
    
    def added(self):
        """Find items added to the dictionary.

        This will return a set of items that are in "other", 
        that are not in "mine"

        :return: set of new items
        """
        return self.set_mine - self.intersect 

    def removed(self):
        """Return items that have been removed from the dictionary.
        Will return a set of items that are in "mine" but not in "other"
        :return: set of removed items
        """
        return self.set_other - self.intersect
   
    def changed(self):
        """Return items that have changed between dictionarys"""
        changed = [x for x in self.intersect if self.other[x] != self.mine[x]]
        #print changed
        return set(changed)

    def unchanged(self):
        """Return items that are the same between dictionarys"""
        unchanged = [x for x in self.intersect if self.other[x] == self.mine[x]]
        return set(unchanged)
        

class MappingError(Exception):
    """Exception raised for errors when Mapping Items.

    Attributes:
        msg  -- explanation of the error
    """

    def __init__(self, expr,msg):
        self.expr = expr
        self.msg = msg

    def __str__(self):
        return "\n{0}\n{1}".format(self.msg,self.expr)

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

        #Create Logging
        self.log = logging.getLogger("Push Server")
        log = self.log
        log.addHandler(fh)
        log.info("="*70)
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
        self.createEngine(localURL)

        localSession = self.localSession
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

        

        self.QueueLocations(configParser,mappingConfig,pushLimit)

    def QueueLocations(self,configParser,mappingConfig,pushLimit):
        """
        Function to enque a set of locations that the push server is to push to

        :param configParser: Config parser object we are reading from
        :param mappingConfig: Config parser object we are writing to
        :param pushLimit: Maximum number of samples to transmit in one go.
        """

        #Create a session
        localSession = self.localSession
        log = self.log
        syncList = []

        #Read Locations in the config File
        locations = configParser["locations"]

        #For Each location we are looking at
        for item in locations:
            #Check if we need to synchronise to this location.
            needSync = locations.as_bool(item)
            log.debug("Location {0} Needs Sync >{1}".format(item,needSync))

            if needSync: #Enqueue
                thisLoc = configParser[item]
                log.info("Adding {0} to synchronise Queue".format(thisLoc))
                thePusher = Pusher(localSession, #Session
                                   thisLoc["resturl"], #Url to Push to
                                   mappingConfig, #Mapping Configuration file
                                   pushLimit,  #Limit on number of samples to transmit                                 
                                   )
                syncList.append(thePusher)

        self.syncList = syncList        

    def createEngine(self,localURL):
        """Create a connection to the DB engine"""
        log = self.log
        engine = sqlalchemy.create_engine(localURL)
        models.initialise_sql(engine)
        localSession = sqlalchemy.orm.sessionmaker(bind=engine)
        self.localSession = localSession
        log.info("Database Connection to {0} OK".format(localURL))


    def sync(self):
        """
        Run one instance of the synchroniseation mechnism.

        For each item in the config file, perform synchronisation.
        :return: True on success,  False otherwise
        """

        log = self.log
        loopStart = time.time()
        avgTime = None
        log.info("Running Full Syncronise Cycle")

        for item in self.syncList:
            log.debug("Synchronising {0}".format(item))
            item.sync()

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

        self.log = logging.getLogger("Pusher")
        #self.log.setLevel(
        #self.log.setLevel(logging.INFO)
        #self.log.setLevel(logging.WARNING)
        log = self.log
        log.addHandler(fh)

        log.debug("Initialising Push Object")
        #Save the Parameters
        self.localSession = localSession
        self.pushLimit = pushLimit

        log.debug("Starting REST connection for {0}".format(restUrl))
        self.restUrl = restUrl
        #self.restSession = restful_lib.Connection(restUrl)
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
        #Evidently we need to map Sensor Types too
        self.mappedSensorTypes = {}

        dbConfig[restUrl] = mappingConfig
        dbConfig.write()
        
        #And a horribly hacky way to load Classes into memory so inhritance is simple
        self.SensorType = models.SensorType
        self.RoomType = models.RoomType
        self.Room = models.Room
        self.Deployment = models.Deployment
        self.House = models.House
        self.Node = models.Node
        self.Location = models.Location


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

        log.debug("Performing sync")
        #Load our Stored Mappings
        #TODO: update the Load Mappings Script
        self.syncSensorTypes()       
        self.syncRoomTypes()
        self.syncRooms() 
        self.syncDeployments()
        self.loadMappings()
        self.saveMappings()

        #Moved here for the Sampson Version
        self.syncNodes()
        

        session = self.localSession()
        houses = session.query(self.House)   
        mappingConfig = self.mappingConfig

        ##FIXME
        for item in houses:
           log.info("Synchronising Readings for House {0}".format(item))
           #Look for the Last update
           self.uploadReadings(item)

        #Then upload the node Sttes
        self.uploadNodeStates()
        self.saveMappings()

    def loadMappings(self):
        """Load known mappings from the config file,
        then update with new mappings"""
        log = self.log
        log.info("--- Loading Mappings ---")


        #self.mapDeployments()
        self.mapHouses() #Then houses
        self.mapLocations()
        log.info("---- Save Mappings ----")
        self.saveMappings()


    def saveMappings(self):
        """Save mappings to a file"""
        mappingConfig = self.mappingConfig

        mappingConfig["deployment"] = dict([(str(k),v) for k,v in self.mappedDeployments.iteritems()])
        mappingConfig["house"] = dict([(str(k),v) for k,v in self.mappedHouses.iteritems()])
        mappingConfig["location"] = dict([(str(k),v) for k,v in self.mappedLocations.iteritems()])
        mappingConfig["room"] = dict([(str(k),v) for k,v in self.mappedRooms.iteritems()])
        self.dbConfig[self.restUrl] = self.mappingConfig
        self.dbConfig.write()

    def uploadItem(self,theUrl,theBody):
        """Helper function to Add / Fetch a single item from the Database
        """
        #It would be nice to add "reverse" Synchronisation here (i.e. reflect changes on main server).
        log = self.log        
        #restSession = self.restSession
        #restQry = restSession.request_get(theUrl)
        restQry = requests.get(theUrl)
        
        log.debug(restQry)
        jsonBody = restQry.json()
        log.debug(jsonBody)

        if jsonBody == []:
            #Item does not exist so we want to add it 
            restQry = requests.post(theUrl,data=json.dumps(theBody))
            log.debug("New Item to be added {0}".format(theBody))
            jsonBody = restQry.json()
            log.debug(jsonBody)
                    
        restItem = self.unpackJSON(jsonBody).next()
        log.debug(restItem)

        return restItem

    def unpackJSON(self,jsonBody):
        """Unpack Json Objects returned by the REST interface.
        This needs to be seperated out to allow the Sampson Verison on the code to work

        :var jsonBody: Json Encoded body
        :return: Genertor object for these elements
        """
        return models.clsFromJSON(jsonBody)

    def _syncItems(self,localTypes,remoteTypes,theUrl):
        """
        Helper Function to syncronise two sets of items between databases
        
        :var localTypes: Dictionary of <id>:<item> representing local DB 
        :var remoteTypes: Dictionay of <id>:<item> representing remote DB
        :var theUrl: Url to push to

        :return: Dictionary representing the mapping between the Local and Remote DB
        """
        log = self.log
        session = self.localSession()

        theDiff = DictDiff(remoteTypes,localTypes)
        
        #A place to hold our lookup table
        mergedItems = {}
  
        #Stuff that is unchanged is pretty easy to deal with
        unchanged = theDiff.unchanged()
        log.debug("Unchanged, {0}".format(unchanged))

        for item in unchanged:
            theItem = localTypes[item]
            mergedItems[theItem.id] = theItem.id

        #Then stuff were the ID's different
        changed = theDiff.changed()
        log.debug("Changed, {0}".format(changed))
        #sys.exit(0)
        for item in changed:
            localItem = localTypes[item]
            remoteItem = remoteTypes[item]
            mergedItems[localItem.id] = remoteItem.id

        #And Sync New room types to the Remote DB 
        added = theDiff.added()
        log.debug("Added, {0}".format(added))

        for item in added:
           thisItem = remoteTypes[item]
           origId = thisItem.id
           log.info("Item {0} Not on local Database".format(thisItem))
           #We need to remove the Id so that we do not overwrite anything in the DB 
           thisItem.id = None
           session.add(thisItem)
           session.flush()
           log.info("New Id {0}".format(thisItem))
           mergedItems[origId] = thisItem.id
        #sys.exit(0)
        session.commit()
        

        #And Sync new Room Types to the Remote DB 
        removedItems = theDiff.removed()
        log.debug("Removed {0}".format(removedItems))
        for item in removedItems:
            thisItem = localTypes[item]
            log.info("Item {0} Not in remote DB".format(thisItem))
            dictItem = thisItem.toDict()
            del(dictItem["id"])
            r = requests.post(theUrl,data=json.dumps(dictItem))
            newItem = r.json()
            log.info("New Item {0}".format(thisItem))
            mergedItems[thisItem.id] = newItem["id"]

        return mergedItems

    def syncRoomTypes(self):
        """Synchronise Room Types"""
        log = self.log
        session = self.localSession()
        log.debug("--> Synchronising Room Types")
        #First we need to map room Types
        #sys.exit(0)
        #Fetch the room types from the remote Database
        theUrl = "{0}roomtype/".format(self.restUrl)

        #Fetch All room Types the Remote Database knows about        
        remoteQry = requests.get(theUrl)       
        jsonBody = remoteQry.json()
        restItems = self.unpackJSON(jsonBody)#models.clsFromJSON(jsonBody)
        remoteTypes = dict([(x.name,x) for x in restItems])

        #Fetch Local Version of room types
        localQry = session.query(self.RoomType)
        localTypes = dict([(x.name,x) for x in localQry])

        log.debug(localTypes)
        log.debug(remoteTypes)

        mappedRoomTypes = self._syncItems(localTypes,remoteTypes,theUrl)
        self.mappedRoomTypes = mappedRoomTypes
        
    
    def syncRooms(self):
        """Function to map Rooms and Room types between the two databases.
        This is a bi-directional sync method, room types should also be global (although ID's may vary)
        """
        log = self.log
        session = self.localSession()
        log.info("--> Synching Rooms")
        mappedRoomTypes = self.mappedRoomTypes

        #Now we have room types, we can map the rooms themselves.        
        #Fetch Remote Room Types
        theUrl = "{0}room/".format(self.restUrl)
        
        remoteQry = requests.get(theUrl)
        jsonBody = remoteQry.json()
        restItems = self.unpackJSON(jsonBody)
        remoteTypes = dict([(x.name,x) for x in restItems])

        localQry = session.query(self.Room)
        #Dictionary of local Types
        localTypes = dict([(x.name,x) for x in localQry])

        tmpTypes = {}
        for item in localQry:
            #Convert the local types to hold mapped room type Ids
            mappedId = mappedRoomTypes.get(item.roomTypeId,None)
            #mappedId = mappedRoomTypes.get(item.roomTypeId,None)
            tmpRoom = self.Room(id = item.id,
                                name = item.name,
                                roomTypeId = mappedId
                                )
            tmpTypes[item.name] = tmpRoom

        mappedRooms = self._syncItems(tmpTypes,remoteTypes,theUrl)
        self.mappedRooms = mappedRooms

    def syncSensorTypes(self):
        """Function to synchronise Sensor types between the two databases.
        This is a bi-directional sync method as Sensor Types should EXACTLY match in ALL databases.
        """
        
        #First we need to map room Types
        log = self.log
        log.debug("Mapping Sensors between databases")
        session = self.localSession()
        #restSession = self.restSession

        #Fetch the sensor types from the remote Database
        theUrl = "{0}{1}".format(self.restUrl,"sensortype/")
        
        #print theUrl
        #sys.exit(0)
        
        remoteTypes = {}
        localTypes = {}

        #sys.exit(0)
        #remoteQry = restSession.request_get(theUrl)
        remoteQry = requests.get(theUrl)
        #print remoteQry
        jsonBody=remoteQry.json()
        
        #jsonBody = json.loads(remoteQry['body'])
        restItems = self.unpackJSON(jsonBody)

        #log.debug("---- SENSOR TYPES FROM REMOTE SERVER ---")
        for item in restItems:
            #log.debug("--> {0}".format(item))
            remoteTypes[item.id] = item
        #sys.exit(0)
        itemTypes = session.query(self.SensorType)
        #log.debug("---- SENSOR TYPES FROM LOCAL SERVER ----")
        for item in itemTypes:
            #log.debug(item)
            localTypes[item.id] = item

        theDiff = DictDiff(remoteTypes,localTypes)

        #So we get "new" Items, those in the remote Database that are not in the local
        newItems = theDiff.added()
        #"Removed" items (Those that are in the Remote but not in the local)
        removedItems = theDiff.removed()
        #"Changed" items,  Items that are not the same
        changedItems = theDiff.changed()

        log.debug( "--> NEW")
        log.debug( newItems)
        log.debug( "--> Removed")
        log.debug( removedItems)
        log.debug( "--> Changed")
        log.debug( changedItems)
        #return
        #sys.exit(0)

        if changedItems:
            log.warning("Sensor Types with mathching Id's but different Names")
            log.warning(changedItems)
            raise(MappingError(changedItems,"Diffrent Sensor Types with Same ID"))

        #Deal with items that are not on the local database
        for item in newItems:
            theItem = remoteTypes[item]
            log.info("--> Sensor {0} Not in Local Database: {1}".format(item,theItem))
            #Turn into a SensorType
            session.add(theItem)
            localTypes[item] = theItem
           
        session.flush()
        session.commit()

        #Then Push any new sensors to the Remote Database
        for item in removedItems:
            theItem = localTypes[item]
            log.info("--> Sensor {0} Not in Remote Database: {1}".format(item,theItem))
            theUrl = "{0}sensortype/".format(self.restUrl)
            #print theUrl
            dictItem = theItem.toDict()
            #We then Post the New Item to the Remote DBString
            r= requests.post(theUrl,data=json.dumps(dictItem))
            log.debug(r)
            #print dictItem

        log.debug("Updating Mapping Dictionary")
        #Update the Mapping Dictionary
        newTypes = {}
        for key,value in localTypes.iteritems():
            newTypes[key] = value.id
            
            
        #self.mappedSensorTypes = localType
        self.mappedSensorTypes = newTypes
        return True

    def syncDeployments(self):
        """Synchronise Deployments between the local and remote Databaess"""
        log = self.log
        log.debug("----- Mapping Deployments ------")
        mappedDeployments = self.mappedDeployments
        session = self.localSession()

        #Fetch the room types from the remote Database
        theUrl = "{0}deployment/".format(self.restUrl)
        # #Fetch All Deployments the Remote Database knows about        
        remoteQry = requests.get(theUrl)       
        jsonBody = remoteQry.json()
        restItems = self.unpackJSON(jsonBody)#models.clsFromJSON(jsonBody)
        remoteTypes = dict([(x.name,x) for x in restItems])

        #Fetch Local Version of room types
        localQry = session.query(self.Deployment)
        localTypes = dict([(x.name,x) for x in localQry])

        #sys.exit(0)

        mappedDeployments = self._syncItems(localTypes,remoteTypes,theUrl)
        self.mappedDeployments = mappedDeployments

    # def mapDeployments(self, localIds = None):
    #     """
    #     Map deployments in the local database to those in the remote database

    #     .. warning::

    #         We assume that deployments all have a unique name.

    #     :var localIds:  List of Id's for local database objects
    #     :return: A List of delployment ID's that have been updated
    #     """
    #     return
    #     log = self.log
    #     log.debug("----- Mapping Deployments ------")
    #     mappedDeployments = self.mappedDeployments

    #     lSess = self.localSession()
    #     #restSession = self.restSession

    #     #Fetch deployments we know about from config file
    #     log.debug("Loading Known mappings from config file")
    #     #mappingConfig = self.mappingConfig
    #     #configDeployments = mappingConfig.get("deployment",{})
    #     #mappedDeployments.update(dict([(int(k),v) for k,v in configDeployments.iteritems()]))

    #     depQuery = lSess.query(self.Deployment)
        
    #     #TODO:  Load / Save mappings. Work if there are changes to deployment name on remote server
    #     #log.setLevel(logging.DEBUG)
    #     for item in depQuery:
    #         log.debug("Checking Mapping for Deployment {0}".format(item))
    #         if item.id in mappedDeployments:
    #             log.debug("--> Deployment {0} Exists in config file".format(item))
    #             continue
    #         #Look for this deployment on the remote server
    #         params = {"name":item.name}
    #         theUrl = "{0}deployment/?{1}".format(self.restUrl,urllib.urlencode(params))            
    #         log.debug(theUrl)
    #         theBody = item.toDict()
    #         del theBody["id"]

    #         newItem = self.uploadItem(theUrl,theBody)            
    #         log.debug("--> Deployment {0} Mapped to {1} ({2}:{3})".format(item,newItem,item.id,newItem.id))
    #         #deploymentMap[item.id] = newItem
    #         mappedDeployments[item.id] = newItem.id
            
    #     log.debug("Mapped Deps: {0}".format(mappedDeployments))

    #     #And Save this in out Local Version
    #     #self.mappedDeployments = deploymentMap

    def mapHouses(self):
        """Map houses on the Local Database to those on the Remote Database"""
        log = self.log
        log.debug("----- Mapping Houses ------")
        mappedDeployments = self.mappedDeployments
        mappedHouses = self.mappedHouses
        lSess = self.localSession()

        #log.debug("Loading Known Houses from config file")
        mappingConfig = self.mappingConfig
        #configHouses = mappingConfig.get("house",{})
        #mappedHouses.update(dict([(int(k),v) for k,v in configHouses.iteritems()]))

        #Get the list of deployments that may need updating
        #Deployment = models.Deployment
        theQry = lSess.query(self.House)

        for item in theQry:
            log.debug("Check Mapping for {0}".format(item))

            #Calculate the Deployment Id:
            mapDep = mappedDeployments.get(item.deploymentId,None)
            log.debug("-->Maps to deployment {0}".format(mapDep))

            params = {"address":item.address,
                      "deploymentId":mapDep}
            theUrl = "{0}house/?{1}".format(self.restUrl,urllib.urlencode(params))                            

            # #Look for the item
            theBody = item.toDict()
            theBody["deploymentId"] = mapDep
            del theBody["id"]
            newItem = self.uploadItem(theUrl,theBody)
            log.debug("House {0} maps to {1} ({2}:{3})".format(item,newItem,item.id,newItem.id))
            mappedHouses[item.id] = newItem.id
            
        log.debug("Map House: {0}".format(mappedHouses))
        #And Save this in out Local Version
        self.mappedHouses = mappedHouses

    def mapLocations(self):
        #Synchronise Locations
        log = self.log
        log.debug("----- Syncing Locations ------")
        lSess = self.localSession()
        
        #Get the list of deployments that may need updating
        #Deployment = models.Deployment
        mappedHouses = self.mappedHouses
        mappedRooms = self.mappedRooms
        mappedLocations = self.mappedLocations

        mappingConfig = self.mappingConfig
        configLoc = mappingConfig.get("location",{})
        mappedLocations.update(dict([(int(k),v) for k,v in configLoc.iteritems()]))
        #theMap = {}

        theQry = lSess.query(self.Location)

        #print mappedHouses
        #print mappedRooms
        for item in theQry:
            #Convert to take account of mapped houses and Rooms
            #print item
            hId = mappedHouses[item.houseId]
            rId =mappedRooms.get(item.roomId,None)
            log.debug("Mapping for item {0} : House {1} Room {2}".format(item,hId,rId))

        #     #We need to make sure the deployment is mapped correctly
            params = {"houseId":hId,
                      "roomId":rId}
            theUrl = "{0}location/?{1}".format(self.restUrl,urllib.urlencode(params))                            
        #     #Look for the item
            theBody = item.toDict()
            theBody["houseId"] = hId
            theBody["roomId"] = rId
            del(theBody["id"])
            log.debug("LOCATION {0}={1}".format(item,theBody))

            newItem = self.uploadItem(theUrl,theBody)
            mappedLocations[item.id] = newItem.id

        log.debug(mappedLocations)
        self.mappedLocations = mappedLocations

    def syncNodes(self):
        """Synchronise Nodes between databases.
        
        #Currently the node 'Location' field is not updated,  we need to work out how to do this
        while avoiding overwriting a node with an out of date location.

        TODO:  A Couple of potential issues here,  
            *) no Sych of Location,
            *) No Sync of Sensor Types (calibration),
            *) No Sync of Node Types
        """

        log = self.log

        log.debug("----- Syncing Nodes ------")
        session = self.localSession()

        #Get Local Nodes
        theQry = session.query(self.Node)
        #Then we want to map and compare our node dictionarys
        localNodes = dict([(x.id,x) for x in theQry])

        #Remote Nodes
        theUrl = "{0}node/".format(self.restUrl)
        theRequest = requests.get(theUrl)
        rNodes = self.unpackJSON(theRequest.json())
        #FOO
        remoteNodes = dict([(x.id,x) for x in rNodes])


        theDiff = DictDiff(remoteNodes,localNodes)
        
        #Items not in the Local Database
        log.debug("Dealing with new items in Local DB:")
        newItems = theDiff.added()
        log.debug(newItems)

        #log.debug(newItems)
        for item in newItems:
            thisItem = remoteNodes[item]
            log.info("Node {0}:{1} Not in Local Database".format(item,thisItem))
            thisItem.nodeTypeId = None #Set node type to none
            thisItem.locationId = None
            session.add(thisItem)
            session.flush()
        
        session.commit()
        removedItems = theDiff.removed()
        log.debug(removedItems)
        
        
        log.debug("Dealing with new items in Remote DB:")
        for item in removedItems:
            thisItem = localNodes[item]
            theUrl = "{0}node/".format(self.restUrl)
            log.info("Node {0} Not in Remote Db, Uploading".format(item))
            dictItem= thisItem.toDict()
            r = requests.post(theUrl,data=json.dumps(dictItem))
            log.debug(r)

    def uploadNodeStates(self):
        """
        Upload Nodestates between two databases
        """

        log = self.log
        log.info("---- Upload Node States ----")

        session = self.localSession()

        #Get the last state upload 
        mappingConfig = self.mappingConfig

        uploadDate = mappingConfig.get("lastStateUpdate",None)
        lastUpdate = None


        if uploadDate:
            log.debug("Last State upload from Config {0}".format(uploadDate))            
            if uploadDate and uploadDate != "None":
                lastUpdate = dateutil.parser.parse(uploadDate)
        else:
            lastUpdate = self.firstUpload  #Hack to match last nodestate with the first Reading we transfer

        log.info("Last Update from Config {0}".format(lastUpdate))
        
        #Otherwise we want to fetch the last synchronisation
        #Which is a little bit difficult as we dont have a house or anything to base this on So we will have to rely on this being correct
        
        #Count total number of Nodestates to upload
        theStates = session.query(models.NodeState)
        if lastUpdate:
            log.debug("-- Filter on {0}".format(lastUpdate))
            theStates = theStates.filter(models.NodeState.time>lastUpdate)

        origCount = theStates.count()
        log.info("--> Total of {0} Nodestates to transfer".format(origCount))
        rdgCount = origCount
        transferCount = 0

        while rdgCount > 0:
            theState = session.query(models.NodeState)
            if lastUpdate:
                theState = theStates.filter(models.NodeState.time>lastUpdate)
            theState = theState.order_by(models.NodeState.time)
            theState = theState.limit(self.pushLimit)
            rdgCount = theState.count()
            if rdgCount <= 0:
                log.info("--> No States Remain")
                return True
            
            transferCount += rdgCount
            log.debug("--> Transfer {0}/{1} States to remote DB".format(transferCount,origCount))


            #Convert to REST
            jsonList = [x.toDict() for x in theState]
            lastSample = theState[-1].time
            log.debug("Last State in List {0}".format(lastSample))

            #Zip him up
            jsonStr = json.dumps(jsonList)
            gzStr = zlib.compress(jsonStr)

            #And Upload
            theUrl = "{0}bulk/".format(self.restUrl)
            restQry = requests.post(theUrl,data=gzStr)

            log.debug("REST QUERY RETURN CODE {0}".format(restQry.status_code))
            if restQry.status_code== 500:
                log.warning("Upload of States Fails")
                log.warning(restQry)
                raise Exception ("Upload Failed")
            
            #update the stample times
            lastUpdate = lastSample
            mappingConfig["lastStateUpdate"] = lastUpdate
            self.saveMappings()

        return rdgCount > 0
            
        
    def uploadReadings(self,theHouse):
        """
        Syncronise Readings between two databases,
        modified to upload by House
        """
        log = self.log
        log.info("--- Upload Readings for house {0} ----".format(theHouse))

        #Load the Mapped items to the local namespace
        mappedLocations = self.mappedLocations
        mappedTypes = self.mappedSensorTypes
        #print mappedTypes
        #Mapping Config
        mappingConfig = self.mappingConfig
        
        #Fetch the last Date from the mapping config
        uploadDates = mappingConfig.get("lastupdate",None)
        lastUpdate = None
        if uploadDates:
            print uploadDates
            lastUpdate = uploadDates.get(str(theHouse.id),None)
            if lastUpdate and lastUpdate != 'None':
                lastUpdate = dateutil.parser.parse(lastUpdate)
            else:
                lastUpdate = None
        log.info("Last Update from Config is {0} {1}".format(lastUpdate,type(lastUpdate)))

        #TODO:
        # This is a temporary fix for the problem for nodestates,  Currently I cannot think of a sensible way 
        # To do this without generting a lot of network traffic.  
        self.firstUpload = lastUpdate

        #Get the last reading for this House
        session = self.localSession()
        #restSession =self.restSession

        #As we should be able to trust the last update field of the config file.
        #Only request the last sample from the remote DB if this does not exist.

        if lastUpdate is None:
            log.info("--> Requesting date of last reading in Remote DB")
            params = {"house":theHouse.address,
                      "lastUpdate":lastUpdate}
            theUrl = "{0}lastSync/".format(self.restUrl)
            #restQuery = restSession.request_get(theUrl,args=params)
            restQuery = requests.get(theUrl,params=params)
            strDate =  restQuery.json()

            log.debug("Str Date {0}".format(strDate))
            if strDate is None:
                log.info("--> --> No Readings in Remote DB")
                lastDate = None
            else:
                lastDate = dateutil.parser.parse(strDate)
                log.info("--> Last Upload Date {0}".format(lastDate))

            lastUpdate = lastDate

        #Then Save 
        uploadDates[str(theHouse.id)] = lastUpdate
        mappingConfig["lastupdate"] = uploadDates
        self.saveMappings()


        #Get locations associated with this House
        theLocations = [x.id for x in theHouse.locations]

        #Count the Number of Readings we need to transfer
        theReadings = session.query(models.Reading).filter(models.Reading.locationId.in_(theLocations))
        if lastUpdate:
            theReadings = theReadings.filter(models.Reading.time > lastUpdate)

        origCount = theReadings.count()
        log.info("--> Total of {0} samples to transfer".format(origCount))
        rdgCount = origCount
        transferCount = 0
                          
        for x in range(2):
        #while rdgCount > 0:
        #while True:
            #Add some timings
            stTime = time.time()
            theReadings = session.query(models.Reading).filter(models.Reading.locationId.in_(theLocations))
            if lastUpdate:
                theReadings = theReadings.filter(models.Reading.time > lastUpdate)
            theReadings = theReadings.order_by(models.Reading.time)
            theReadings = theReadings.limit(self.pushLimit)
            #theReadings = theReadings.limit(10000)
            rdgCount = theReadings.count()
            if rdgCount <= 0:
                log.info("--> No Readings Remain")
                return True
            
            transferCount += rdgCount

            log.debug("--> Transfer {0}/{1} Readings to remote DB".format(transferCount,origCount))

            jsonList = [] #Blank Object to hold readings

            for reading in theReadings:
                #log.debug(reading)

                #Convert our Readings to REST, and remap to the new locations
                dictReading = reading.toDict()
                #log.debug("==> {0}".format(dictReading))
                dictReading['locationId'] = mappedLocations[reading.locationId]
                dictReading['typeId'] = mappedTypes[reading.typeId]
                #log.debug("--> {0}".format(dictReading))            
                
                jsonList.append(dictReading)
                lastSample = reading.time
            
            jsonStr = json.dumps(jsonList)
            gzStr = zlib.compress(jsonStr)
            #log.debug("Size of Compressed JSON {0}kB".format(sys.getsizeof(gzStr)/1024))

            qryTime = time.time()
             #And then try to bulk upload them
            theUrl = "{0}bulk/".format(self.restUrl)
            #restQry = restSession.request_post("/bulk/",
            #                                   body=json.dumps(jsonList))
            #log.debug(restQry)
            restQry = requests.post(theUrl,data=gzStr)
            #print restQry
            #print restQry.status_code

            transTime = time.time()
            if restQry.status_code == 500:
                log.warning("Upload Fails")
                log.warning(restQry)
                raise Exception ("Upload Fails")            
            

            log.info("--> Transferred {0}/{1} Readings to remote DB".format(transferCount,origCount))
            log.info("--> Timings: Local query {0}, Data Transfer {1}, Total {2}".format(qryTime - stTime, transTime -qryTime, transTime - stTime))
            lastUpdate = lastSample
            
            #And save the last date in the config file
            uploadDates[str(theHouse.id)] = lastUpdate
            mappingConfig["lastupdate"] = uploadDates
            self.saveMappings()

        #Return True if we need to upload more
        return rdgCount > 0
            

  

if __name__ == "__main__":
    import datetime
    import pickle
    logging.debug("Testing Push Classes")

    server = PushServer()
    server.sync()
