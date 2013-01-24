"""
Modified Version of the Push Server to Deal with the Old Samson Database

.. warning:: Requires SQLA 0.8 or above to deal with automagic relfection

.. warning:: The Old (or testing) Sampson Database has GAS (sensortype) as ID 9,  I think this should be Air Quality.
             This is a Bad Thing (TM),  Remapping sensors types would be foolish in my opinion.
             Use the following SQL to check that this is not the case in newer versions
             
             SELECT * FROM `old-sampson`.SensorType as sam
             LEFT OUTER JOIN test.SensorType as test
             ON sam.name = test.name
             WHERE  test.id IS NULL
             UNION

             SELECT * FROM `old-sampson`.SensorType as sam
             RIGHT OUTER JOIN test.SensorType as test
             ON sam.name = test.name
             WHERE sam.id IS NULL

             To get a list of SensorTypes that are not matching in each database.
             

             #Then update 
"""

import logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(name)-10s %(levelname)-8s %(message)s",
                    datefmt = "%m-%d-%Y %H:%M",
                    )
#Add a File hander
#fh = logging.FileHandler("push_out.log")
logsize = (1024*1024) * 5 #5Mb Logs


import logging.handlers
fh = logging.handlers.RotatingFileHandler("sampson_push_out.log",maxBytes=logsize,backupCount = 5)
fh.setLevel(logging.INFO)

fmt = logging.Formatter("%(asctime)s %(name)-10s %(levelname)-8s %(message)s")
fh.setFormatter(fmt)


__version__ = "0.1.0"

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


import json
import urllib

import requests
import RestPusher
import zlib

#Major Change,  Reflect remote DB
dbString = "mysql://root:Ex3lS4ga@127.0.0.1/faraday"

#Setup New Delariative Reflection stuff, (REQUIRES SQLA > 0.8)
from sqlalchemy.ext.declarative import declarative_base, DeferredReflection

Base = declarative_base(cls=DeferredReflection)


class SensorType(Base,meta.InnoDBMix):
    __tablename__ = "SensorType"

    def __cmp__(self,other):
        
        if self.id == other.id:
            return 0
            #if self.name == other.name:
            #    return 0
        return -1

class RoomType(Base,meta.InnoDBMix):
    __tablename__ = "RoomType"
    
    def __cmp__(self,other):
        if self.id == other.id:
            if self.name == other.name:
                return 0
            return -1
        return self.id - other.id

class Room(Base,meta.InnoDBMix):
    __tablename__ = "Room"

    def __cmp__(self,other):
        if self.id == other.id:
            if self.name == other.name:
                return 0
            return -1
        return self.id - other.id
        

class Deployment(Base,meta.InnoDBMix):
    __tablename__ = "Deployment"
    
    def __cmp__(self,other):
        if self.id == other.id:
            if self.name == other.name:
                return 0
            return -1
        return self.id - other.id

class House(Base,meta.InnoDBMix):
    __tablename__ = "House"
    
    def __cmp__(self,other):
        if self.id == other.id:
            if self.address == other.address:
                return 0
            return -1
        return self.id - other.id

class Node(Base,meta.InnoDBMix):
    __tablename__ = "Node"
    def __cmp__(self,other):
        return self.id - other.id

class Reading(Base,meta.InnoDBMix):
    __tablename__ = "Reading"
    pass

class PushServer(RestPusher.PushServer):
    """Subclass of the Rest Pusher to deal with old style Sampson Databases"""

    def createEngine(self,localURL):
        """Create a connection to the DB engine"""
        log = self.log
        engine = sqlalchemy.create_engine(localURL)

        #This 
        Base.prepare(engine)

        #models.initialise_sql(engine)
        localSession = sqlalchemy.orm.sessionmaker(bind=engine)
        self.localSession = localSession
        
    def QueueLocations(self,locations,configParser,mappingConfig,pushLimit):
        localSession = self.localSession
        log = self.log
        syncList = []

        for item in locations:
            #Check if we need to synchronise to this location.
            needSync = locations.as_bool(item)
            log.debug("Location {0} Needs Sync {1}".format(item,needSync))

            if needSync:
                #Enque
                thisLoc = configParser[item]
                log.info("Adding {0} to synchronise Queue".format(thisLoc))
                thePusher = SampsonPusher(localSession, #Session
                                   thisLoc["resturl"], #Url to Push to
                                   mappingConfig, #Mapping Configuration file
                                   pushLimit,                                   
                                   )
                syncList.append(thePusher)

        self.syncList = syncList 

class SampsonPusher(RestPusher.Pusher):
    def __init__(self, localSession,restUrl,dbConfig,pushLimit=5000):
        """Initalise a pusher object

        :param localSession: A SQLA session, connected to the local database
        :param restUrl: URL of rest interface to upload to
        :param dbConfig: Config Parser that holds details of mappings for the DB we are synching
        :param pushLimit: Number of samples to transfer in each "Push"
        """
        super(SampsonPusher,self).__init__(localSession,restUrl,dbConfig,pushLimit)
        self.SensorType = SensorType
        self.RoomType = RoomType
        self.Room = Room
        self.Deployment = Deployment

        self.House = House
        self.Node = Node
        #self.Location = Location

    def unpackJSON(self,theList):
        """Unpack Json Objects returned by the REST interface.
        This needs to be seperated out to allow the Sampson Verison on the code to work

        :var theList: Json Encoded body
        :return: Genertor object for these elements
        """
        
        """Generator object to convert JSON strings from a rest object
        into database objects"""
        #Convert from JSON encoded string
        if type(theList) == str:
            theList = json.loads(theList)

        #Make the list object iterable
        if not type(theList) == list:
            theList = [theList]


        typeMap = {"sensortype":SensorType,
                   "roomtype":RoomType,
                   "room":Room,
                   "deployment":Deployment,
                   "house":House,
                   "node":Node,
        #           "reading":Reading,
        #           "sensor":Sensor,
        #           "nodestate":NodeState,
        #           "roomtype":RoomType,

        #           "room":Room,
                   "location":models.Location,
                   }


        for item in theList:
            #print "--> {0}".format(item)
            #Convert to the correct type of object
            theType = item["__table__"]
            theModel = typeMap[theType.lower()]()
            #print theModel

            theModel.fromJSON(item)
            yield theModel
                
    def mapLocations(self):
        #Synchronise Locations
        # Rather than deal with new locations, this instead just loads the location map
        log = self.log
        log.debug("----- Syncing Locations ------")
        # lSess = self.localSession()
        # restSession = self.restSession

        # #Get the list of deployments that may need updating
        # #Deployment = models.Deployment
        # theQry = lSess.query(self.Location)

        # mappedHouses = self.mappedHouses
        # mappedRooms = self.mappedRooms
        mappedLocations = self.mappedLocations
        
        mappingConfig = self.mappingConfig
        configLoc = mappingConfig.get("location",{})
        mappedLocations.update(dict([(int(k),v) for k,v in configLoc.iteritems()]))
#         for k,v in configLoc.iteritems():
#             log.debug("K {0} V {1}".format(k,v))
#             keyParts = k.strip("()").split(",")
#  #           print keyParts
#             theKey = tuple([int(x.strip("L")) for x in keyParts])
# #            print theKey
#             mappedLocations[theKey] = int(v)
#             #keyParts = k.split(",")
#             #theKey = (keyParts[0].strip(),keyParts[1].strip())
#             #print theKey
#         #sys.exit(0)

    def syncNodes(self):
        """Synchronise Nodes between databases
        This will not 'pull' new nodes down 
        #Currently the node 'Location' field is not updated,  we need to work out how to do this
        while avoiding overwriting a node with an out of date location.

        TODO:  A Couple of potential issues here,  1) no Sych of Location,  No Sync of Sensor Types (calibration)
        """
        log = self.log
        log.debug("----- Syncing Nodes ------")
        session = self.localSession()
        #restSession = self.restSession

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


        # #Get the list of deployments that may need updating
        # #Deployment = models.Deployment
        # theQry = lSess.query(self.Node)#.limit(10)

        # sys.exit(0)
        #Location Mappings
        locMap = self.mappedLocations
        houseMap = self.mappedHouses
        roomMap = self.mappedRooms

        #log.debug("{0} HOUSE {0}".format("-"*20))
        #log.debug(houseMap)
        #log.debug("{0} ROOM {0}".format("-"*20))
        #log.debug(roomMap)

        #print locMap
        #print houseMap
        #print roomMap
        #log.setLevel(logging.DEBUG)
        for item in theQry:
            #log.debug(item)
            #We need to make sure the deployment is mapped correctly
            params = {"id":item.id}
            theUrl = "node/?{0}".format(urllib.urlencode(params))                            
            log.debug("-"*60)
            log.debug("Node {0} = HouseId {1} Room Id {2}".format(item.id,item.houseId,item.roomId))
            
            #Check if we have a location for this node in the Map
            theLocation = locMap.get((item.houseId,item.roomId),None)
            log.debug("--> Location is {0}".format(theLocation))
            
            if theLocation is None:
                log.debug("No Such Location, Checking for mapping on remote server")

            
                hId = houseMap[item.houseId]
                rId = roomMap.get(item.roomId,None)
                params = {"houseId":hId,
                          "roomId":rId}
                log.debug("Updated Parameters {0}".format(params))
                theUrl = "{0}location/".format(self.restUrl)
                restQuery = requests.get(theUrl,params = params)
                jsonBody = restQuery.json()
                log.debug(jsonBody)
                
                if jsonBody == []:
                    log.debug("No Such Location in remote database, Creating")
                    restQry = requests.post(theUrl,data=json.dumps(params))
                    log.debug(restQry)
                    jsonBody = restQry.json()
                    log.debug(jsonBody)
                    #newItem = self.uploadItem(theUrl,params)
                    #log.debug(newItem)
                    #sys.exit(0)
                else:
                    jsonBody = jsonBody[0]
                log.debug("Room {0} House {1} Maps to Location {2}".format(hId,rId,jsonBody["id"]))
                locMap[item.id] = jsonBody["id"]
            #restQuery = restSession.request_get(theUrl,args=params)
            #log.debug("--> Get {0}".format(restQuery))
            #jsonBody = json.loads(restQuery["body"])
            #log.debug(jsonBody)
            # sys.exit(0)
            # if not jsonBody:
            #     params['__table__'] = 'Location'
            #     #We need to upload the new Location
            #     #newItem = self.uploadItem(theUrl,params)
            #     log.info("Creating new location on remote server {0}".format(params))
                
            #     restQry = restSession.request_post(theUrl,
            #                                        body=json.dumps(params))

            #     #The Query should now hold the Id of the item on the remote DB
            #     log.debug(restQry)
            #     theItem = json.loads(restQry["body"])
            #     print theItem
            #     locMap[item.id] = theItem[0]['id']
            # else:
            #     log.debug("--> Mapping Location {0}".format(item))
            #     locMap[item.id] = jsonBody[0]['id']
            
            #Look for the item
            #theBody = item.toDict()
            #del(theBody["nodeTypeId"])
        self.mappedLocations = locMap
        log.debug(locMap)
        #sys.exit(0)

        
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
            lastUpdate = uploadDates.get(str(theHouse.id),None)
            if lastUpdate and lastUpdate != 'None':
                lastUpdate = dateutil.parser.parse(lastUpdate)
        log.info("Last Update from Config is {0}".format(lastUpdate))

        #Get the last reading for this House
        session = self.localSession()
        #restSession =self.restSession

        #Request node Ids first, this will save on requesting times for houses where we have no data
        nodeQry = session.query(Node).filter_by(houseId = theHouse.id)
        if nodeQry.count() == 0:
            log.info("No Node Ids for this House. {0}".format(theHouse.id))
            return 0

        nodeIds = [x.id for x in nodeQry]
        log.info("--> Node Ids {0}".format(nodeIds))

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

        #We Dont have any locations in the Local DB so this bit needs reworking
        #nodeIds = [x.id for x in theHouse.nodes]


        # #Get locations associated with this House
        # theLocations = [x.id for x in theHouse.locations]

        #Count the Number of Readings we need to transfer
        #theReadings = session.query(models.Reading).filter(models.Reading.locationId.in_(theLocations))
        theReadings = session.query(Reading).filter(Reading.nodeId.in_(nodeIds))
        if lastUpdate:
            theReadings = theReadings.filter(Reading.time > lastUpdate)

        #print theReadings.first()
        #sys.exit(0)
        #sys.exit(0)
        origCount = theReadings.count()
        log.info("--> Total of {0} samples to transfer".format(origCount))
        rdgCount = origCount
        transferCount = 0
                          
        #for x in range(2):
        while rdgCount > 0:
        #while True:
            #Add some timings
            stTime = time.time()
            theReadings = session.query(Reading).filter(Reading.nodeId.in_(nodeIds))
            if lastUpdate:
                theReadings = theReadings.filter(Reading.time > lastUpdate)
            theReadings = theReadings.order_by(Reading.time)
            #theReadings = theReadings.limit(self.pushLimit)
            theReadings = theReadings.limit(10000)
            rdgCount = theReadings.count()
            if rdgCount <= 0:
                log.info("--> No Readings Remain")
                return True
            
            transferCount += rdgCount

            log.debug("--> Transfer {0}/{1} Readings to remote DB".format(transferCount,origCount))

            jsonList = [] #Blank Object to hold readings
            for reading in theReadings:
                #Convert our Readings to REST, and remap to the new locations
                dictReading = reading.toDict()
                log.debug("==> {0}".format(dictReading))

                #Convert the Reading to the new Location Format 
                theLocation = mappedLocations[reading.nodeId]
                #log.debug("--> Node {0} Maps to Location {1}".format(reading.nodeId,theLocation))
                
                dictReading['locationId'] = mappedLocations[reading.nodeId]
                dictReading['typeId'] = mappedTypes[reading.type]
                dictReading['type'] = mappedTypes[reading.type]
                del(dictReading['id'])
                
                log.debug("--> {0}".format(dictReading))            
                
                jsonList.append(dictReading)
                lastSample = reading.time

            #sys.exit(0)
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
            #sys.exit(0)

        #Return True if we need to upload more
        return rdgCount > 0





if __name__ == "__main__":
    print "Processing"
    foo = PushServer(dbString)
    foo.sync()
