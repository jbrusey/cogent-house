"""
Script to push data to a remote server using REST

.. codeauthor:: Daniel Goldsmith <djgoldsmith@googlemail.com>

For Changes see CHANGES.txt

.. version:: 0.3.5
"""

__version__ = "0.3.5"

#Setup Logging
import logging
import logging.handlers

import os
import datetime
import re

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(name)-10s %(levelname)-8s %(message)s",
                    datefmt = "%m-%d-%Y %H:%M",
                    )

#Add a File hander (Max of 5 * 5MB Logfiles)
LOGSIZE = (1024*1024) * 5 #5Mb Logs
FH = logging.handlers.RotatingFileHandler("push.log",
                                          maxBytes=LOGSIZE,
                                          backupCount = 5)
FH.setLevel(logging.INFO)

#Formatter
FMT = logging.Formatter("%(asctime)s %(name)-10s %(levelname)-8s %(message)s")
FH.setFormatter(FMT)

__version__ = "0.3.4"


#Library Imports
import sqlalchemy
import dateutil.parser
import json
import urllib
import requests
import configobj 
import time
#Local Imports
import cogent.base.model as models

from cogent.push.dictdiff import DictDiff

#Disable Requests Logging
REQUESTS_LOG = logging.getLogger("requests")
REQUESTS_LOG.setLevel(logging.WARNING)

INIT_COMMENT = ["this file holds details of mappings",
                "it is strongly recommended that you do not edit!!",
                "I take no responsibility for bad things(tm) hapening",
                "if changes are made"
                ]

class MappingError(Exception):
    """Exception raised for errors when Mapping Items.

    Attributes:
        msg  -- explanation of the error
    """

    def __init__(self, expr, msg):
        Exception.__init__(self)
        self.expr = expr
        self.msg = msg

    def __str__(self):
        return "\n{0}\n{1}".format(self.msg, self.expr)

class PushServer(object):
    """
    Class to deal with pushing updates to a group of remote databases

    This class is designed to be run as a daemon, managing a group of individual
    pusher objects, and facilitating the transfer of data between remote and
    local DB's
    """

    def __init__(self, localURL=None, configfile="synchronise.conf"):
        """Initialise the push server object

        This should:

        #. Create a connection to the local database,
        #. Read the Configuration files.
        #.Setup Necessary Pusher objects for each database that needs
          synchronising.

        :var localURL:  The DBString used to connect to the local database.
                        This can be used to overwrite the url in the config file
                        
        :configfile:  Name of configfile to use
        """

        self.synclist = None
        self.localsession = None
        #Create Logging
        self.log = logging.getLogger("Push Server")
        log = self.log
        log.addHandler(FH)
        log.info("="*70)
        log.info("Initialising Push Server")

        #Load and Read the Configuration files
        configparser = configobj.ConfigObj(configfile)
        self.configparser = configparser

        #Process General Configuration Options and
        #Initialise Local Database connection.
        log.debug("Processing Global Configuration options")
        generaloptions = configparser["general"]

        #Local Database Connection
        if not localURL:
            localURL = generaloptions["localurl"]

        log.info("connecting to local database at {0}".format(localURL))

        #initialise the local database connection
        self.create_engine(localURL)

        #we also need to know the "limit" on items to push
        pushlimit = generaloptions["pushlimit"]
        log.debug("push limit is {0}".format(pushlimit))

        #open / build a config object to store mappings for this location
        mappingname = "{0}_map.conf".format(localURL.split("@")[-1])
        mappingname = mappingname.replace("/","-")

        log.debug("open config object for {0}".format(mappingname))
        mappingconfig = configobj.ConfigObj(mappingname)

        #append a warning to the start of the config file
        mappingconfig.initial_comment = INIT_COMMENT

        #next we want to queue up all the remote urls we wish to push to.
        self.queuelocations(configparser, mappingconfig, pushlimit)
        log.debug("List of Locations to Sync:")
        for item in self.synclist:
            log.debug("--> {0}".format(item))
        #self.synclist = [] #List of locations to sync
        #self.localsession = None #pointer to local session

    def queuelocations(self, configparser, mappingconfig, pushlimit):
        """
        Function to enque a set of locations that the push server is to push to

        :param configparser: Config parser object we are reading from
        :param mappingConfig: Config parser object we are writing to
        :param pushLimit: Maximum number of samples to transmit in one go.
        """

        #Create a session
        localsession = self.localsession
        log = self.log
        synclist = []

        #Read Locations in the config File
        locations = configparser["locations"]

        #For Each location we are looking at
        for item in locations:
            #Check if we need to synchronise to this location.
            needsync = locations.as_bool(item)
            log.debug("Location {0} Needs Sync >{1}".format(item, needsync))

            if needsync: #Enqueue
                thisloc = configparser[item]
                log.info("Adding {0} to synchronise Queue".format(thisloc))
                thepusher = Pusher(localsession, #Session
                                   thisloc["resturl"], #Url to Push to
                                   mappingconfig, #Mapping Configuration file
                                   pushlimit,  #Limit on number of samples
                                   )
                synclist.append(thepusher)

        self.synclist = synclist

    def create_engine(self, localURL):
        """Create a connection to the DB engine"""
        log = self.log
        engine = sqlalchemy.create_engine(localURL)
        models.initialise_sql(engine)
        #models.init_model(engine)
        localsession = sqlalchemy.orm.sessionmaker(bind=engine)
        self.localsession = localsession
        log.info("Database Connection to {0} OK".format(localURL))


    def sync(self):
        """
        Run one instance of the synchroniseation mechnism.

        For each item in the config file, perform synchronisation.
        :return: True on success,  False otherwise
        """

        log = self.log
        loopstart = time.time()
        avgtime = None
        log.info("Running Full Syncronise Cycle")
        for item in self.synclist:
            log.info("Synchronising {0}".format(item))
            item.checkRPC()
            #TODO Uncomment this after testing
            item.sync()
            

        loopend = time.time()
        log.info("Total Time Taken {0} Avg {1}".format(loopend-loopstart,
                                                       avgtime))

class Pusher(object):
    """Class to push updates to a remote database.

    This class contains the code to deal with the nuts and bolts of syncronising
    remote and local databases

    """

    def __init__(self, localSession, restUrl, dbConfig, pushLimit=5000):
        """Initalise a pusher object

        :param localSession: A SQLA session, connected to the local database
        :param restUrl: URL of rest interface to upload to
        :param dbConfig: Config Parser that holds details of mappings for the DB
        :param pushLimit: Number of samples to transfer in each "Push"
        """

        self.log = logging.getLogger("Pusher")
        self.log.setLevel(logging.DEBUG)
        #self.log.setLevel(logging.INFO)
        #self.log.setLevel(logging.WARNING)
        log = self.log
        log.addHandler(FH)

        log.debug("Initialising Push Object")
        #Save the Parameters
        self.localsession = localSession
        self.pushLimit = pushLimit

        log.debug("Starting REST connection for {0}".format(restUrl))
        self.restUrl = restUrl
        #self.restSession = restful_lib.Connection(restUrl)
        self.dbConfig = dbConfig

        #And get the individual mappings for this particaular Remote URLS
        mappingConfig = dbConfig.get(restUrl, None)
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
        self.backmappedLocations = {}
        self.mappedRoomTypes = {}

        #Evidently we need to map Sensor Types too
        self.mappedSensorTypes = {}

        dbConfig[restUrl] = mappingConfig
        dbConfig.write()

        #And a horribly hacky way to load Classes into memory so inhritance is
        #simple
        self.SensorType = models.SensorType
        self.RoomType = models.RoomType
        self.Room = models.Room
        self.Deployment = models.Deployment
        self.House = models.House
        self.Node = models.Node
        self.Location = models.Location

    # NOTE: this code removed as it is not used
    # def checkConnection(self):
    #     #Do we have a connection to the server
    #     log = self.log

    def checkConnection(self):
        #Do we have a connection to the server
        log = self.log

        #Fetch the room types from the remote Database                                                                                                      
        theUrl = "{0}deployment/".format(self.restUrl)
        # #Fetch All Deployments the Remote Database knows about                                                                                            
        restQry = requests.get(theUrl)
        if restQry.status_code == 503:
            log.warning("No Connection to server available")
            return False
        log.debug("Connection to rest server OK")
        return True

    def checkRPC(self):
        """Check for a set of remote procedure calls"""
        log = self.log
        log.info("Checking for RPC")

        theUrl = "{0}rpc/".format(self.restUrl)

        #Work out my hostname
        hostname = os.uname()[1]
        log.debug("Hostname {0}".format(hostname))
        #hostname = "salford21"
        try:
            #Quick and simple for the moment
            #theport = int(hostname[-2:])
            theport = int(re.findall("\d+",hostname)[0])
            log.debug("Port to use is {0}".format(theport))
        except ValueError:
            log.warning("Unable to get port from hostname {0}".format(hostname))
            theport = 0

        #sys.exit(0)

        #Fetch All room Types the Remote Database knows about        
        log.debug("Fetching data from {0}".format(theUrl))
        try:
            remoteqry = requests.get(theUrl,timeout=60)    
        except requests.exceptions.Timeout:
            log.warning("Timeout on connection to cogentee")
            sys.exit(-1)
            
        jsonbody = remoteqry.json()
        log.debug(jsonbody)
        
        log.debug("Processing RPC")
        #Go through the JSON and see if we have any RPC
        for item in jsonbody:
            log.debug(item)
            host, command = item
            if host.lower() == hostname.lower():
                log.info("RPC COMMAND {0}".format(command))
                if command == "tunnel":
                    log.debug("Attempting to start SSH Process on port {0}".format(theport))
                    #subprocess.check_output(["./ch-ssh start {0}".format(theport)], shell=True)
                    proc = subprocess.Popen(["/opt/cogent-house.clustered/cogent/push/ch-ssh", "start" ,"{0}".format(theport)],
                                            stderr=subprocess.PIPE)
                    
                    # for line in iter(proc.stdout.readline, ''):
                        
                    #     log.debug("--> {0}".format(line.strip()))

                    for line in iter(proc.stderr.readline, ''):
                        log.debug("E-> {0}".format(line.strip()))

                    print proc.returncode
                    log.debug("Killing existing SSH Process")
                    #Wait for Exit then Kill
                    subprocess.check_output(["./ch-ssh stop"],shell=True)
        

    def sync_simpletypes(self):
        """Synchronse any simple (ie ones that have no foreign keys) tables"""
        self.sync_sensortypes()
        self.sync_roomtypes()
        self.sync_rooms()
        self.sync_deployments()


    def sync(self):
        """
        Perform one synchronisation step for this Pusher object

        :return: True if the sync is successfull, False otherwise
        """

        log = self.log

        self.load_mappings()

        log.debug("Performing sync")
        #Load our Stored Mappings

        #Things that should be relitively static
        self.sync_simpletypes()

        self.sync_houses() #Then houses
        self.sync_locations()

        self.save_mappings()

        #Moved here for the Sampson Version
        self.sync_nodes()


        session = self.localsession()
        houses = session.query(self.House)
        mappingconfig = self.mappingConfig

        #sys.exit(0)
        for item in houses:
            log.info("Synchronising Readings for House {0}".format(item))
            #Look for the Last update
            self.upload_readings(item)

        #Then upload the node Sttes
        #self.upload_nodestate()
        self.save_mappings()

    def load_mappings(self):
        """Load known mappings from the config file"""
        log = self.log
        log.info("--- Loading Mappings ---")
        mappingConfig = self.mappingConfig

        log.debug("Loading Deployments")
        deployments = mappingConfig["deployment"]        
        self.mappedDeployments = dict([(int(k),int(v))
                                       for k,v in 
                                       deployments.iteritems()])
                                       
        log.debug("Loading Houses")
        houses = mappingConfig["house"]        
        self.mappedHouses = dict([(int(k),int(v))
                                       for k,v in 
                                       houses.iteritems()])
                                       
        log.debug("Loading Locations")
        locations = mappingConfig["location"]        
        self.mappedLocations = dict([(int(k),int(v))
                                       for k,v in 
                                       locations.iteritems()])
        log.debug("Loading Rooms")
        rooms = mappingConfig["room"]        
        self.mappedRooms = dict([(int(k),int(v))
                                       for k,v in 
                                       rooms.iteritems()])
        #return

        #self.mapDeployments()
        log.info("---- Save Mappings ----")
        #self.save_mappings()


    def save_mappings(self):
        """Save mappings to a file"""
        mappingConfig = self.mappingConfig

        mappingConfig["deployment"] = dict([(str(k),v)
                                            for k,v in
                                            self.mappedDeployments.iteritems()])

        mappingConfig["house"] = dict([(str(k),v)
                                       for k,v in
                                       self.mappedHouses.iteritems()])

        mappingConfig["location"] = dict([(str(k),v)
                                          for k,v in
                                          self.mappedLocations.iteritems()])

        mappingConfig["room"] = dict([(str(k),v)
                                      for k,v in
                                      self.mappedRooms.iteritems()])

        self.dbConfig[self.restUrl] = self.mappingConfig
        self.dbConfig.write()

    def uploadItem(self, theUrl, theBody):
        """Helper function to Add / Fetch a single item from the Database

        .. todo::

            #It would be nice to add "reverse" Synchronisation here
            #(i.e. reflect changes on main server).
        """

        log = self.log
        #restSession = self.restSession
        #restQry = restSession.request_get(theUrl)
        restQry = requests.get(theUrl)

        log.debug(restQry)
        jsonBody = restQry.json()
        log.debug(jsonBody)

        if jsonBody == []:
            #Item does not exist so we want to add it
            restQry = requests.post(theUrl, data=json.dumps(theBody))
            log.debug("New Item to be added {0}".format(theBody))
            jsonBody = restQry.json()
            log.debug(jsonBody)

        restItem = self.unpackJSON(jsonBody).next()
        log.debug(restItem)

        return restItem

    def unpackJSON(self, jsonBody):
        """Unpack Json Objects returned by the REST interface.
        This needs to be seperated out to allow the Sampson Version on the code
        to work as that version of the code has different tables,
        thus we need to map them in a different way.

        :var jsonBody: Json Encoded body
        :return: Genertor object for these elements
        """
        return models.clsFromJSON(jsonBody)

    def _syncItems(self, localTypes, remoteTypes, theUrl):
        """
        Helper Function to syncronise two sets of items between databases

        .. NOTE::

           The accuracy of this function depends on the output of the models.__eq__ function

        #This function has three things that could happen.

        1) Items are Equal therefore no synchonisation takes place
        2) A Local Item doesn't exist on the remote DB Thus a new item is created and mapped
        3) A Local Item is created and mapped

        :var localTypes: Dictionary of <id>:<item> representing local DB
        :var remoteTypes: Dictionay of <id>:<item> representing remote DB
        :var theUrl: Url to push to

        :return: Dictionary representing the mapping between the
                 Local and Remote DB
        """
        log = self.log
        session = self.localsession()

        theDiff = DictDiff(remoteTypes, localTypes)

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
            #We need to remove the Id so that we do not overwrite anything in
            #the DB
            thisItem.id = None
            session.add(thisItem)
            session.flush()
            log.info("New Id {0}".format(thisItem))
            mergedItems[origId] = thisItem.id

        session.commit()
        session.close()

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

    def sync_roomtypes(self):
        """Synchronise Room Types

        Room types should be global to all databases, as it is likely that
        a given room type may be needed in several deployments.  

        Thus this method does a two way sync between the local and remote database
        While room types will be the same between databases.  The ID's may differ 
        betweeen instances.  Therefore this function also maps the local roomtypeId
        to the remote roomtypeId

        :return: True if this was successfull
        """
        log = self.log
        session = self.localsession()
        log.debug("--> Synchronising Room Types")
        #First we need to map room Types

        #Fetch the room types from the remote Database
        theUrl = "{0}roomtype/".format(self.restUrl)

        #Fetch All room Types the Remote Database knows about
        remoteQry = requests.get(theUrl)
        jsonBody = remoteQry.json()
        restItems = self.unpackJSON(jsonBody)
        remoteTypes = dict([(x.name, x) for x in restItems])

        #Fetch Local Version of room types
        localQry = session.query(self.RoomType)
        localTypes = dict([(x.name, x) for x in localQry])
        session.close()
        log.debug(localTypes)
        log.debug(remoteTypes)


        mappedRoomTypes = self._syncItems(localTypes, remoteTypes, theUrl)
        self.mappedRoomTypes = mappedRoomTypes

        return True

    def sync_rooms(self):
        """Function to map Rooms and Room types between the two databases.

        This is a bi-directional sync method,
        room types should also be global (although ID's may vary).
        So there should be some garentee that the same room types will be
        abailable in every database.
        """
        log = self.log
        session = self.localsession()
        log.info("--> Synching Rooms")
        mappedRoomTypes = self.mappedRoomTypes

        #Now we have room types, we can map the rooms themselves.
        #Fetch Remote Room Types
        theUrl = "{0}room/".format(self.restUrl)

        remoteQry = requests.get(theUrl)
        jsonBody = remoteQry.json()
        restItems = self.unpackJSON(jsonBody)
        remoteTypes = dict([(x.name, x) for x in restItems])

        localQry = session.query(self.Room)
        #Dictionary of local Types
        localTypes = dict([(x.name, x) for x in localQry])

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

        mappedRooms = self._syncItems(tmpTypes, remoteTypes, theUrl)
        self.mappedRooms = mappedRooms

        return True

    def sync_nodetypes(self):
        """Function to synchronise Node types between the two databases.
        This is a bi-directional sync method.
        Node Types should EXACTLY match in ALL databases.

        :return: True on Success
        :raises: MappingError if node types do not match
        """

        #First we need to map room Types
        log = self.log
        log.debug("Mapping NodeTypes between databases")
        session = self.localsession()

        #Fetch the sensor types from the remote Database
        theUrl = "{0}{1}".format(self.restUrl, "nodetype/")

        remoteTypes = {}
        localTypes = {}

        remoteQry = requests.get(theUrl)
        jsonBody=remoteQry.json()
        restItems = self.unpackJSON(jsonBody)
        for item in restItems:
            remoteTypes[item.id] = item

        itemTypes = session.query(models.NodeType)
        for item in itemTypes:
            localTypes[item.id] = item

        theDiff = DictDiff(remoteTypes,localTypes)

        #those in the remote Database that are not in the local
        newItems = theDiff.added()
        #Those that are in the Remote but not in the local
        removedItems = theDiff.removed()
        #"Changed" items,  Items that are not the same
        changedItems = theDiff.changed()

        if changedItems:
            log.warning("Node Types with mathching Id's but different Names")
            # print "{0} Local {0}".format("-"*25)
            # for key,item in localTypes.iteritems():
            #     print "{0} {1}".format(key,item)
            # print "{0} Remote {0}".format("-"*25)
            # for key,item in remoteTypes.iteritems():
            #     print "{0} {1}".format(key,item)
            for item in changedItems:
                log.warning("--> {0}".format(item))
            #log.warning("Remote is {0}".format(remoteTypes[changedItems[0]]))
            #log.warning("local is {0}".format(localTypes[changedItems[1]]))
            raise(MappingError(changedItems,
                               "Diffrent Node Types with Same ID"))

        #Deal with items that are not on the local database
        for item in newItems:
            theItem = remoteTypes[item]
            log.info("--> Nodetype {0} Not in Local Database: {1}".format(item,
                                                                        theItem))
            #Turn into a NodeType
            session.add(theItem)
            localTypes[item] = theItem

        session.flush()
        session.commit()

        #Then Push any new nodes to the Remote Database
        for item in removedItems:
            theItem = localTypes[item]
            log.info("--> Nodetype {0} Not in Remote Database: {1}".format(item,
                                                                         theItem))
            theUrl = "{0}nodetype/".format(self.restUrl)
            #print theUrl
            dictItem = theItem.toDict()
            #We then Post the New Item to the Remote DBString
            r= requests.post(theUrl,data=json.dumps(dictItem))
            log.debug(r)

        log.debug("Updating Mapping Dictionary")
        #Update the Mapping Dictionary
        newTypes = {}
        for key, value in localTypes.iteritems():
            newTypes[key] = value.id

        self.mappedNodeTypes = newTypes
        return True


    def sync_sensortypes(self):
        """Function to synchronise Sensor types between the two databases.
        This is a bi-directional sync method.
        Sensor Types should EXACTLY match in ALL databases.

        :return: True on Success
        :raises: MappingError if sensor types do not match
        """

        #First we need to map room Types
        log = self.log
        log.debug("Mapping Sensors between databases")
        session = self.localsession()

        #Fetch the sensor types from the remote Database
        theUrl = "{0}{1}".format(self.restUrl, "sensortype/")

        remoteTypes = {}
        localTypes = {}

        remoteQry = requests.get(theUrl)
        jsonBody=remoteQry.json()
        restItems = self.unpackJSON(jsonBody)
        for item in restItems:
            remoteTypes[item.id] = item

        itemTypes = session.query(self.SensorType)
        for item in itemTypes:
            localTypes[item.id] = item

        theDiff = DictDiff(remoteTypes,localTypes)

        #those in the remote Database that are not in the local
        newItems = theDiff.added()
        #Those that are in the Remote but not in the local
        removedItems = theDiff.removed()
        #"Changed" items,  Items that are not the same
        changedItems = theDiff.changed()

        if changedItems:
            log.warning("Sensor Types with mathching Id's but different Names")
            for item in changedItems:
                log.warning("--> {0}".format(item))
            #log.warning("Remote is {0}".format(remoteTypes[changedItems[0]]))
            #log.warning("local is {0}".format(localTypes[changedItems[1]]))
            raise(MappingError(changedItems,
                               "Diffrent Sensor Types with Same ID"))

        #Deal with items that are not on the local database
        for item in newItems:
            theItem = remoteTypes[item]
            log.info("--> Sensor {0} Not in Local Database: {1}".format(item,
                                                                        theItem))
            #Turn into a SensorType
            session.add(theItem)
            localTypes[item] = theItem

        session.flush()
        session.commit()

        #Then Push any new sensors to the Remote Database
        for item in removedItems:
            theItem = localTypes[item]
            log.info("--> Sensor {0} Not in Remote Database: {1}".format(item,
                                                                         theItem))
            theUrl = "{0}sensortype/".format(self.restUrl)
            #print theUrl
            dictItem = theItem.toDict()
            #We then Post the New Item to the Remote DBString
            r= requests.post(theUrl,data=json.dumps(dictItem))
            log.debug(r)

        log.debug("Updating Mapping Dictionary")
        #Update the Mapping Dictionary
        newTypes = {}
        for key, value in localTypes.iteritems():
            newTypes[key] = value.id

        self.mappedSensorTypes = newTypes
        return True

    def sync_deployments(self):
        """Synchronise Deployments between the local and remote Databaess
        Another bi-directional sync that will pull the relevant deployments
        between database
        """
        log = self.log
        log.debug("----- Mapping Deployments ------")
        mappedDeployments = self.mappedDeployments
        session = self.localsession()

        #Fetch the room types from the remote Database
        theUrl = "{0}deployment/".format(self.restUrl)
        # #Fetch All Deployments the Remote Database knows about
        remoteQry = requests.get(theUrl)
        jsonBody = remoteQry.json()
        restItems = self.unpackJSON(jsonBody)
        #remoteTypes = dict([(x.name, x) for x in restItems])
        remoteTypes = dict([(x.name, x) for x in restItems])

        #Fetch Local Version of room types
        localQry = session.query(self.Deployment)
        localTypes = dict([(x.name, x) for x in localQry])

        # log.debug("------ REMOTE ------")
        # for key,item in remoteTypes.iteritems():
        #     log.debug("--> '{0}' {1}".format(key,item))
        
        # log.debug("------ LOCAL -------")
        # for key,item in localTypes.iteritems():
        #     log.debug("--> '{0}' {1}".format(key,item))

        mappedDeployments = self._syncItems(localTypes,remoteTypes,theUrl)
        log.debug("Mapped Deployments are {0}".format(mappedDeployments))

        self.mappedDeployments = mappedDeployments

    def sync_houses(self):
        """Map houses on the Local Database to those on the Remote Database

        Houses need mapping in a different way to the more simple items.  For a
        start they have foreign keys (which may rely on another mapping) Thus we
        get the house from the database, and make sure the location Id is mapped
        against the deployment mapped from the remote DB.

        """
        log = self.log
        log.debug("----- Mapping Houses ------")
        mappedDeployments = self.mappedDeployments
        mappedHouses = self.mappedHouses
        lSess = self.localsession()

        log.debug("----- CURRENTLY MAPPED HOUSES ARE -----")
        log.debug(mappedHouses)
        log.debug("---------------------------------------")
        
        #log.debug("Loading Known Houses from config file")
        mappingConfig = self.mappingConfig

        #Get the list of deployments that may need updating
        #Deployment = models.Deployment
        theQry = lSess.query(self.House)

        for item in theQry:
            log.debug("Check Mapping for {0}".format(item))
            if item.id in mappedHouses:
                log.debug("--> Mapping for house exists")
                continue
                #raw_input("--> Press a key to continue")
                


            #Calculate the Deployment Id:
            mapDep = mappedDeployments.get(item.deploymentId,None)
            log.debug("-->Maps to deployment {0}".format(mapDep))

            params = {"address":item.address,
                      "deploymentId":mapDep}
            theUrl = "{0}house/?{1}".format(self.restUrl,
                                            urllib.urlencode(params))
            # #Look for the item
            theBody = item.toDict()
            theBody["deploymentId"] = mapDep
            del theBody["id"]
            newItem = self.uploadItem(theUrl,theBody)
            log.debug("House {0} maps to {1} ({2}:{3})".format(item,
                                                               newItem,
                                                               item.id,
                                                               newItem.id))
            mappedHouses[item.id] = newItem.id

        log.debug("Map House: {0}".format(mappedHouses))
        #And Save this in out Local Version
        self.mappedHouses = mappedHouses
        lSess.flush()
        lSess.close()

    def sync_locations(self):
        #Synchronise Locations
        log = self.log
        log.debug("----- Syncing Locations ------")
        lSess = self.localsession()

        #Get the list of deployments that may need updating
        #Deployment = models.Deployment
        mappedHouses = self.mappedHouses
        mappedRooms = self.mappedRooms
        mappedLocations = self.mappedLocations
        backmappedLocations = self.backmappedLocations

        theQry = lSess.query(self.Location)

        for item in theQry:
            #Convert to take account of mapped houses and Rooms
            if item.id in mappedLocations:
                log.info("Location {0} has been mapped")
                continue

            hId = mappedHouses[item.houseId]
            rId =mappedRooms.get(item.roomId,None)
            log.debug("Mapping for item {0} : House {1} Room {2}".format(item,
                                                                         hId,
                                                                         rId))

            #We need to make sure the deployment is mapped correctly
            params = {"houseId":hId,
                      "roomId":rId}
            theUrl = "{0}location/?{1}".format(self.restUrl,
                                               urllib.urlencode(params))
            #Look for the item
            theBody = item.toDict()
            theBody["houseId"] = hId
            theBody["roomId"] = rId
            del(theBody["id"])
            log.debug("LOCATION {0}={1}".format(item,
                                                theBody))

            newItem = self.uploadItem(theUrl,
                                      theBody)
            mappedLocations[item.id] = newItem.id

        log.debug(mappedLocations)
        self.mappedLocations = mappedLocations

        #And sort out the backmapping
        for key, value in mappedLocations.iteritems():
            backmappedLocations[value] = key
        
        self.backmappedLocations = backmappedLocations

    def sync_nodes(self):
        """Synchronise Nodes between databases.

        .. TODO:

            Currently the node 'Location' field is not updated,
            we need to work out how to do this
            while avoiding overwriting a node with an out of date location.
            A Couple of potential issues here,
            *) no Sych of Location,
            *) No Sync of Sensor Types (calibration),
            *) No Sync of Node Types
        """

        log = self.log

        log.debug("----- Syncing Nodes ------")
        session = self.localsession()

        #Get Local Nodes
        theQry = session.query(self.Node)
        #Then we want to map and compare our node dictionarys
        localNodes = dict([(x.id, x) for x in theQry])

        #Remote Nodes
        theUrl = "{0}node/".format(self.restUrl)
        theRequest = requests.get(theUrl)
        rNodes = self.unpackJSON(theRequest.json())
        #FOO
        remoteNodes = dict([(x.id, x) for x in rNodes])

        theDiff = DictDiff(remoteNodes,localNodes)

        #Items not in the Local Database
        log.debug("Dealing with new items in Local DB:")
        newItems = theDiff.added()
        log.debug(newItems)

        for item in newItems:
            thisItem = remoteNodes[item]
            log.info("Node {0}:{1} Not in Local Database".format(item,
                                                                 thisItem))

            #We also need to map this location to that in the local database
            rloc = self.backmappedLocations.get(thisItem.locationId,None)
            log.info("Attempting to map location {0} to {1}".format(thisItem.locationId, rloc))
            thisItem.locationId = rloc
            
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
            rloc = self.mappedLocations.get(thisItem.locationId,None)
            log.info("Attempting to map location {0} to {1}".format(thisItem.locationId,rloc))
            dictItem["locationId"] = rloc
            #dictItem["nodeTypeId"] = None
            log.debug("--> New Node is {0}".format(dictItem))
            r = requests.post(theUrl,data=json.dumps(dictItem))
            log.debug(r)

    def upload_nodestate(self):
        """
        Upload Nodestates between two databases
        """

        log = self.log
        log.info("---- Upload Node States ----")

        session = self.localsession()

        #Get the last state upload
        mappingConfig = self.mappingConfig

        uploadDate = mappingConfig.get("lastStateUpdate", None)
        lastUpdate = None


        if uploadDate:
            log.debug("Last State upload from Config {0}".format(uploadDate))
            if uploadDate and uploadDate != "None":
                lastUpdate = dateutil.parser.parse(uploadDate)
        else:
            #Hack to match last nodestate with the first Reading we transfer
            lastUpdate = self.firstUpload

        log.info("Last Update from Config {0}".format(lastUpdate))

        #Otherwise we want to fetch the last synchronisation
        #Which is a little bit difficult as we dont have a house or
        #anything to base this on so we will have to rely on the nodestates
        #and the readings being synchonised

        #Count total number of Nodestates to upload
        theStates = session.query(models.NodeState)
        if lastUpdate:
            log.debug("-- Filter on {0}".format(lastUpdate))
            theStates = theStates.filter(models.NodeState.time > lastUpdate)

        origCount = theStates.count()
        log.info("--> Total of {0} Nodestates to transfer".format(origCount))
        rdgCount = origCount
        transferCount = 0

        while rdgCount > 0:
            theState = session.query(models.NodeState)
            if lastUpdate:
                theState = theStates.filter(models.NodeState.time > lastUpdate)
            theState = theState.order_by(models.NodeState.time)
            theState = theState.limit(self.pushLimit)
            rdgCount = theState.count()
            if rdgCount <= 0:
                log.info("--> No States Remain")
                return True

            transferCount += rdgCount
            log.debug("--> Transfer {0}/{1} States to remote DB".format(
                    transferCount,
                    origCount))

            #Convert to REST
            jsonList = []
            for x in theState:
                theItem = x.toDict() 
                theItem["id"] = None
                jsonList.append(theItem)
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
            self.save_mappings()

        return rdgCount > 0

    def upload_readings(self, theHouse):
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
        uploadDates = mappingConfig.get("lastupdate", None)
        lastUpdate = None
        if uploadDates:
            print uploadDates
            lastUpdate = uploadDates.get(str(theHouse.id), None)
            log.info("LAST UPDATE {0} {1}".format(lastUpdate, type(lastUpdate)))
            if type(lastUpdate) == datetime:
                pass
            elif lastUpdate and lastUpdate != 'None':
                lastUpdate = dateutil.parser.parse(lastUpdate)
            else:
                lastUpdate = None
        log.info("Last Update from Config is >{0}< >{1}<".format(lastUpdate,
                                                                 type(lastUpdate)))

        #TODO:
        # This is a temporary fix for the problem for nodestates,
        # Currently I cannot think of a sensible way
        # To do this without generting a lot of network traffic.
        self.firstUpload = lastUpdate

        #Get the last reading for this House
        session = self.localsession()

        #As we should be able to trust the last update field of the config file.
        #Only request the last sample from the remote DB if this does not exist.

        if lastUpdate is None:
            log.info("--> Requesting date of last reading in Remote DB")
            log.info("The House is {0}".format(theHouse))
            params = {"house":theHouse.address,
                      "lastUpdate":lastUpdate}
            theUrl = "{0}lastSync/".format(self.restUrl)

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

        #sys.exit(0)
        #Then Save
        uploadDates[str(theHouse.id)] = lastUpdate
        mappingConfig["lastupdate"] = uploadDates
        self.save_mappings()

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

        while True:
            #Add some timings
            stTime = time.time()
            theReadings = session.query(models.Reading).filter(models.Reading.locationId.in_(theLocations))
            if lastUpdate:
                theReadings = theReadings.filter(models.Reading.time > lastUpdate)
            theReadings = theReadings.order_by(models.Reading.time)
            #---theReadings = theReadings.limit(self.pushLimit)
            #theReadings = theReadings.limit(10)
            theReadings = theReadings.limit(10000)
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
                #log.debug("==> Converted {0}".format(dictReading))
                jsonList.append(dictReading)
                lastSample = reading.time

            jsonStr = json.dumps(jsonList)
            gzStr = zlib.compress(jsonStr)

            qryTime = time.time()
             #And then try to bulk upload them
            theUrl = "{0}bulk/".format(self.restUrl)

            restQry = requests.post(theUrl,data=gzStr)

            transTime = time.time()
            if restQry.status_code == 500:
                log.warning("Upload Fails")
                log.warning(restQry)
                sys.exit(0)
                raise Exception ("Upload Fails")
            

            log.info("--> Transferred {0}/{1} Readings to remote DB".format(transferCount,origCount))
            log.info("--> Timings: Local query {0}, Data Transfer {1}, Total {2}".format(qryTime - stTime, transTime -qryTime, transTime - stTime))
            lastUpdate = lastSample

            #And save the last date in the config file
            uploadDates[str(theHouse.id)] = lastUpdate
            mappingConfig["lastupdate"] = uploadDates
            self.save_mappings()

        #Return True if we need to upload more
        return rdgCount > 0

if __name__ == "__main__":
    logging.debug("Testing Push Classes")

    server = PushServer(configfile="test.conf")
    server.sync()
