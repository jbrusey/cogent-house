"""
Functionality to upload from a Arch Rock database

Be Warned there is lots of weirdness in the database that does not make this quite
as straight forward as it could be.

Duplicate nodes with different Id's are one such problem,  This arises when a "New" deployment is started.
The way I have been dealing with this is to use node address to index nodes when they are added, 
Rather than 
"""

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__) 
log.setLevel(logging.DEBUG)

#import orbit_viewer.models as models
#import orbit_viewer.models.meta as meta

#And for the local connection
import sqlalchemy
import sqlalchemy.orm

from sqlalchemy.ext.declarative import declarative_base

import datetime

import mainDb
import models

BASE_NODE_ID = 118118

localBase = declarative_base()

#GLOBALS FOR SENSOR TYPES
ALLOWED_TYPES = [["Humidity","Humidity"],
                 ["LightPAR","Light PAR"],
                 ["LightTSR","Light TSR"],
                 ["Temperature","Temperature"],
                 ["ADC0","CO2"],
                 ["CO2","CO2"],
                 ["Voltage","Battery Voltage"],
                 ]


class Data(localBase):
    """ Meta class to Represent Data in the Reflected Database.
    
    .. warning:: It is not intended for this class to be directly instantiated, only created via sqlalchemy reflection
    """
    __tablename__ = "data"
    data_key = sqlalchemy.Column("data_key",sqlalchemy.Integer,primary_key = True)
    node_key = sqlalchemy.Column("node_key",sqlalchemy.Integer)
    datasource_key = sqlalchemy.Column("datasource_key",sqlalchemy.Integer)
    timestamp = sqlalchemy.Column("timestamp",sqlalchemy.DateTime)
    value = sqlalchemy.Column("value",sqlalchemy.Float)
    text_value = sqlalchemy.Column("text_value",sqlalchemy.Text)
    

    def __str__(self):
        outStr = []
        outStr.append("Key: %s" %self.data_key)
        outStr.append("Node Id: %s" %self.node_key)
        outStr.append("Sensor Id: %s" %self.datasource_key)
        outStr.append("Time: %s" %self.timestamp)
        outStr.append("Value: %s" %self.value)
        return "\t".join(outStr)


class Source(localBase):
    """
    Reflect the Datasource_Dimension Table
    
    @warning: This does not have all the info in the original table.
              Rather, it just includes the stuff we will be using
    """
    __tablename__ = "datasource_dimension"
    datasource_key = sqlalchemy.Column(sqlalchemy.Integer,primary_key=True)
    datasource_created = sqlalchemy.Column(sqlalchemy.DateTime)
    source = sqlalchemy.Column(sqlalchemy.Text)
    addr = sqlalchemy.Column(sqlalchemy.Text)
    name = sqlalchemy.Column(sqlalchemy.Text)

    def __str__(self):
        outStr = []
        outStr.append("dsKey {0}".format(self.datasource_key))
        outStr.append("created {0}".format(self.datasource_created))
        outStr.append("source {0}".format(self.source))
        outStr.append("addr {0}".format(self.addr))
        outStr.append("name {0}".format(self.name))

        return "  ".join(outStr)

class Ar_Node(localBase):
    """ Table to deal with Arch Rock Nodes"""
    __tablename__ = "node_dimension"
    node_key = sqlalchemy.Column(sqlalchemy.Integer,primary_key = True)
    node_created = sqlalchemy.Column(sqlalchemy.DateTime)
    addr = sqlalchemy.Column(sqlalchemy.Text)
    name = sqlalchemy.Column(sqlalchemy.Text)
    short_addr = sqlalchemy.Column(sqlalchemy.Integer)

    def __str__(self):
        outStr = []
        outStr.append("Key: {0}".format(self.node_key))
        outStr.append("Created: {0}".format(self.node_created))
        outStr.append("Addr: {0}".format(self.addr))
        outStr.append("saddr {0}".format(self.short_addr))
        outStr.append("Name: {0}".format(self.name))
        return "  ".join(outStr)
                      

class ArchRockDB(object):
    """Functionality to connect to a Arch Rock Postgresql Database"""
    def __init__(self,url="127.0.0.1",database="pp",address=None):
        """Create the connection"""

        log.debug("Initialising Arch Rock Engine")
        #engine = sqlalchemy.create_engine('postgresql+psycopg2://postgres:@{0}:5432/{1}'.format(address,database), convert_unicode=True)

        engine = sqlalchemy.create_engine('postgresql+psycopg2://pp:pr1merp4ck@{0}:5432/{1}'.format(url,database),
                                          convert_unicode=True,
                                          server_side_cursors=True)

        #Bind Metadata to those tables declared in Base
        localBase.metadata.create_all(engine)

        # #And Session Maker
        self.Session = sqlalchemy.orm.sessionmaker(bind=engine)
        self.meta = localBase.metadata


        self.houseAddress = address
        #Load all known sensor types
        sensorDict = {}
        #session = meta.DBSession()
        #sensorTypes = session.query(models.sensor.SensorType).all()

        #log.debug("{0} Sensor Types {0}".format("-"*20))
        #for sensor in sensorTypes:
        #    log.debug(sensor)
        #    sensorDict[sensor.sensor_type] = sensor
        #log.debug("{0}".format("-"*40))

        #self.sensorTypes= sensorDict
        #log.debug("PG Engine Init Complete")        
        #self.log = log

    def listTables(self):
        """Print and Return a list of all tables in this database

        :returns: A List of Tables in the database
        """

        for t in self.meta.sorted_tables:
            print t.name

        return self.meta.sorted_tables

    def listNodes(self):
        """Print and return a list of nodes"""
        self.log.debug("{0} Nodes {0}".format("-"*20))
        session = self.Session()
        query = session.query(Ar_Node).all()
        for item in query:
            self.log.debug(item)


    def createDatabase(self):
        """Create the Required Database Objects"""
        session = models.meta.Session()
        arSession = self.Session()

        deploymentName = "archRock"
        houseName = self.houseAddress

        theDep = session.query(models.Deployment).filter_by(name=deploymentName).first()
        log.debug("Checking for existing deployment {0}".format(theDep))
        if theDep is None:
            #Create a new deployment
            theDep = models.Deployment(name=deploymentName)
            session.add(theDep)
            session.flush()
            log.debug("Adding Deployment to database {0}".format(theDep))


        #And check for Houses
        theHouse = session.query(models.House).filter_by(address=houseName).first()
        log.debug("Checking for house {0}".format(theHouse))
        if theHouse is None:
            theHouse = models.House(address=houseName,
                                    deploymentId = theDep.id)
            session.add(theHouse)
            session.flush()
            log.debug("Adding New House {0}".format(theHouse))


        self.theHouse = theHouse

        emptyRoom = session.query(models.RoomType).filter_by(name="Unocupied").first()

        nodeMap = {}
        #Temp storage for <ADDDR> <Node>
        addrMap = {}

        #We want to setup nodes / Rooms / Locations based on the node_dimension table
        nodeQry = arSession.query(Ar_Node)
        for item in nodeQry:
            #Dont bother with the router
            if item.name == "archrock-router":
                continue

            #Check / Create a node if required
            nodeId = int(item.addr[8:],16)
            log.debug("{0} {1} {2}".format(item,item.addr,nodeId))
            
            #nodeId = BASE_NODE_ID + item.short_addr
            
            theNode = session.query(models.Node).filter_by(id = nodeId).first()
            if theNode is None:
                theNode = models.Node(id=nodeId)
                session.add(theNode)
                session.flush()
                log.debug("Creating New Node {0}".format(theNode))
            
            #Next we create a room / Location
            roomName = item.name
            if not roomName == "":
                log.debug("Room Name is {0}".format(roomName))

                theRoom = session.query(models.Room).filter_by(name=roomName).first()
                if theRoom is None:
                    theRoom = models.Room(name=roomName,
                                          roomTypeId=emptyRoom.id)
                    log.debug("Creating Room {0}".format(theRoom))
                    session.add(theRoom)
                    session.flush()

                #And now we can turn this room into a Location
                theLocation = session.query(models.Location).filter_by(houseId=theHouse.id,
                                                                       roomId = theRoom.id).first()
                if theLocation is None:
                    theLocation = models.Location(houseId = theHouse.id,
                                                  roomId = theRoom.id)
                    session.add(theLocation)
                    log.debug("Creating Location {0}".format(theLocation))
                    session.flush()
            #Last thing we create a mapping between the node and the Location
            nodeMap[item.node_key] = [theNode,theLocation]
            addrMap[item.addr] = theNode

        log.debug(nodeMap)
        self.nodeMap = nodeMap
        #We also need to do mapping for sensor types etc
        #theQry = arSession.query(Source)

        #Map the Types we are expecting to types from the database
        sensorTypeMap = {}
        for sType in ALLOWED_TYPES:
            theType = session.query(models.SensorType).filter_by(name=sType[1]).first()
            
            log.debug("AR: {0}  Local {1}".format(sType,theType))
            sensorTypeMap[sType[0]] = theType
            
        log.debug(sensorTypeMap)

        sensorMap = {}
        
        sQry = arSession.query(Source)
        for item in sQry:
            thisItem = sensorTypeMap.get(item.source,None)
            if thisItem:
                sensorMap[item.datasource_key] = sensorTypeMap[item.source]

        self.sensorMap = sensorMap
                
        

                          
        


            #Next we want to add a room
        #sensorDict = {}
        #sensorTypes = session.query(models.sensor.SensorType).all()

        #log.debug("{0} Sensor Types {0}".format("-"*20))
        #for sensor in sensorTypes:
        #    log.debug(sensor)
        #    sensorDict[sensor.sensor_type] = sensor
        #log.debug("{0}".format("-"*40))

        #self.sensorTypes= sensorDict
        #log.debug("PG Engine Init Complete")        
        #self.log = log



        session.flush()
        session.commit()


    def transferData(self,deploymentName,startDate = None,endDate = None):
        """
        Transfer Data from the DB

        @param deplotmentName: Name of the Deployment
        @param startDate: If we have more than one deployment can filter here
        @param endDate: as Above
        """
        log = self.log
        status = {"deployment":None,
                  "nodes":[],
                  "sensors":[]}

        #Create Sessions
        session = meta.Session()
        arSession = self.Session()

        
                
#         sampleTable = models.sample.Sample

        
#         status["deployment"] = theDeployment
        
#         # #Next thing to do is to add all the Nodes but as the AR database is a little arse about face.
#         # We need to do some trickery here.

#         # Find the Nodes
#         arNodes = arSession.query(Ar_Node)
#         #if startDate:
#         #    arNodes = arNodes.filter(Ar_Node.node_created >= startDate)
#         #if endDate:
#         #    arNodes = arNodes.filter(Ar_Node.node_created <= endDate)
        
#         #I want to add a quick filter here for testing
#         #arNodes = arNodes.filter_by(name = "Node1")
#         arNodes = arNodes.all()

#         #To Hold all our nodes and sensors
#         nodeDict = {}
#         nodeIdDict = {}
#         addrDict = {}
#         sensorDict = {}
#         sensorTypes = self.sensorTypes

#         #Node / Sensors Pairs
#         nodePairs = {}
    
#         sensorData = {}
#         print "Finding Nodes"
#         for node in arNodes:
#             print node
#             #Do we already know about this node
#             theNode = nodeDict.get(node.addr,None)
#             if not theNode:
#                 #Check it does not already exist in the database
#                 theQry = session.query(models.nodes.Node).filter_by(deploymentId = theDeployment.Id,
#                                                                     name=node.name,
#                                                                     serialNo = node.addr)

#                 theQry = theQry.first()
                    
#                 if theQry is None:
#                     theNode = models.nodes.Node(deploymentId = theDeployment.Id,
#                                                 name=node.name,
#                                                 serialNo = node.addr)
#                     log.info("Node {0} not in Database".format(theNode))
#                     nodePairs[node.addr] = []
                    
#                 else:
#                     theNode = theQry
#                     log.info("Node {0} Exists ({1})".format(theNode,type(theNode)))
                
#                 #session.flush()

#                 nodeDict[node.addr] = theNode            
#                 addrDict[node.addr] = [node.node_key]
#                 #theAddr = addrDict.get(node.addr,[])
#                 #theAddr.append(node.node_key)
#                 #addrDict[node.addr] = theAddr
#             else:
#                 #log.debug("Dictonary Entry Exists for {0}".format(node))
#                 addrDict[node.addr].append(node.node_key)

#             nodeIdDict[node.node_key] = theNode

#         #We should also check if the node has any data attached to it before saving it in the database
        
#         for nodeAddr,nodeId in addrDict.iteritems():
#             #log.debug("Id: {0} Item: {1}".format(nodeAddr,nodeId))
#             #Check if the data Exists

#             sensorQry = arSession.query(Source.datasource_key)
#             sensorQry = sensorQry.filter_by(addr = nodeAddr,
#                                             source="Temperature")
#             #log.debug(sensorQry.all())

#             theQuery = arSession.query(Data)
#             theQuery = theQuery.filter(Data.node_key.in_(nodeId))
#             #log.debug("Sensor Query {0}".format(sensorQry))
#             theQuery = theQuery.filter(Data.datasource_key.in_(sensorQry))
        
#             if startDate:
#                 theQuery = theQuery.filter(Data.timestamp >= startDate)
#             if endDate:
#                 theQuery = theQuery.filter(Data.timestamp <= endDate)

            

#             #And Filter by the known sensor types
            

#             #theQuery = theQuery.limit(10)
#             cnt = theQuery.first()
#             log.debug("Item {1} Has Data {0} ".format(cnt,nodeDict[nodeAddr]))

#             if cnt is None:
#                 log.warning("Node {0} Has no Data".format(nodeDict[nodeAddr]))
#                 del nodeDict[nodeAddr]
#             else:
#                 status['nodes'].append(nodeDict[nodeAddr])
#                 session.add(nodeDict[nodeAddr])

#         #log.debug("New Dict")
#         #for addr,node in nodeDict.iteritems():

#         #And Add Sensors
#         for node in arNodes:
#             theNode = nodeDict.get(node.addr,None)
#             if theNode:
#                 #log.debug("#"*40)
#                 #log.info("Finding sensors for node: {0} ({1})".format(node,theNode))

#                 #Find any sensors attached to this node
#                 arSensors = arSession.query(Source).filter_by(addr = node.addr)
#                 #Strip out meta sensors like voltage
#                 arSensors = arSensors.filter(Source.source.in_(ALLOWED_TYPES))
#                 arSensors = arSensors.all()
                
#                 #Check and Add to Database
#                 #log.debug("=== Sensors ===")

#                 for sensor in arSensors:                                     
#                     #Check if we know about this Sensor
#                     theSensor = sensorDict.get(sensor.datasource_key,None)
#                     #log.debug("--> Sensor {0} --> Dictonary {1}".format(sensor,theSensor))

#                     if not theSensor:
#                         #Check Database
#                         #log.debug("Sensor Name {0}".format(sensor.name))
#                         sName = sensor.name
#                         if sName == "CO2":
#                             sName = "Co2"
#                         sType = sensorTypes[sName]
#                         theQry = session.query(models.sensor.Sensor).filter_by(nodeId = theNode.Id,
#                                                                                sensorTypeId = sType.Id)
#                         theQry = theQry.first()

#                         if theQry is None:
#                             thisSensor = models.sensor.Sensor(nodeId = theNode.Id,
#                                                               sensorTypeId = sType.Id,
#                                                               name = sName)

#                             session.add(thisSensor)
#                             log.debug("--> Checking Database for sensor {0}: Adding Sensor".format(theQry))
#                         else:
#                             thisSensor = theQry

#                         sensorDict[sensor.datasource_key] = thisSensor


#                     #log.debug("--> Copied Sensor {0}".format(thisSensor))
                                
        
#         status["nodes"] = nodeDict.values()
#         status["sensors"] = sensorDict.items()
#         #return status
        
#         log.debug("{0} Sensors {0}".format("-"*20))
#         for key,item in sensorDict.iteritems():
#             log.debug("{0} {1}".format(key,item))
                 
        
#         #The Final thing is to fetch and store all the data.
#         dataQuery = arSession.query(Data)

#         #if not nodeIdDict:
#         #    log.warning("No Node ID's")
#         dataQuery = dataQuery.filter(Data.node_key.in_(nodeIdDict.keys()))
#         #if not sensorDict:
#         #    log.warning("No Sensor ID's")
#         dataQuery = dataQuery.filter(Data.datasource_key.in_(sensorDict.keys()))
        
        
#         log.debug("Removing previous data")
#         #deleteQuery = dataQuery.all().delete()
#         #log.debug("{0} Items removed".format(deleteQuery))
#         #sys.exit(0)


#         if startDate:
#             dataQuery = dataQuery.filter(Data.timestamp >= startDate)
#         if endDate:
#             dataQuery = dataQuery.filter(Data.timestamp <= endDate)

        
#         #dataQuery = dataQuery.order_by(Data.timestamp)

#         #Data Cacheing to help on updates
#         datacache = []
#         tempDict = {}
#         cacheindex = 0
#         cachelimit = 144 #About 12 hours worth of data
#         #cachelimit = 144
#         setIdx = 0

#         currentOffset = 0
#         transferLimit = 100

#         #t1 = time.time()
#         log.info("Counting Rows")
#         #theCount = dataQuery.count()
#         #log.info("{0} Rows Found".format(theCount))
#         #t2 = time.time()
#         #log.debug("{0} Seoconds Taken".format(t2-t1))


#         #log.info("Fetching {0} Rows".format(dataQuery.count()))
        

#         #for dataItem in dataQuery.limit(100):
#         #    if currentOffset > transferLimit:
#         #        log.debug("Records Stored")
#         #    currentOffset += 1

#         tempStore = []
#         dataQuery = dataQuery
#         sampleList = []
#         sampleCount = 0
#         maxSamples = 1000 #Items before a commit
#         loopIndex = 0
#         dataQuery = dataQuery.limit(5000).offset(1000000)
#         log.info("Starting to save Data")
#         for dataItem in dataQuery.yield_per(1000):
#             transaction.begin()
#             sensorId = sensorDict[dataItem.datasource_key]

#             thisSample = sampleTable(sensorId = sensorId.Id,
#                                          timestamp = dataItem.timestamp,
#                                          value = dataItem.value)

#             sampleList.append(thisSample)

#             if sampleCount > maxSamples:
#                 log.debug("Saving items {0}".format(loopIndex))
#                 loopIndex += 1
#                 session.add_all(sampleList)

#                 try:
#                     session.flush()
#                     transaction.commit()
#                 except sqlalchemy.exc.IntegrityError,e:
#                     session.rollback()
#                     log.warning("Some Error {0}".format(e))
#                     for mergeItem in sampleList:
#                         session.merge(mergeItem)
#                         session.flush()
#                         transaction.commit()

#                 sampleList = []
#                 sampleCount = 0

#             sampleCount += 1
        

        

            


# #            print item
#         #for item in dataQuery.yield_per(5):
#         #    print item
        
#         log.info("Samples Stored, Summarising")
#         status["nodes"] = nodeDict.values()
#         status["sensors"] = sensorDict.items()
        
#         return status

#         while True:
#             transaction.begin()
#             thisQuery = dataQuery.limit(transferLimit).offset(currentOffset)


#             theData = thisQuery.all()
#             log.debug("Iteration {0}: {1}".format(currentOffset,theData[0]))
#             if theData is None:
#                 log.info("Reached end of values")
#                 break
        
#             currentOffset += transferLimit
#             sampleList = []
#             for dataItem in theData:
#                 sensorId = sensorDict[dataItem.datasource_key]

#                 if sensorId is None:
#                     log.warning("Error Fetching Id for {0}".format(dataItem))

#                 thisSample = sampleTable(sensorId = sensorId.Id,
#                                          timestamp = dataItem.timestamp,
#                                          value = dataItem.value)

#                 sampleList.append(thisSample)

#             #Test if we have samples for this
#             #thisSample = sampleList[0]
#             #theQry = session.query(sampleTable).filter_by(sensorId = thisSample.sensorId,
#             #                                              timestamp = thisSample.timestamp)
#             #hasData = theQry.first()
#             hasData = False
#             if hasData:
#                 log.warning("Readings Exists {0}".format(thisSample))
#             else:
#                 session.add_all(sampleList)

#             try:
#                 session.flush()
#                 transaction.commit()
#             except sqlalchemy.exc.IntegrityError,e:
#                 session.rollback()
#                 #transaction.rollback()
#                 transaction.begin()
#                 log.warning("Some Error {0}".format(e))
#                 for mergeItem in sampleList:
#                     session.merge(mergeItem)
                    
#                 session.flush()
#                 transaction.commit()
        
        


#         # summarise(theDeployment.Id)
#         # log.info("Upload Complete")
#         # #And Run a summary for this 
#         # node.summariseData(theDeployment.Id)
#         return status



if __name__ == "__main__":
    log.debug("Connecting to central DB")
    mainDb.initDB()

    log.debug("Connecting to Postgresql")
    theDb = ArchRockDB(database="PriorPark41",address="41PriorPark")
    theDb.listTables()
    theDb.createDatabase()
    theDb.transferData()
