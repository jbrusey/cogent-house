import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

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

        log.debug("\n{0} Checking Nodes {0}".format("#"*20))
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

        if not syncNodes:
            syncNodes = self.checkNodes()

        #Create the Remote Connection
        log.debug("{0} Synchronising Nodes {0}".format("="*30))
        for node in syncNodes:
            log.debug("--> Synching Node {0}".format(node))
            #First we need to create the node itself
            newNode = remoteModels.Node(id=node.id)
            rSess.add(newNode)
            
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
        rSess.commit()

    def syncLocation(self,theLocation):
        """Code to Synchonise Locations

        :param theLocation: Location to Synchronise
        :return Equivelent Location Id in the Remote Database
        """
        lSess = self.LocalSession()
        rSess = self.RemoteSession()

        log.debug("Synchonising Location {0}".format(theLocation))

        remoteRoom = rSess.query(remoteModels.Room).filter_by(name= theLocation.room.name,
                                                              roomTypeId = theLocation.room.roomTypeId).first()

        #If the Room Doesnt exist Create item
        
        
        remoteLocation = rSess.query(remoteModels.Location)
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
        rSess = self.RemoteSession()

        log.debug("Synchonising Readings")

        #Timestamp to check readings against
        cutTime = self.rUrl.lastUpdate
        rUrl = self.rUrl

        #Get the Readings
        readings = lSess.query(models.Reading).order_by(models.Reading.time)
        if cutTime:
            readings = readings.filter(models.Reading.time > cutTime)

        log.debug("Total Readings to Synch {0}".format(readings.count()))
        
        #Init Temp Storage
        locationStore = {}
        for reading in readings:
            mappedLoc = locationStore.get(reading.locationId,None)
            #Check if we have the location etc
            if mappedLoc is None:
                log.debug("No Such Location Creating")
                mapId = self.syncLocation(reading.location)
                locationStore[reading.locationId] = mapId
            #Otherwise, We should just be able to sync the Reading
            newReading = remoteModels.Reading(time = reading.time,
                                              nodeId = reading.nodeId,
                                              typeId = reading.typeId,
                                              locationId = mapId,
                                              value = reading.value)
            session.add(newReading)

        #This should be the last Sample
        commit = sesison.commit()
        print "Commit Success {0}".format(commit)
        if commit:
            self.rUrl.lastUpdate = newReading.time
            session.flush()
            session.commit()
        
        pass


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
