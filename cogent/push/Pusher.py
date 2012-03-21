import logging
logging.basicConfig(level=logging.DEBUG)


import sqlalchemy
import remoteModels

import cogent
import cogent.base.model as models
import cogent.base.model.meta as meta
import datetime
import subprocess

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class Pusher(object):
    """Class to push updates to a remote database.

    .. warning::
    
        This will fail if the database type is SQLite, currently a connection cannot issue a
        statement while another is open.  Therefore the loop through the readings, appending new items 
        fails with a DATABASE LOCKED error.

        I am at a loss of what to do to fix this.
        However, as we will be pushing to mySQL, its not really a problem except for some test cases
        
    .. note::
    
        I currently add 1 second to the time the last sample was transmitted,  
        this means that there is no chance that the query to get readings will return an
        item that has all ready been synced, leading to an integrity error.

        I have tried lower values (0.5 seconds) but this pulls the last synced item out, 
        this is possibly a error induced by mySQL's datetime not holding microseconds.
        

    """
    def __init__(self):
        pass

    def initRemote(self,remoteUrl):
        """Initialise a connection to the database and reflect all Remote Tables

        :param remoteUrl:  a :class:`models.remoteURL` object that we need to connect to
        """
        log.debug("Initialising Remote Engine")
        RemoteSession = sqlalchemy.orm.sessionmaker()

        self.rUrl = remoteUrl

        #Put up an ssh tunnel
        #theProcess = subprocess.Popen("ssh -L 3308:localhost:3307 dang@127.0.0.1",
         #                             shell=True,
          #                            close_fds=True)

        #self.theProcess = theProcess        

        engine = sqlalchemy.create_engine(remoteUrl.dburl)
        RemoteSession.configure(bind=engine)
        RemoteMetadata = sqlalchemy.MetaData()
        
        
        log.debug("Reflecting Remote Tables")
        remoteModels.reflectTables(engine,RemoteMetadata)
        self.RemoteSession=RemoteSession
        

    def initLocal(self,engine):
        """Initialise a local connection"""
        log.debug("Initialising Local Engine")
        models.initialise_sql(engine)
        LocalSession = sqlalchemy.orm.sessionmaker(bind=engine)
        self.LocalSession = LocalSession


    def testRemoteQuery(self):
        """
        Return all room types in our remote object (Test Method)
        """
        session = self.RemoteSession()
        theQry = session.query(remoteModels.RoomType)
        return theQry.all()

    def testLocalQuery(self):
        """
        Return all room types in our local object (Test Method)
        """
        session = self.LocalSession()
        theQry = session.query(models.RoomType)
        return theQry.all()

    def checkNodes(self):
        """
        Does the nodes in the remote database need syncing.

        :return: A list of node objects that need synchronising
        """
        lSess = self.LocalSession()
        rSess = self.RemoteSession()

        #Get the Nodes we Know about on the Remote Connection
        rQry = rSess.query(remoteModels.Node.id)

        #As the above query returns a list of tuples then we need to filter that down
        rQry = [x[0] for x in rQry]

        #Normally we would just issue a query, but having a empty query._in(<array>) 
        #Will issue a SQL statement.  Therefore have a guard here to keep DB activity
        #To a minimum
        if rQry:
            lQry = lSess.query(models.Node).filter(~models.Node.id.in_(rQry)).all()
        else:
            lQry = []
        
        log.info("Nodes requiring sync: {0}".format(lQry))
        return lQry

    def syncNodes(self,syncNodes=False):
        """
        Synchronise the nodes in the remote and local databases
        It is expected that this method takes the output of the :func:`checkNode` function 
        Synchronising these nodes with the remote database
        
        If no list of nodes to synchronise is provided, then the function calls
        :func:`checkNodes` to get a list of nodes to operate on

        Basic operation is 

        #.  Synchronise Nodes
        #.  Ensure that any new nodes have the correct location.
        #.  Ensure that the Node has the correct sensors attached to it.

        .. note::
         
            This does not synchronise the sensor type id.
            As this table does not appear to be used currently.

        :param syncNodes: The Nodes to Synchronise
        :return: True is the Sync is successful
        """
        rSess = self.RemoteSession()
        lSess = self.LocalSession()

        if not syncNodes:
            syncNodes = self.checkNodes()

        #Create the Remote Connection
        for node in syncNodes:
            log.info("--> Sync Node {0} with remote database".format(node))
            node = lSess.query(models.Node).filter_by(id=node.id).first()
            #First we need to create the node itself
            newNode = remoteModels.Node(id=node.id)
            rSess.add(newNode)
            rSess.flush()
            newLocation = self.syncLocation(node.locationId)
            newNode.locationId = newLocation.id
            rSess.flush()
            for sensor in node.sensors:
                log.debug("--> --> Sync Sensor {0}".format(sensor))
                #We shouldn't have to worry about sensor types as they should be global
                newSensor = remoteModels.Sensor(sensorTypeId=sensor.sensorTypeId,
                                                nodeId = newNode.id,
                                                calibrationSlope = sensor.calibrationSlope,
                                                calibrationOffset = sensor.calibrationOffset)
                rSess.add(newSensor)
                rSess.flush()
            #Finally we also need to synchronise locations
  
        rSess.commit()
        rSess.close()

    def syncLocation(self,locId):
        """Code to Synchronise Locations

        Locations are a combination of Rooms/Houses
        
        # Check we have a room of this (name/type) in the remote databases (Create)
        # Check we have a house of this (name/deployment) in the remote (Create)
        # Check we have a location with these parameters (create)

        :param locId: LocationId to Synchronise
        :return Equivalent Location Id in the Remote Database
        """
        lSess = self.LocalSession()
        rSess = self.RemoteSession()

        theLocation = lSess.query(models.Location).filter_by(id=locId).first()
        log.debug("{2} Synchronising Location ({0}) {1} {2}".format(locId,theLocation,"="*10))

        #This is a little unfortunate, but I cannot (without over complicating reflection) 
        #Setup backrefs on the remote tables this should be a :TODO:
        #So We need a long winded query

        localRoom = theLocation.room
        remoteRoom = rSess.query(remoteModels.Room).filter_by(name=localRoom.name).first()
        if remoteRoom is None:
            log.debug("--> No Such Room {0}".format(localRoom.name))

            localRoomType = localRoom.roomType
            log.debug("--> Local Room Type {0}".format(localRoomType))
            #We also cannot assume that the room type will exist so we need to check that
            roomType = rSess.query(remoteModels.RoomType).filter_by(name=localRoomType.name).first()
            if roomType is None:
                log.debug("--> --> No Such Room Type {0}".format(theLocation.room.roomType.name))
                roomType = remoteModels.RoomType(name=theLocation.room.roomType.name)
                rSess.add(roomType)
                rSess.flush()

            remoteRoom = remoteModels.Room(name=theLocation.room.name,
                                           roomTypeId = roomType.id)

            rSess.add(remoteRoom)
            rSess.flush()

        rSess.commit()
        log.debug("Remote Room is {0}".format(remoteRoom))
        remoteRoomId = remoteRoom.id


        #Then Check the House

        remoteHouse = rSess.query(remoteModels.House).filter_by(deploymentId = theLocation.house.deploymentId,
                                                                address = theLocation.house.address).first()
        if remoteHouse is None:
            #Check the Deployment Exists
            remoteDeployment = rSess.query(remoteModels.Deployment).filter_by(name=theLocation.house.deployment.name).first()
            if not remoteDeployment:
                remoteDeployment = remoteModels.Deployment(name=theLocation.house.deployment.name,
                                                           description = theLocation.house.deployment.description,
                                                           startDate = theLocation.house.deployment.startDate,
                                                           endDate = theLocation.house.deployment.endDate)
                rSess.add(remoteDeployment)
                rSess.flush()
            
            remoteHouse = remoteModels.House(address=theLocation.house.address,
                                             deploymentId=remoteDeployment.id)
            rSess.add(remoteHouse)
            rSess.flush()
            
        rSess.commit()
        log.debug("--> Remote House is {0}".format(remoteHouse))


        remoteHouseId = remoteHouse.id
        remoteLocation = rSess.query(remoteModels.Location).filter_by(houseId = remoteHouseId,
                                                                      roomId=remoteRoomId).first()

        log.debug("--> DB Remote Location {0}".format(remoteLocation))
        rSess.flush()
        if not remoteLocation:
            remoteLocation = remoteModels.Location(houseId=remoteHouseId,
                                                   roomId = remoteRoomId)
            rSess.add(remoteLocation)
            log.debug("Adding New Remote Location")
            
        log.debug("--> Remote Location is {0}".format(remoteLocation))
        rSess.commit()
        return remoteLocation
        pass

    def syncReadings(self,cutTime=None):
        """Synchronise readings between two databases

        :param DateTime cutTime: Time to start the Sync from

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

        # If Sync is successful, fix the last update timestamp.

        Additionally we need to Sync the Node-State Table


        
        """

        lSess = self.LocalSession()
        session = self.RemoteSession()

        log.info("Synchronising Readings")

        #Time stamp to check readings against
        if not cutTime:
            rUrl = self.rUrl
            lastUpdate = lSess.query(models.UploadURL).filter_by(url=self.rUrl.url).first()
            log.info("--> Time Query {0}".format(lastUpdate))

            if lastUpdate:
                cutTime = lastUpdate.lastUpdate
            else:
                cutTime = None
                  
        #Get the Readings
        readings = lSess.query(models.Reading).order_by(models.Reading.time)
        if cutTime:
            log.info("Filter all readings since {0}".format(cutTime))
            readings = readings.filter(models.Reading.time >= cutTime)

        log.info("Total Readings to Sync {0}".format(readings.count()))
        
        readings = list(readings.all())
        #Init Temp Storage
        locationStore = {}
        newReading = None
        for reading in readings:  
            #print reading
            mappedLoc = locationStore.get(reading.locationId,None)
            #Check if we have the location etc
            if mappedLoc is None:
                mapId = self.syncLocation(reading.locationId)
                #And update the nodes Location
                if not mapId.id:
                    log.warning("Error Creating Location {0}".format(reading.locationId))
                    sys.exit(0)
                                
                locationStore[reading.locationId] = mapId
            #Otherwise, We should just be able to sync the Reading
            newReading = remoteModels.Reading(time = reading.time,
                                              nodeId = reading.nodeId,
                                              type = reading.typeId,
                                              locationId = mapId.id,
                                              value = reading.value)
                     
            session.add(newReading)
            session.commit()

        if newReading is None:
            #If we had no data to update
            return

        log.info("Last Reading Added Was {0}".format(newReading))

        try:
            session.flush()
            session.commit()
            #Update the Local Time stamp
            newUpdate = lSess.query(models.UploadURL).filter_by(url=self.rUrl.url).first()
            #Add a bit of jitter otherwise we end up getting the same reading.
            newUpdate.lastUpdate = newReading.time + datetime.timedelta(seconds = 1)
            lSess.flush()
            lSess.commit()
            log.info("Commit Successful Last update is {0}".format(newUpdate))
        except Exception, e:
            log.warning("Commit Fails {0}".format(e))
        

        lSess.close()
        session.close()
        # pass

    def syncState(self,cutTime=None):
        """
        Synchronise any node state information

        Currently this just syncronises the node state table based on a given start date.
        Actually this is pretty easy, as our constaints on unique node names mean that 
        We dont have to do any error checking.


        :param DateTime startTime: Time to start filtering the states from
        """
        lSess = self.LocalSession()
        session = self.RemoteSession()

        #Find out what time we need to update from
        # rUrl = self.rUrl
        # lastUpdate = lSess.query(models.UploadURL).filter_by(url=self.rUrl.url).first()
        # log.info("--> Time Query {0}".format(lastUpdate))

        # if lastUpdate:
        #     cutTime = lastUpdate.lastUpdate
        # else:
        #     cutTime = None

        nodeStates = lSess.query(models.NodeState).order_by(models.NodeState.time)
        log.info("Total Nodestates {0}".format(nodeStates.count()))
        if cutTime:
            log.info("Filter all nodeStates since {0}".format(cutTime))
            nodeStates = nodeStates.filter(models.NodeState.time >= cutTime)

        log.info("Total NodeStates to Sync {0}".format(nodeStates.count()))
                  
        for item in nodeStates:
            newState = remoteModels.NodeState(time=item.time,
                                              nodeId = item.nodeId,
                                              parent = item.parent,
                                              localtime = item.localtime)
            session.add(newState)
        session.flush()
        session.commit()


if __name__ == "__main__":
    logging.debug("Testing Push Classes")
    
    
    remoteEngine = sqlalchemy.create_engine("sqlite:///remote.db")
    localEngine =  sqlalchemy.create_engine("sqlite:///test.db")

    push = Pusher()
    push.initRemote(remoteEngine)
    push.initLocal(localEngine)
    push.testRemoteQuery()
    push.testLocalQuery()
    pass
