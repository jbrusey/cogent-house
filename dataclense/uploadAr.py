"""
Functionality to upload from a Arch Rock database

Be Warned there is lots of weirdness in the database that does not make this quite
as straight forward as it could be.

Duplicate nodes with different Id's are one such problem,  This arises when a "New" deployment is started.
The way I have been dealing with this is to use node address to index nodes when they are added, 
Rather than 
"""

import logging
log = logging.getLogger(__name__) 
log.setLevel(logging.DEBUG)

import orbit_viewer.models as models
import orbit_viewer.models.meta as meta

#And for the local connection
import sqlalchemy
import sqlalchemy.orm

from sqlalchemy.ext.declarative import declarative_base

import datetime
import transaction

localBase = declarative_base()

import general
from pyramid.response import Response
from pyramid.renderers import render_to_response

from node import summariseData as summarise

import csv
import time

#GLOBALS FOR SENSOR TYPES
ALLOWED_TYPES = ["Humidity","LightPAR","LightTSR","Temperature","ADC0","CO2"]
#Map these types to ones we know about in the database

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


    def __str__(self):
        outStr = []
        outStr.append("Key: {0}".format(self.node_key))
        outStr.append("Created: {0}".format(self.node_created))
        outStr.append("Addr: {0}".format(self.addr))
        outStr.append("Name: {0}".format(self.name))
        return "  ".join(outStr)
                      
    
    


class ArchRockDB(object):
    """Functionality to connect to a Arch Rock Postgresql Database"""
    def __init__(self,address="127.0.0.1",database="pp",deployment=None):
        """Create the connection"""
        log = logging.getLogger(__name__)
        log.setLevel(logging.DEBUG)

        log.debug("Initialising Arch Rock Engine")
        #engine = sqlalchemy.create_engine('postgresql+psycopg2://postgres:@{0}:5432/{1}'.format(address,database), convert_unicode=True)

        engine = sqlalchemy.create_engine('postgresql+psycopg2://pp:pr1merp4ck@{0}:5432/{1}'.format(address,database), convert_unicode=True,server_side_cursors=True)

        #Bind Metadata to those tables declared in Base
        localBase.metadata.create_all(engine)

        # #And Session Maker
        self.makeSession = sqlalchemy.orm.sessionmaker(bind=engine)
        self.meta = localBase.metadata

        #Load all known sensor types
        sensorDict = {}
        session = meta.DBSession()
        sensorTypes = session.query(models.sensor.SensorType).all()

        log.debug("{0} Sensor Types {0}".format("-"*20))
        for sensor in sensorTypes:
            log.debug(sensor)
            sensorDict[sensor.sensor_type] = sensor
        log.debug("{0}".format("-"*40))

        self.sensorTypes= sensorDict
        log.debug("PG Engine Init Complete")        
        self.log = log

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
        session = self.makeSession()
        query = session.query(Ar_Node).all()
        for item in query:
            self.log.debug(item)


    # def cleanData(self):
    #     #""Remove Cruft from the database""
    #     log = self.log 
    #     log.debug("Cleaning Data")
    #     session = self.makeSession()

    #     deleteNodes = []
    #     #First Pass Remove sensors and data datatypes that have no data
    #     nodeQry = session.query(Ar_Node).all()
    #     log.debug("{0} nodes returned".format(len(nodeQry)))
    #     for node in nodeQry:
    #         log.debug("Checking Node {0}".format(node))
    #         nodeData = session.query(Data).filter_by(node_key = node.node_key).first()
    #         if nodeData is None:
    #             log.debug("--> Node has no data Deleting")
    #             #session.delete(node)
    #             deleteNodes.append(node.node_key)

    #     #Finally delete these nodes
    #     session.close()
    #     log.debug(deleteNodes)
    #     transaction.begin()
    #     session = self.makeSession()
    #     #session.query(Ar_Node).filter(Ar_Node.node_key.in_(deleteNodes)).delete()
    #     for item in deleteNodes:
    #         session.query(Ar_Node).filter_by(node_key = item).delete()
            
    #     session.flush()
    #     transaction.commit()
    #     session.close()
    # """

    # """"
    # def removeDupes(self):
    #     """Remove Duplicate Items"""
    #     print "Removing Dupes"

    #     from sqlalchemy.orm import aliased

    #     session = self.makeSession()

    #     t1 = time.time()

    #     a1 = aliased(Data)
    #     a2 = aliased(Data)

    #     query = session.query(a1,a2)
    #     query = query.filter(a1.datasource_key == a2.datasource_key)
    #     query = query.filter(a1.timestamp == a2.timestamp)
    #     query = query.filter(a1.data_key < a2.data_key)
    #     query = query.limit(10)
    #     #print "Count of Items ",query.count()
    #     #print query.limit(10).all()
        
    #     nodeIds = []
    #     for item in query.all():
    #         print "{0}\n{1}\n".format(item[0],item[1])
    #         nodeIds.append(item[0].data_key)

    #     query = session.query(Data).filter(Data.data_key.in_(nodeIds))
    #     for item in query.all():
    #         print item
        
    #     query = session.query(Data).filter(Data.data_key.in_(nodeIds))
    #     #delItems = query.delete()
    #     print "Total Deleted {0}".format(delItems)

    #     #nodeIds = [n.data_key for n in query.all()]
    #     #print "Node Id's Retrieved {0}".format(time.time()-t1)
        
    #     #query = session.query(Data)
    #     #query.filter(Data.data_key.in_(nodeIds))
    #     #delItems = query.delete()
    #     #print "Items Deleted ",delItems
    #     #transaction.begin()
    #     #for item in query:
    #     #    print item
    #     #    session.delete(item)

    #     #    print "{0}\n{1}\n".format(item[0],item[1])
    #     #query.delete()
    #     #session.flush()
    #     #transaction.commit()
    #     #session.close()


    #     t2 = time.time()
    #     print "Total Time Taken {0}".format(t2-t1)
    # """
           
    def csvData(self,theNode="Node1.1",theSensor="Temperature"):
        """Helper function, convert a given node and sensortype to a csv file"""
        log = self.log
        log.debug("{0} CSV'ing Data {0}".format("-"*20))
        session = self.makeSession()
        
        log.debug("--> Nodes <--")
        nodeQry = session.query(Ar_Node).filter_by(name = theNode).all()
        for item in nodeQry:
            log.debug("--> {0}".format(item))

        #Sensor types
        log.debug("--> Sensors <--")
        sensorQry = session.query(Source).filter_by(name=theSensor,
                                                    addr=nodeQry[0].addr).all()
        for item in sensorQry:
            log.debug("--> {0}".format(item))

        # #Finally Data

        loop = 0
        import time 

        import csv 
        import time
        writer = csv.writer(open("dbDump.csv","w"),delimiter="\t")

        sys.exit(0)
        for x in range(1):
            t1 = time.time()
            log.debug("Looping")
            dataQry = session.query(Data).filter_by(datasource_key = sensorQry[0].datasource_key).limit(100)
            dataQry = dataQry.all()
            t2 = time.time()
            
            log.debug("Writing")
            for item in dataQry:
                log.debug("{0}\t{1}".format(time.mktime(item.timestamp.timetuple()),item.value))
                writer.writerow([time.mktime(item.timestamp.timetuple()),item.value])
            
            log.debug("{0} Seconds Taken".format(t2-t1))
            loop += 1

        writer.close()  

    def getData(self):
        """Tester Function to Return some data"""
        session = self.makeSession()
        
        cutoffDate = datetime.datetime(2011,8,10)

        #query = session.query(Data).limit(10).all()
        #query = session.query(Source).limit(10).all()
        query = session.query(Ar_Node).filter(Ar_Node.node_created > cutoffDate).limit(10).all()
        #for item in query:
        #    log.debug(item)
        
        return query


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

        transaction.begin()
        #Connect any Sessions
        session = meta.DBSession()
        arSession = self.makeSession()
        
        # #Check for and Create the Deployment
        depQry = session.query(models.deployment.Deployment).filter_by(name=deploymentName).first()
        if depQry is None:
            theDeployment = models.deployment.Deployment(name=deploymentName)
            status["newDep"] = True
            session.add(theDeployment)
            session.flush()
            log.info("New Deployment Created {0}".format(theDeployment))
            
        else:
            log.info("Using Existing Deployment {0}".format(depQry))
            status["newDep"] = False
            theDeployment = depQry

        sampleTable = models.sample.Sample

        
        status["deployment"] = theDeployment
        
        # #Next thing to do is to add all the Nodes but as the AR database is a little arse about face.
        # We need to do some trickery here.

        # Find the Nodes
        arNodes = arSession.query(Ar_Node)
        #if startDate:
        #    arNodes = arNodes.filter(Ar_Node.node_created >= startDate)
        #if endDate:
        #    arNodes = arNodes.filter(Ar_Node.node_created <= endDate)
        
        #I want to add a quick filter here for testing
        #arNodes = arNodes.filter_by(name = "Node1")
        arNodes = arNodes.all()

        #To Hold all our nodes and sensors
        nodeDict = {}
        nodeIdDict = {}
        addrDict = {}
        sensorDict = {}
        sensorTypes = self.sensorTypes

        #Node / Sensors Pairs
        nodePairs = {}
    
        sensorData = {}
        print "Finding Nodes"
        for node in arNodes:
            print node
            #Do we already know about this node
            theNode = nodeDict.get(node.addr,None)
            if not theNode:
                #Check it does not already exist in the database
                theQry = session.query(models.nodes.Node).filter_by(deploymentId = theDeployment.Id,
                                                                    name=node.name,
                                                                    serialNo = node.addr)

                theQry = theQry.first()
                    
                if theQry is None:
                    theNode = models.nodes.Node(deploymentId = theDeployment.Id,
                                                name=node.name,
                                                serialNo = node.addr)
                    log.info("Node {0} not in Database".format(theNode))
                    nodePairs[node.addr] = []
                    
                else:
                    theNode = theQry
                    log.info("Node {0} Exists ({1})".format(theNode,type(theNode)))
                
                #session.flush()

                nodeDict[node.addr] = theNode            
                addrDict[node.addr] = [node.node_key]
                #theAddr = addrDict.get(node.addr,[])
                #theAddr.append(node.node_key)
                #addrDict[node.addr] = theAddr
            else:
                #log.debug("Dictonary Entry Exists for {0}".format(node))
                addrDict[node.addr].append(node.node_key)

            nodeIdDict[node.node_key] = theNode

        #We should also check if the node has any data attached to it before saving it in the database
        
        for nodeAddr,nodeId in addrDict.iteritems():
            #log.debug("Id: {0} Item: {1}".format(nodeAddr,nodeId))
            #Check if the data Exists

            sensorQry = arSession.query(Source.datasource_key)
            sensorQry = sensorQry.filter_by(addr = nodeAddr,
                                            source="Temperature")
            #log.debug(sensorQry.all())

            theQuery = arSession.query(Data)
            theQuery = theQuery.filter(Data.node_key.in_(nodeId))
            #log.debug("Sensor Query {0}".format(sensorQry))
            theQuery = theQuery.filter(Data.datasource_key.in_(sensorQry))
        
            if startDate:
                theQuery = theQuery.filter(Data.timestamp >= startDate)
            if endDate:
                theQuery = theQuery.filter(Data.timestamp <= endDate)

            

            #And Filter by the known sensor types
            

            #theQuery = theQuery.limit(10)
            cnt = theQuery.first()
            log.debug("Item {1} Has Data {0} ".format(cnt,nodeDict[nodeAddr]))

            if cnt is None:
                log.warning("Node {0} Has no Data".format(nodeDict[nodeAddr]))
                del nodeDict[nodeAddr]
            else:
                status['nodes'].append(nodeDict[nodeAddr])
                session.add(nodeDict[nodeAddr])

        #log.debug("New Dict")
        #for addr,node in nodeDict.iteritems():

        #And Add Sensors
        for node in arNodes:
            theNode = nodeDict.get(node.addr,None)
            if theNode:
                #log.debug("#"*40)
                #log.info("Finding sensors for node: {0} ({1})".format(node,theNode))

                #Find any sensors attached to this node
                arSensors = arSession.query(Source).filter_by(addr = node.addr)
                #Strip out meta sensors like voltage
                arSensors = arSensors.filter(Source.source.in_(ALLOWED_TYPES))
                arSensors = arSensors.all()
                
                #Check and Add to Database
                #log.debug("=== Sensors ===")

                for sensor in arSensors:                                     
                    #Check if we know about this Sensor
                    theSensor = sensorDict.get(sensor.datasource_key,None)
                    #log.debug("--> Sensor {0} --> Dictonary {1}".format(sensor,theSensor))

                    if not theSensor:
                        #Check Database
                        #log.debug("Sensor Name {0}".format(sensor.name))
                        sName = sensor.name
                        if sName == "CO2":
                            sName = "Co2"
                        sType = sensorTypes[sName]
                        theQry = session.query(models.sensor.Sensor).filter_by(nodeId = theNode.Id,
                                                                               sensorTypeId = sType.Id)
                        theQry = theQry.first()

                        if theQry is None:
                            thisSensor = models.sensor.Sensor(nodeId = theNode.Id,
                                                              sensorTypeId = sType.Id,
                                                              name = sName)

                            session.add(thisSensor)
                            log.debug("--> Checking Database for sensor {0}: Adding Sensor".format(theQry))
                        else:
                            thisSensor = theQry

                        sensorDict[sensor.datasource_key] = thisSensor


                    #log.debug("--> Copied Sensor {0}".format(thisSensor))
                                
        
        status["nodes"] = nodeDict.values()
        status["sensors"] = sensorDict.items()
        #return status
        
        log.debug("{0} Sensors {0}".format("-"*20))
        for key,item in sensorDict.iteritems():
            log.debug("{0} {1}".format(key,item))
                 
        
        #The Final thing is to fetch and store all the data.
        dataQuery = arSession.query(Data)

        #if not nodeIdDict:
        #    log.warning("No Node ID's")
        dataQuery = dataQuery.filter(Data.node_key.in_(nodeIdDict.keys()))
        #if not sensorDict:
        #    log.warning("No Sensor ID's")
        dataQuery = dataQuery.filter(Data.datasource_key.in_(sensorDict.keys()))
        
        
        log.debug("Removing previous data")
        #deleteQuery = dataQuery.all().delete()
        #log.debug("{0} Items removed".format(deleteQuery))
        #sys.exit(0)


        if startDate:
            dataQuery = dataQuery.filter(Data.timestamp >= startDate)
        if endDate:
            dataQuery = dataQuery.filter(Data.timestamp <= endDate)

        
        #dataQuery = dataQuery.order_by(Data.timestamp)

        #Data Cacheing to help on updates
        datacache = []
        tempDict = {}
        cacheindex = 0
        cachelimit = 144 #About 12 hours worth of data
        #cachelimit = 144
        setIdx = 0

        currentOffset = 0
        transferLimit = 100

        #t1 = time.time()
        log.info("Counting Rows")
        #theCount = dataQuery.count()
        #log.info("{0} Rows Found".format(theCount))
        #t2 = time.time()
        #log.debug("{0} Seoconds Taken".format(t2-t1))


        #log.info("Fetching {0} Rows".format(dataQuery.count()))
        

        #for dataItem in dataQuery.limit(100):
        #    if currentOffset > transferLimit:
        #        log.debug("Records Stored")
        #    currentOffset += 1

        tempStore = []
        dataQuery = dataQuery
        sampleList = []
        sampleCount = 0
        maxSamples = 1000 #Items before a commit
        loopIndex = 0
        dataQuery = dataQuery.limit(5000).offset(1000000)
        log.info("Starting to save Data")
        for dataItem in dataQuery.yield_per(1000):
            transaction.begin()
            sensorId = sensorDict[dataItem.datasource_key]

            thisSample = sampleTable(sensorId = sensorId.Id,
                                         timestamp = dataItem.timestamp,
                                         value = dataItem.value)

            sampleList.append(thisSample)

            if sampleCount > maxSamples:
                log.debug("Saving items {0}".format(loopIndex))
                loopIndex += 1
                session.add_all(sampleList)

                try:
                    session.flush()
                    transaction.commit()
                except sqlalchemy.exc.IntegrityError,e:
                    session.rollback()
                    log.warning("Some Error {0}".format(e))
                    for mergeItem in sampleList:
                        session.merge(mergeItem)
                        session.flush()
                        transaction.commit()

                sampleList = []
                sampleCount = 0

            sampleCount += 1
        

        

            


#            print item
        #for item in dataQuery.yield_per(5):
        #    print item
        
        log.info("Samples Stored, Summarising")
        status["nodes"] = nodeDict.values()
        status["sensors"] = sensorDict.items()
        
        return status

        while True:
            transaction.begin()
            thisQuery = dataQuery.limit(transferLimit).offset(currentOffset)


            theData = thisQuery.all()
            log.debug("Iteration {0}: {1}".format(currentOffset,theData[0]))
            if theData is None:
                log.info("Reached end of values")
                break
        
            currentOffset += transferLimit
            sampleList = []
            for dataItem in theData:
                sensorId = sensorDict[dataItem.datasource_key]

                if sensorId is None:
                    log.warning("Error Fetching Id for {0}".format(dataItem))

                thisSample = sampleTable(sensorId = sensorId.Id,
                                         timestamp = dataItem.timestamp,
                                         value = dataItem.value)

                sampleList.append(thisSample)

            #Test if we have samples for this
            #thisSample = sampleList[0]
            #theQry = session.query(sampleTable).filter_by(sensorId = thisSample.sensorId,
            #                                              timestamp = thisSample.timestamp)
            #hasData = theQry.first()
            hasData = False
            if hasData:
                log.warning("Readings Exists {0}".format(thisSample))
            else:
                session.add_all(sampleList)

            try:
                session.flush()
                transaction.commit()
            except sqlalchemy.exc.IntegrityError,e:
                session.rollback()
                #transaction.rollback()
                transaction.begin()
                log.warning("Some Error {0}".format(e))
                for mergeItem in sampleList:
                    session.merge(mergeItem)
                    
                session.flush()
                transaction.commit()
        
        


        # summarise(theDeployment.Id)
        # log.info("Upload Complete")
        # #And Run a summary for this 
        # node.summariseData(theDeployment.Id)
        return status


def runUpload(request):
    outDict = {}
    outDict["mainLinks"] = general.genUrls(request)
    outDict["subLinks"] = general.genSecondUrls(request)

    outDict["pgTitle"] = "Upload Data"


    #This Stuff Can Come from a Form
    #depName =  "30Newdigate"
    dbName = "rooftopnibe"
    depName = "RooftopNibe"
    #depName = "227Foleshill"
    stDate = datetime.datetime(2011,10,1)
    

    theDb = ArchRockDB(database = dbName)
    #theDb.getData()

    status = theDb.transferData(depName,stDate)
    outDict["status"] = status
    return render_to_response('orbit_viewer:templates/uploadAr.mak',
                              outDict,
                              request=request)


class CSVParser(object):
    """
    Parse Data from one of the CSV files suppied by Ross
    """
    def __init__(self,theFile):
        """
        Initialise the Parser
        @param theFile: File to take data from
        """
        self.log = logging.getLogger("Arch Rock")
        self.log.setLevel(logging.DEBUG)
        log = self.log
        log.debug("Creating Arch Rock File Parser")

        reader = csv.reader(open(theFile,"r"),delimiter="\t")
        self.reader = reader

    def createNodes(self,deploymentName):
        """Create or retrieve the relevant nodes and Sensors
        from the database
        """
        log = self.log
        session = meta.DBSession()
        #transaction.begin()
        qry = session.query(models.deployment.Deployment).filter_by(name=deploymentName).first()

        if not qry:
            log.debug("No such Deployment")
            theDeployment = models.deployment.Deployment(name=deploymentName)

            session.add(theDeployment)
        else:
            log.debug("Using Existing Deployment {0}".format(qry))
            theDeployment = qry

        self.theDeployment = theDeployment


        #Now load all the relevant sensor types
        sensorTypes = session.query(models.sensor.SensorType).all()

        sensorDict = {}
        for item in sensorTypes:
            sensorDict[item.sensor_type] = item.Id

        self.sensorDict = sensorDict

        #transaction.commit()

    def parseHeader(self):
        """Parse the header to get all the relevant nodes"""

        log = self.log
        theHead = self.reader.next()
        log.debug(theHead)
        sensorList = []
        nodeDict = {}
        
        session = meta.DBSession()
        deployId = self.theDeployment.Id

        sensorType = {}
        theQry = session.query(models.sensor.SensorType).filter_by(name="Arch Rock").all()
        for item in theQry:
            sensorType[item.sensor_type] = item
            

        for idx in range(len(theHead)):
            item = theHead[idx]
            log.debug("Parsing {0} {1}".format(idx,item))
            if item == "Time":
                log.debug("--> Time Stamp Ignoring")
                sensorList.append(item)
            else:
                #Split into Node Name and Id
                nName,nType = item.split(".")
                log.debug("--> Node Name {0} Type {1}".format(nName,nType))

                #check if we know about this node
                theNode = nodeDict.get(nName,None)
                if theNode is None:
                    #Check DB and add if necessary
                    theQry = session.query(models.nodes.Node).filter_by(name = nName,
                                                                        deploymentId = deployId)
                    theQry = theQry.first()
                    if theQry is None:

                        theNode = models.nodes.Node(deploymentId = deployId,
                                                    name = nName)
                        session.add(theNode)
                        log.debug("--> Creating Node {0}".format(theNode))
                    else:
                        theNode = theQry
                        log.debug("--> Using DB Node {0}".format(theNode))
                    nodeDict[nName] = theNode
                else:
                    log.debug("--> Using Stored Node")
                        
                #And then the Sensor
                if nType == "H":
                    sType = sensorType["Humidity"]
                elif nType == "T":
                    sType = sensorType["Temperature"]
                elif nType == "C":
                    sType = sensorType["Co2"]
                else:
                    logging.warning("NO SUCH SENSOR {0}".format(nType))
                    import sys
                    sys.exit(0)                    
 
                
                #Check if that Exists
                theQry = session.query(models.sensor.Sensor).filter_by(nodeId = theNode.Id,
                                                                       sensorTypeId = sType.Id).first()

                if theQry is None:
                    theSensor = models.sensor.Sensor(nodeId = theNode.Id,
                                                     sensorTypeId = sType.Id,
                                                     name= item)
                    session.add(theSensor)
                else:
                    theSensor = theQry

                #And Append to the List so we know where we are
                sensorList.append(theSensor)

        #Final Debuggy Stuff
        #for item in sensorList:
        #    print item
        self.sensorList = sensorList
                    
    def parseData(self):
        log = self.log
        reader = self.reader
        sensorList = self.sensorList
        outData = []
        #for x in range(2):
        #    row = reader.next()
        for row in reader:
            #log.debug(row)
            
            timestamp = datetime.datetime.fromtimestamp(float(row[0]))
            #log.debug("--> Time {0}".format(timestamp))
            for idx in range(1,len(row)):
                reading = float(row[idx])
                theValue = models.sample.Sample(timestamp = timestamp,
                                                value = reading,
                                                sensorId = sensorList[idx].Id)
                                                
                #log.debug("Val {0} Sample {1}".format(row[idx],theValue))
                outData.append(theValue)

        self.outData = outData

    def transferData(self,deploymentName,startDate=None,endDate=None):
        """Transfer Data between the file and the main database
        """
        log = self.log

        transaction.begin()
        self.createNodes(deploymentName)
        self.parseHeader()
        #session = meta.DBSession()
        
        self.parseData()

        #Then Save everything
        session = meta.DBSession()
        log.debug("Deleting Existing Data")
        for item in self.sensorList[1:]:
            theQry = session.query(models.sample.Sample).filter_by(sensorId = item.Id).delete()

        session.flush()
        log.debug("Adding New Data")
        session.add_all(self.outData)
        session.flush()
        log.debug("Summarising")
        summarise(self.theDeployment.Id)            

        log.debug("Done")
        transaction.commit()



        
        
        
if __name__ == "__main__":
    """Run from command line"""
    from pyramid.paster import bootstrap
    env = bootstrap('../../development.ini')
    print env['request'].route_url('home')

    import logging.config
    logging.config.fileConfig("../../development.ini")



    #theFile = "/home/dang/DeploymentData/119Jodrell/119jodrellEnvironment.csv"
    #foo = CSVParser(theFile)
    #foo.transferData("119Jodrell")
    #log.debug("Running")
    
    #Connect to the Arch Rock Database
    #runUpload(env['request'])

    #theDb = ArchRockDB(address="192.168.69.3")
    #theDb = ArchRockDB(database="227Foleshill")
    print "{0} Tables {0}".format("-"*20)
    #theDb.listTables()
    #theDb.listNodes()
    #theDb.cleanData()
    #theDb.removeDupes()
    #theDb.csvData("Kitchen","Temperature")
    #theDb = ArchRockDB(database="227Foleshill")
    #theDb.listTables()

    #stDate = datetime.datetime(2011,7,22)
    #theDb.transferData("227Foleshill",stDate)
    
