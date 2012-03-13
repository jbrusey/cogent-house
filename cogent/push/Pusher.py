import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
#log.setLevel(logging.WARNING)

import sqlalchemy
import remoteModels

import cogent
import cogent.base.model as models
import cogent.base.model.meta as meta
#RemoteSession = sqlalchemy.orm.sessionmaker()
#RemoteMetadata = sqlalchemy.MetaData()

class Pusher(object):
    """Class to push updates to a remote database"""
    def __init__(self):
        pass

    def initRemote(self,remoteUrl):
        """Intialise a connection to the database and reflect all Remote Tables

        :param remoteUrl:  a :class:`models.remoteURL` object that we need to connect to
        """
        log.debug("Initalising Remote Engine")
        RemoteSession = sqlalchemy.orm.sessionmaker()

        self.rUrl = remoteUrl
        engine = sqlalchemy.create_engine(remoteUrl.dburl)
        RemoteSession.configure(bind=engine)
        RemoteMetadata = sqlalchemy.MetaData()
        
        
        log.debug("Reflecting Remote Tables")
        remoteModels.reflectTables(engine,RemoteMetadata)
        self.RemoteSession=RemoteSession
        

    def initLocal(self,engine):
        """Initalise a local connection"""
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

        :return: False if no synch is needed, otherwise a list of node objects that need synhronising
        """
        lSess = self.LocalSession()
        rSess = self.RemoteSession()

        log.debug("{0} Checking Nodes {0}".format("#"*20))
        #Get the Nodes we Know about on the Remote Connection
        rQry = rSess.query(remoteModels.Node.id)

        #As the above query returns a list of tuples then we need to filter that down
        rQry = [x[0] for x in rQry]

        log.debug("Remote Items {0}".format(rQry))
        if rQry:
            lQry = lSess.query(models.Node).filter(~models.Node.id.in_(rQry)).all()

            return lQry
        else:
            return False

    def syncNodes(self,syncNodes=False):
        """
        Synchronise the nodes in the remote and local databases
        It is expected that this method takes the output of the :func:`checkNode` function 
        Synchonising these nodes with the remote database
        
        If no list of nodes to synchronise is provided, then the function calls
        :func:`checkNodes` to get a list of nodes to opperate on

        Basic opperation is 

        #.  Synchronise Nodes
        #.  Ensure that the Node has the correct sensors attached to it.

        .. note::
         
            This does not sycnronsie the sensor type id.
            As this table does not appear to be used currently.

        :param syncNodes: The Nodes to Synchronse
        :return: True is the Sync is successfull
        """
        rSess = self.RemoteSession()
        lSess = self.LocalSession()

        if not syncNodes:
            syncNodes = self.checkNodes()

        #Create the Remote Connection
        log.debug("{0} Synchronising Nodes {0}".format("="*30))
        for node in syncNodes:
            log.debug("--> Synching Node {0}".format(node))
            node = lSess.query(models.Node).filter_by(id=node.id).first()
            #First we need to create the node itself
            newNode = remoteModels.Node(id=node.id)
            rSess.add(newNode)

            newLocation = self.syncLocation(node.locationId)
            newNode.locationId = newLocation.id
            
            log.debug("--> SYNCHING SENSORS")
            for sensor in node.sensors:
                log.debug("--> --> Adding Sensor {0}".format(sensor))
                #We shouldnt have to worry about sensor types as they should be global
                newSensor = remoteModels.Sensor(sensorTypeId=sensor.sensorTypeId,
                                                nodeId = newNode.id,
                                                calibrationSlope = sensor.calibrationSlope,
                                                calibrationOffset = sensor.calibrationOffset)
                rSess.add(newSensor)
                rSess.flush()
            #Finally we also need to synchonise locations

  
        rSess.commit()

    def syncLocation(self,locId):
        """Code to Synchonise Locations

        Locations are a combination of Rooms/Houses
        
        # Check we have a room of this (name/type) in the remote databases (Create)
        # Check we have a house of this (name/deployment) in the remote (Create)
        # Check we have a location with these paramters (create)

        :param locId: LocationId to Synchronise
        :return Equivelent Location Id in the Remote Database
        """
        lSess = self.LocalSession()
        rSess = self.RemoteSession()

        theLocation = lSess.query(models.Location).filter_by(id=locId).first()
        log.debug("Synchonising Location ({0}) {1}".format(locId,theLocation))

        #This is a little unfortunate, but I cannot (without over complicating reflection) 
        #Setup backrefs on the remote tables this should be a :TODO:
        #So We need a long winded query

        remoteRoom = rSess.query(remoteModels.Room).filter_by(name=theLocation.room.name).first()
        if remoteRoom is None:
            log.debug("--> No Such Room {0}".format(theLocation.room.name))

            #We also cannot assume that the room type will exist so we need to check that
            roomType = rSess.query(remoteModels.RoomType).filter_by(name=theLocation.room.roomType.name).first()
            if roomType is None:
                log.debug("--> --> No Such Room Type {0}".format(theLocation.room.roomType.name))
                roomType = remoteModels.RoomType(name=theLocation.room.roomType.name)
                rSess.add(roomType)
                rSess.flush()
            remoteRoom = remoteModels.Room(name=theLocation.room.name,
                                           roomTypeId = roomType.id)

            rSess.add(remoteRoom)
            rSess.flush()
        log.debug("Remote Room is {0}".format(remoteRoom))
            
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
                                             

        log.debug("--> Remote House is {0}".format(remoteHouse))
        #It is 
        
        remoteLocation = rSess.query(remoteModels.Location).filter_by(houseId = remoteHouse.id,
                                                                      roomId=remoteRoom.id).first()

        if not remoteLocation:
            remoteLocation = remoteModels.Location(houseId=remoteHouse.id,
                                                   roomId = remoteRoom.id)
            rSess.add(remoteLocation)
            rSess.flush()
            
        log.debug("--> Remote Location is {0}".format(remoteLocation))
        rSess.commit()
        return remoteLocation
        pass

    def syncReadings(self):
        """Syncronse readings between two databases

        This assumes that Sync Nodes has been called.

        The Algorithm for this is:

        Initialise Temproray Storage, (Location = {})
        
        #. Get the time of the most recent update from the local database
        #. Get all Local Readings after this time.
        #. For Each Reading

            #. If !Location in TempStore:
                #. Add Location()
            #. Else:
                #. Add Sample

        Additionally we need to Sync the NodeState Table
        
        """

        lSess = self.LocalSession()
        session = self.RemoteSession()

        log.debug("Synchonising Readings")

        #Timestamp to check readings against
        #cutTime = self.rUrl.lastUpdate
        rUrl = self.rUrl
        log.debug("--> rURL {0}".format(self.rUrl))
        #log.debug("Cut Off Time {0}".format(cutTime))
        lastUpdate = lSess.query(models.UploadURL).filter_by(url=self.rUrl.url).first()
        log.debug("--> Time Query {0}".format(lastUpdate))
        if lastUpdate:
            cutTime = lastUpdate.lastUpdate
        else:
            cutTime = None
        log.debug("Last Update {0}".format(cutTime))
                 
        #Get the Readings
        readings = lSess.query(models.Reading).order_by(models.Reading.time)
        if cutTime:
            
            readings = readings.filter(models.Reading.time >= cutTime)

        log.debug("Total Readings to Synch {0}".format(readings.count()))
        
        #Init Temp Storage
        locationStore = {}
        for reading in readings:
            
            mappedLoc = locationStore.get(reading.locationId,None)
            #Check if we have the location etc
            if mappedLoc is None:
                mapId = self.syncLocation(reading.locationId)
                if not mapId:
                    log.warning("Error Creating Location {0}".format(reading.locationId))
                    return False
                                
                locationStore[reading.locationId] = mapId
            #Otherwise, We should just be able to sync the Reading
            newReading = remoteModels.Reading(time = reading.time,
                                              nodeId = reading.nodeId,
                                              type = reading.typeId,
                                              locationId = mapId.id,
                                              value = reading.value)
                     
            session.add(newReading)
            #log.debug("ProcessingReading {0} -> {1}".format(reading,newReading))
            #session.flush()
            #session.commit()
        #This should be the last Sample


        log.debug("Last Reading Added Was {0}".format(newReading))

        try:
            session.flush()
            session.commit()
            log.info("Commit Successfull")
            #Update the Local Timestamp
            newUpdate = lSess.query(models.UploadURL).filter_by(url=self.rUrl.url).first()
            newUpdate.lastUpdate = newReading.time
            lSess.flush()
            lSess.commit()
            log.info("Commit Successfull Last update is {0}".format(newUpdate))
        except Exception, e:
            log.warning("Commit Fails {0}".format(e))
            self.rUrl.lastUpdate = newReading.time
            session.flush()
            session.commit()
        
        lSess.close()
        session.close()
        # pass


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
