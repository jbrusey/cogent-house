import logging
logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO,filename="push.log")

__version__ = "0.3.0"

import sqlalchemy
import remoteModels

import cogent
import cogent.base.model as models
import cogent.base.model.meta as meta
import datetime
import subprocess

import paramiko
import sshClient
import threading
import socket

import time

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#log.setLevel(logging.DEBUG)

#Reset Paramiko logging to reduce output cruft.
plogger = paramiko.util.logging.getLogger()
plogger.setLevel(logging.WARNING)

#URL of local database to connect to
LOCAL_URL = 'mysql://test_user:test_user@localhost/pushSource'
PUSH_LIMIT = 500 #Limit on samples to transfer at any one time
SYNC_TIME = 60*10  #How often we want to call the sync (Every 10 Mins)

class Pusher(object):
    """Class to push updates to a remote database.

    .. warning::
    
        This will fail if the database type is SQ-Lite, currently a connection cannot issue a
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
        
    .. warning::
    
       In My experience you may need to bugger about with connection strings 
       Checking either Localhost or 127.0.0.1  
       Localhost worked on my machine,
       my connecting to Cogentee wanted 127.0.0.1

    .. since 0.1::
       Moved ssh port forwarding to paramiko (see sshclient class) This should stop the 
       errors when there is a connection problem.
       
    .. since 0.2::
       * Better error handling
       * Pagination for sync results, transfer at most PUSH_LIMIT items at a time. 

    .. since 0.3::
       Moved Nodestate Sync into the main readings sync class, this should stop duplicate
       nodestates turning up if there is a failiure

    """
    def __init__(self):
        log.info("Initialise Push Object")
        #Create a local session
        localEngine = sqlalchemy.create_engine(LOCAL_URL)
        self.initLocal(localEngine)


    def sync(self):
        """Synchronise data"""
        #For Each remote connection
        log.debug("Sync Data")
        session = self.LocalSession()
        theQry = session.query(models.UploadURL)
        #theQry = theQry.filter_by(url="dang@127.0.0.1")
        
        session.close()
        for syncLoc in theQry:
            log.info("-------- Sync Nodes for {0} ----------------".format(syncLoc))
            sshUrl = syncLoc.url

            log.debug("--> Creating SSH Tunnel {0}".format(sshUrl))

            #Old SSH Connection
            #subParams = ["ssh","-L","3307:localhost:3306", sshUrl]
            #log.info("--> --> {0}".format(" ".join(subParams)))
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            user,host = sshUrl.split("@")
            #Connection
            try:
                ssh.connect(host,username=user)
            except socket.error,e:
                log.warning("Connection Error {0}".format(e))
                break
            except paramiko.AuthenticationException:
                log.warning("Authentication Error")
                break

            log.debug("Connection Ok")
            transport = ssh.get_transport()
    
            # #Next setup tunnelling
            server = sshClient.forward_tunnel(3307,"127.0.0.1",3306,transport)
            serverThread = threading.Thread(target=server.serve_forever)
            serverThread.daemon = True
            serverThread.start()
          
            log.debug("--> Initialise Remote Connection")
            dburl = syncLoc.dburl
            log.debug("--> {0}".format(dburl))


            self.initRemote(syncLoc)
            
            log.debug("--> Synchronising Objects")
            log.debug("-->--> Nodes")
            try:
                self.syncNodes()
            except sqlalchemy.exc.OperationalError,e:
                log.warning(e)
                server.shutdown()
                server.socket.close()
                ssh.close()
                break
                
            # log.debug("-->--> State")
            # #Synchronise State
            # try:
            #     self.syncState()
            # except sqlalchemy.exc.OperationalError,e:
            #     log.warning(e)
            #     server.shutdown()
            #     server.socket.close()
            #     ssh.close()
            #     break
            #Synchronise Readings
            log.debug("-->--> Readings")
            try:
                needsSync = True #Simple Pagination
                while needsSync:
                    needsSync = self.syncReadings()
            except sqlalchemy.exc.OperationalError,e:
                log.warning(e)
                server.shutdown()
                server.socket.close()
                ssh.close()
                break

            server.shutdown()
            server.socket.close()
            ssh.close()

            time.sleep(1) #Let things settle down

    def initRemote(self,remoteUrl):
        """Initialise a connection to the database and reflect all Remote Tables

        :param remoteUrl:  a :class:`models.remoteURL` object that we need to connect to

        Timeout code may not be necessary (if we have a decent connection)
        But trys to address the following problem.
        1) Database is not available on connect [FAILS GRACEFULLY]
        
        2) Database is there on connect:
           Database / Network goes away during query [HANGS]

        I hope that putting a timeout on the querys will fix this.


        .. since:: 0.3  
            Connection timeout added.  
        """
        log.debug("Initialising Remote Engine")
        RemoteSession = sqlalchemy.orm.sessionmaker()

        self.rUrl = remoteUrl


        engine = sqlalchemy.create_engine(remoteUrl.dburl)
        log.debug("--> Engine {0}".format(engine))
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
            lQry = [x.id for x in lQry]
        else:
            #This means there cannot be any nodes in the remote database
            #Therefore return them all
            lQry = lSess.query(models.Node).all()
            lQry = [x.id for x in lQry]
        
        log.info("Nodes requiring sync: {0}".format(lQry))

        #lSess.close()
        lSess.close()
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
        for nId in syncNodes:
            log.info("--> Sync Node Id {0} with remote database".format(nId))
            node = lSess.query(models.Node).filter_by(id=nId).first()
            #First we need to create the node itself
            newNode = remoteModels.Node(id=node.id)
            rSess.add(newNode)
            rSess.flush()
            if node.locationId:
                newLocation = self.syncLocation(node.locationId)
                newNode.locationId = newLocation
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
        lSess.close()

    def syncLocation(self,locId):
        """Code to Synchronise Locations

        Locations are a combination of Rooms/Houses
        
        # Check we have a room of this (name/type) in the remote databases (Create)
        # Check we have a house of this (name/deployment) in the remote (Create)
        # Check we have a location with these parameters (create)

        :param locId: LocationId to Synchronise
        :return Equivalent Location Id in the Remote Database



        :since 0.1: Fixed House Name based bug.  Consider the
            following Say we have one house -> Deployment combo (Say
            Summer Deployments), then revisit at a later time (Winter
            Deployments)

            The Following should happen,
        
            Deployment1 -> House1 --(Location1)->  Room1 -> Node1 ...
            Deployment2 -> House2 --(Location2)->  Room1 -> Node1 ...

            Our Original Code for syncing locations did this:

            Deployment1 -> House1 --(Location1)->  Room1 -> Node1 ...
            Deployment2 -> House1 --(Location1)->  Room1 -> Node1 ...
        """
        lSess = self.LocalSession()
        rSess = self.RemoteSession()

        theLocation = lSess.query(models.Location).filter_by(id=locId).first()
        log.debug("{2} Synchronising Location {1} {2}".format(locId,theLocation,"="*10))

        #This is a little unfortunate, but I cannot (without over complicating reflection) 
        #Setup backrefs on the remote tables this should be a :TODO:
        #So We need a long winded query

        localRoom = theLocation.room
        log.debug("Local Room {0}".format(localRoom))
        remoteRoom = rSess.query(remoteModels.Room).filter_by(name=localRoom.name).first()
        if remoteRoom is None:
            log.debug("--> No Such Room {0}".format(localRoom.name))

            localRoomType = localRoom.roomType
            log.debug("--> Local Room Type {0}".format(localRoomType))
            #We also cannot assume that the room type will exist so we need to check that
            roomType = rSess.query(remoteModels.RoomType).filter_by(name=localRoomType.name).first()
            if roomType is None:
                log.debug("--> --> No Such Room Type {0}".format(localRoomType.name))
                roomType = remoteModels.RoomType(name=localRoomType.name)
                rSess.add(roomType)
                rSess.flush()

            remoteRoom = remoteModels.Room(name=localRoom.name,
                                           roomTypeId = roomType.id)

            rSess.add(remoteRoom)
            rSess.flush()

        rSess.commit()
        log.debug("==> Remote Room is {0}".format(remoteRoom))
        
        #Then Check the House
        localHouse = theLocation.house
        #To address the bug above, Add an intermediate step of checking the deployment
        localDeployment = localHouse.deployment
        log.debug("--> Local Deployment {0}".format(localDeployment))
        
        #Assume that all deployments will have a unique name
        remoteDeployment = rSess.query(remoteModels.Deployment).filter_by(name=localDeployment.name).first()

        if remoteDeployment is None:
            log.debug("--> --> Create new Deployment")
            remoteDeployment = remoteModels.Deployment(name=localDeployment.name,
                                                       description = localDeployment.description,
                                                       startDate = localDeployment.startDate,
                                                       endDate = localDeployment.endDate)
            rSess.add(remoteDeployment)
            rSess.commit()

        log.debug("--> Remote Deployment {0}".format(remoteDeployment))
        
        remoteHouse = rSess.query(remoteModels.House).filter_by(deploymentId = remoteDeployment.id,
                                                                address = localHouse.address).first()

        log.debug("--> Local House {0}".format(localHouse))   

        if not remoteHouse:
            #We should have created the deployment before   
            log.debug("--> --> Create new House")
            remoteHouse = remoteModels.House(address=localHouse.address,
                                             deploymentId=remoteDeployment.id)
            rSess.add(remoteHouse)
            rSess.flush()
            rSess.commit()

        log.debug("--> Remote House is {0}".format(remoteHouse))

        remoteLocation = rSess.query(remoteModels.Location).filter_by(houseId = remoteHouse.id,
                                                                      roomId=remoteRoom.id).first()

        log.debug("--> DB Remote Location {0}".format(remoteLocation))
        rSess.flush()
        if not remoteLocation:
            remoteLocation = remoteModels.Location(houseId=remoteHouse.id,
                                                   roomId = remoteRoom.id)
            rSess.add(remoteLocation)
            log.debug("Adding New Remote Location")
            
        log.debug("--> Remote Location is {0}".format(remoteLocation))
        rSess.commit()

        locId = remoteLocation.id
        lSess.close()
        rSess.close()
        return locId
        pass

    def syncReadings(self,cutTime=None):
        """Synchronise readings between two databases

        :param DateTime cutTime: Time to start the Sync from
        :return: True if sync was succesfull there are still nodes to sync
                 False if there were no nodes to Sync
                 -1 if there was an Error

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

        # If Sync is successful, fix the last update timestamp and return 
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

        #Update Node States
                  
        #Get the Readings
        readings = lSess.query(models.Reading).order_by(models.Reading.time)
        if cutTime:
            log.debug("Filter all readings since {0}".format(cutTime))
            readings = readings.filter(models.Reading.time >= cutTime)

        log.info("Total Readings to Sync {0}".format(readings.count()))
        
        #Lets try the Limit
        readings = readings.limit(PUSH_LIMIT)
        
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
                if not mapId:
                    log.warning("Error Creating Location {0}".format(reading.locationId))
                    return -1
                                
                locationStore[reading.locationId] = mapId
            #Otherwise, We should just be able to sync the Reading
            newReading = remoteModels.Reading(time = reading.time,
                                              nodeId = reading.nodeId,
                                              type = reading.typeId,
                                              locationId = mapId,
                                              value = reading.value)
                     
            session.add(newReading)
            #session.commit()

        if newReading is None:
            #If we had no data to update
            return False

        log.debug("Last Reading Added Was {0}".format(newReading))

        try:
            lastTime = newReading.time + datetime.timedelta(seconds = 1)
            session.flush()
            session.commit()
            session.close()
            #Update the Local Time stamp

            newUpdate = lSess.query(models.UploadURL).filter_by(url=self.rUrl.url).first()
            #Add a bit of jitter otherwise we end up getting the same reading.
            newUpdate.lastUpdate = lastTime
            lSess.flush()
            lSess.commit()
            log.info("Commit Successful Last update is {0}".format(newUpdate))
        except Exception, e:
            log.warning("Commit Fails {0}".format(e))
            return -1
        
        lSess.close()
        session.close()

        #Synchonise States
        log.info("Synchronising Nodestate")
        self.syncState(cutTime,lastTime)

        return True
        # pass

    def syncState(self,cutTime=None,endTime=None):
        """
        Synchronise any node state information

        Currently this just syncronises the node state table based on a given start date.
        Actually this is pretty easy, as our constaints on unique node names mean that 
        We dont have to do any error checking.

        :param DateTime startTime: Time to start filtering the states from
        """
        lSess = self.LocalSession()
        session = self.RemoteSession()

        nodeStates = lSess.query(models.NodeState).order_by(models.NodeState.time)
        log.debug("Total Nodestates {0}".format(nodeStates.count()))
        if cutTime:
            nodeStates = nodeStates.filter(models.NodeState.time >= cutTime)
        if endTime:
            nodeStates = nodeStates.filter(models.NodeState.time <= endTime)

        log.info("Total NodeStates to Sync {0}".format(nodeStates.count()))
                  
        stateCount = 0
        for item in nodeStates:
            newState = remoteModels.NodeState(time=item.time,
                                              nodeId = item.nodeId,
                                              parent = item.parent,
                                              localtime = item.localtime)
            session.add(newState)
            if stateCount == 500:
                session.flush()
                session.commit()

        session.flush()
        session.commit()
        lSess.close()
        session.close()


if __name__ == "__main__":
    logging.debug("Testing Push Classes")
    
    import time

    
    push = Pusher()
    while True: #Loop for everything
        t1= time.time()
        log.info("----- Synch at {0}".format(datetime.datetime.now()))
        push.sync()
        log.info("---- Total Time Taken for Sync {0}".format(time.time() - t1))
        time.sleep(SYNC_TIME)

