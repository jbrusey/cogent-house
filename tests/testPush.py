"""
Testing for the Deployment Module

:author: Dan Goldsmith <djgoldsmith@googlemail.com>
"""

"""
FOR FUCKS SAKE DAN.
Testing DB adds data upto Now + 2Days
We then add new data from NOW.
This means that the old stuff is attempted to Sync, Causing an Error'D

"""

#Python Library Imports
import unittest
import datetime

#Python Module Imports
from sqlalchemy import create_engine
import sqlalchemy.exc

import testmeta

models = testmeta.models

#from cogent.push import remoteModels as remoteModels
import cogent.push.Pusher as Pusher
REMOTE_URL = "sqlite:///remote.db"
LOCAL_URL = "sqlite:///test.db"

class TestPush(testmeta.BaseTestCase):
    """Test the Push Functionality.

    For the moment I think we need to overload the standard setup, teardown methods
    Otherwise we will not be able to make any changes to the database

    """

    @classmethod
    def setUpClass(self):
        """Called the First time this class is called.
        This means that we can Init the testing database once per testsuite
        
        We need to override the standard class here, as we also want to create a Remote
        database connection.
        """

        #This is a little bit hackey, but it works quite nicely at the moment.
        #Basically creates an empty remote database that we can connect to.

        #As well as the Push we want to create a direct connection to the remote database
        #This means we can query to ensure the output from each is the same

        #What is pretty cool is the idea we can also  recreate the database to clean it out each time
        #models.initialise_sql(self.engine,True)


        engine = create_engine(REMOTE_URL)
        
        remoteSession = sqlalchemy.orm.sessionmaker(bind=engine)
        self.remoteSession = remoteSession
        self.engine = engine

        self.remoteEngine = sqlalchemy.create_engine(REMOTE_URL)
        self.localEngine =  sqlalchemy.create_engine(LOCAL_URL)

        cleanDB = True
        #cleanDB = False

        #Make sure that the local and remote databases are "clean"
        models.initialise_sql(self.localEngine,cleanDB)
        testmeta.createTestDB()

        models.initialise_sql(self.remoteEngine,cleanDB,remoteSession())
        testmeta.createTestDB(remoteSession())

        #models.init_data(remoteSession())
        #models.init_data(localSession())


        #Add a remote URL to the local database
        session = testmeta.Session()
        uploadurl = models.UploadURL(url="127.0.0.1",
                                     dburl=REMOTE_URL)
        theQry = session.query(models.UploadURL).filter_by(url="127.0.0.1",
                                                           dburl=REMOTE_URL).first()
        if not theQry:
            session.add(uploadurl)
            session.flush()
            session.commit()

        #Setup the Pushing Class
        #Push Method Connection
        push = Pusher.Pusher()
        #Setup Remote Engine
        #rEngine = self._getRemoteEngine()
        session = testmeta.Session()
        remoteUrl = session.query(models.UploadURL).filter_by(url="127.0.0.1").first()
        #rEngine = sqlalchemy.create_engine(remoteUrl.dburl)

        push.initRemote(remoteUrl)
        #SEtup Local Connection
        push.initLocal(self.localEngine)
        self.push = push
            
    #def setUp(self):
    #    """Overload the setup function so we do not do the transaction wrapping"""
    #    pass

    #def tearDown(self):
    #    """Overload the teardown function so we do not do the transaction wrapping"""
    #    pass

    def _syncData(self):
        """Helper function to Synchonse the database"""
        #Synchonise Nodes
        push = self.push
        push.syncNodes()

        #Synchronise Readings
        push.syncReadings()

        #Check Everything is Equal
        lSession = testmeta.Session()
        rSession = self.remoteSession()
        lQry = lSession.query(models.Reading)
        rQry = rSession.query(models.Reading)
        self.assertEqual(lQry.count(),rQry.count())
        
        #And A double check of the items we added
        lQry = lSession.query(models.Reading).filter_by(nodeId=nodeId).all()
        rQry = rSession.query(models.Reading).filter_by(nodeId=nodeId).all()

        self.assertEqual(lQry,rQry)

    @unittest.skip("Skip this for a second")
    def testRemoteDirect(self):
        """Test to see if making a direct connection to the remote database returns what we expect"""
        push = self.push
        
        #Do we get the same items come back from the database
        #For the Remote
        remotePush = push.testRemoteQuery()
        session = self.remoteSession()
        remoteData = session.query(models.RoomType).all()
        self.assertEqual(remotePush,remoteData)

    @unittest.skip("Skip this for a second")
    def testLocalDirect(self):
        """Test to see if making a direct connection to the local database returns what we expect"""
        push = self.push
        #push = Pusher.Pusher()

        push.initLocal(self.localEngine)
        #Do we get the same items come back from the database
        #For the Remote
        remotePush = push.testLocalQuery()
        session =testmeta.Session()
        remoteData = session.query(models.RoomType).all()
        self.assertEqual(remotePush,remoteData)        

    @unittest.skip("Skip this for a second")
    def testTableConnection(self):
        """
        Test if the database connects properly when we use the 
        upload URL table
        """
        push = self.push

        #Compare to local version
        remotePush = push.testRemoteQuery()
        session = self.remoteSession()
        remoteData = session.query(models.RoomType).all()
        self.assertEqual(remotePush,remoteData)
        pass

    @unittest.skip("Skip this for a second")
    def testNodeCompareFalse(self):
        """Does the Compare Function return False if we have no changes to the Nodes"""
        push = self.push

        #As this is the first time test for equlaity between tables
        localSession = testmeta.Session()
        remoteSession = self.remoteSession()
        
        localNodes = localSession.query(models.Node).all()
        remoteNodes = remoteSession.query(models.Node).all()
        self.assertEqual(localNodes,remoteNodes)
        
        #So the node Comparison should return False (No Update Required)
        needsSync = push.checkNodes()
        self.assertFalse(needsSync)

    @unittest.skip("Skip this for a second")   
    def testNodeCompareTrue(self):
        """Does the Compeare function return something if we need to sync nodes"""
        push = self.push

        #As this is the first time test for equlaity between tables
        localSession = testmeta.Session()
        remoteSession = self.remoteSession()
        
        theNode = remoteSession.query(models.Node).filter_by(id=40).first()
        remoteSession.delete(theNode)
        remoteSession.flush()
        remoteSession.commit()
        #localNodes = localSession.query(models.Node).all()
        #remoteNodes = remoteSession.query(models.Node).all()
        #self.assertEqual(localNodes,remoteNodes)
        
        #So the node Comparison should return False (No Update Required)
        needsSync = push.checkNodes()
        self.assertEqual([theNode],needsSync)

        #Add the node back to the remoteDB
        remoteSession.add(models.Node(id=theNode.id,
                                      locationId=theNode.locationId,
                                      nodeTypeId=theNode.nodeTypeId))
        remoteSession.commit()

    @unittest.skip("Skip this for a second")
    def testSingleNodeSync(self):
        """ 
        Can We synchronise a single Node.

        This operates in a simple way, just deleteing a node from the Test DB.
        Therefore there will be no update of sensor types etc

        """
        push = self.push

        #As this is the first time test for equlaity between tables
        localSession = testmeta.Session()
        remoteSession = self.remoteSession()
        
        theNode = remoteSession.query(models.Node).filter_by(id=40).first()
        #print "{0}".format("-="*30)
        #print "Pre {0}".format(theNode)
        remoteSession.delete(theNode)
        remoteSession.flush()
        remoteSession.commit()
        #print "Post: {0}".format(theNode)
        #print "{0}".format("-="*30)
        #localNodes = localSession.query(models.Node).all()
        #remoteNodes = remoteSession.query(models.Node).all()
        #self.assertEqual(localNodes,remoteNodes)
        
        #So the node Comparison should return False (No Update Required)
        needsSync = push.checkNodes()
        #print "Sync {0}".format(needsSync[0])
        self.assertEqual([theNode],needsSync)

        push.syncNodes(needsSync)
        
        lQry = localSession.query(models.Node).all()
        rQry = remoteSession.query(models.Node).all()
        self.assertEqual(lQry,rQry)


        #This does give us a problem, as now node 40 will be missing data
        #I think the best approach is to reset the database after this sync

        cleanDB = True
        #cleanDB = False
        #Make sure that the local and remote databases are "clean"
        models.initialise_sql(self.localEngine,cleanDB)
        testmeta.createTestDB()

        models.initialise_sql(self.remoteEngine,cleanDB,remoteSession)
        testmeta.createTestDB(remoteSession)

    @unittest.skip("Skip this for a second")
    def testNodeSync(self):
        """What happens if we add some new nodes to the mix"""
        #

        #As this is the first time test for equlaity between tables
        session = testmeta.Session()
        
        #Make sure we have the right sensor types
        tempType = session.query(models.SensorType).filter_by(name="Temperature").first()   
        if tempType is None:
            tempType = models.SensorType(id=0,name="Temperature")
            session.add(tempType)
        humType = session.query(models.SensorType).filter_by(name="Humidity").first()
        if humType is None:
            humType = models.SensorType(id=2,name="Humidity")
            session.add(humType)
        co2Type = session.query(models.SensorType).filter_by(name="CO2").first()
        if co2Type is None:
            co2Type = models.SensorType(id=3,name="CO2")
            session.add(co2Type)
        session.flush()

        #Add a Couple of nodes and sensors to the local table
        newNode1 = models.Node(id=101010)
        newNode2 = models.Node(id=101012)
        newNode3 = models.Node(id=101013)
        session.add(newNode1)
        session.add(newNode2)
        session.add(newNode3)
        #And Sensors
        for item in [newNode1,newNode2,newNode3]:
            theTempSensor = models.Sensor(sensorTypeId=tempType.id,
                                          nodeId=item.id,
                                          calibrationSlope=1,
                                          calibrationOffset=0)
            session.add(theTempSensor)
            theHumSensor = models.Sensor(sensorTypeId=humType.id,
                                         nodeId=item.id,
                                         calibrationSlope=1,
                                         calibrationOffset=0)
            session.add(theHumSensor)
        #And add a Co2 Sensor to newNode3
        theCo2Sensor = models.Sensor(sensorTypeId=co2Type.id,
                                     nodeId=newNode3.id,
                                     calibrationSlope=1,
                                     calibrationOffset=0)
        session.add(theCo2Sensor)
        session.flush()
        session.commit()
        
        push = self.push
        #So the node Comparison should return True (Update Required)
        needsSync = push.checkNodes()
        self.assertTrue(needsSync)

        #And was the sync successfull
        #hasSync = push.syncNodes()
        #self.assertTrue(hasSync)
        

        push.syncNodes(needsSync)
        
        #And Was the Synchronising Successfull
        remoteSession = self.remoteSession()
        lQry = session.query(models.Node).all()
        rQry = remoteSession.query(models.Node).all()
        self.assertEqual(lQry,rQry)
        pass

    #@unittest.skip("Skip this for a second")   
    def testUpdateReadings(self):
        """Can we update the remote database readings
        
        Add a load of "new" readings to the local database and ensure they are updated correctly
        """
        
        #Given a known node and location can we update the data we have

        #Fake the last upadate
        lSession = testmeta.Session()

        theNode = lSession.query(models.Node).filter_by(id=38).first()
        tempSensor = lSession.query(models.SensorType).filter_by(name="Temperature").first()
        
        #This should give us the parameters we need
        thisTime = datetime.datetime.now()
        
        #We need to fake that we have had an update to this point in time
        theQry = lSession.query(models.UploadURL).all()
        print "======== TO UPDATE {0}".format(theQry)
        for item in theQry:
            item.lastUpdate = thisTime
            
        lSession.flush()
        lSession.commit()

        nodeId = theNode.id
        typeId = tempSensor.id
        locationId = theNode.location.id

        for x in range(10):
            theReading = models.Reading(time=thisTime,
                                        nodeId=nodeId,
                                        typeId=typeId,
                                        locationId = locationId,
                                        value=x)
            lSession.add(theReading)
            thisTime += datetime.timedelta(seconds=1)
        
        lSession.flush()
        lSession.commit()

        self._syncData()

    @unittest.skip("Skip this for a second")   
    def testUpdateNodes(self):
        """Does the Update work if we have some new nodes

        """
        lSession = testmeta.Session()

        #Get our Sensor Types
        tempType = lSession.query(models.SensorType).filter_by(name="Temperature").first()
        humType = lSession.query(models.SensorType).filter_by(name="Humidity").first()
        
        #Create Nodes and Sensors
        newNode1 = models.Node(id=201010)
        newNode2 = models.Node(id=201012)
        
        for item in [newNode1,newNode2]:
            theTempSensor = models.Sensor(sensorTypeId=tempType.id,
                                          nodeId=item.id,
                                          calibrationSlope=1,
                                          calibrationOffset=0)
            lSession.add(theTempSensor)
            theHumSensor = models.Sensor(sensorTypeId=humType.id,
                                         nodeId=item.id,
                                         calibrationSlope=1,
                                         calibrationOffset=0)
            lSession.add(theHumSensor)
            
        
        #Make Sure we update the last Synch Time
        thisTime = datetime.datetime.now()

        theQry = lSession.query(models.UploadURL)
        for item in theQry:
            item.lastUpdate = thisTime
        lSession.flush()

        #Add a load more Readings
        for x in range(10):
            for node in [newNode1,newNode2]:
                for sensor in node.sensors:
                    theReading = models.Reading(time=thisTime,
                                                nodeId=node.id,
                                                typeId=sensor.sensorTypeId,
                                                locationId = node.locationId,
                                                value=x)
                    lSession.add(theReading)
            thisTime += datetime.timedelta(seconds=1)
        
        lSession.flush()
        lSession.commit()

        self._syncData()            
        pass

    @unittest.skip("Skip this for a second")   
    def testUpdateLocations(self):
        """Does the update work if we have a new location

        This will add not only new readings, but move one of the nodes to a new Location
        """

        lSession = testmeta.Session()
        #Get our Sensor Types
        tempType = lSession.query(models.SensorType).filter_by(name="Temperature").first()
        humType = lSession.query(models.SensorType).filter_by(name="Humidity").first()
        
        #Create Nodes and Sensors
        newNode1 = models.Node(id=301010)
        newNode2 = models.Node(id=301012)
        
        #Get an Existing Location
        theHouse = lSession.query(models.House).filter_by(address="add1").first()
        masterRoom = lSession.query(models.Room).filter_by(name="Master Bedroom").first()
        secondRoom = lSession.query(models.Room).filter_by(name="Second Bedroom").first()
        
        existingLocation = lSession.query(models.Location).filter_by(houseId = theHouse.id,
                                                                    roomId = secondRoom.id).first()

        newNode1.location = existingLocation
        
        #And a New one (that uses existing houses and rooms)
        theHouse = lSession.query(models.House).filter_by(address="add2").first()
        newLocation = models.Location(houseId=theHouse.id,
                                      roomId = secondRoom.id)
        lSession.add(newLocation)



        newNode2.location = newLocation
        lSession.flush()

        lSession.commit()
        


        for item in [newNode1,newNode2]:
            theTempSensor = models.Sensor(sensorTypeId=tempType.id,
                                          nodeId=item.id,
                                          calibrationSlope=1,
                                          calibrationOffset=0)
            lSession.add(theTempSensor)
            theHumSensor = models.Sensor(sensorTypeId=humType.id,
                                         nodeId=item.id,
                                         calibrationSlope=1,
                                         calibrationOffset=0)
            lSession.add(theHumSensor)
            
        
        #Make Sure we update the last Synch Time
        thisTime = datetime.datetime.now()

        theQry = lSession.query(models.UploadURL)
        for item in theQry:
            item.lastUpdate = thisTime
        lSession.flush()
        
        #And Create a New Location to move each node to


        #Add a load more Readings
        for x in range(10):
            for node in [newNode1,newNode2]:
                for sensor in node.sensors:
                    theReading = models.Reading(time=thisTime,
                                                nodeId=node.id,
                                                typeId=sensor.sensorTypeId,
                                                locationId = node.locationId,
                                                value=x)
                    lSession.add(theReading)
            thisTime += datetime.timedelta(seconds=1)
        

            

        lSession.flush()
        lSession.commit()


        self._syncData()
        pass

    @unittest.skip("Skip this for a second")   
    def testUpdateComplete(self):
        """
        Does the update work if we we add a new deployment downwards

        Basically Ripped off from the testmeta.initDB class
        """
        thisTime = datetime.datetime.now()

        session = testmeta.Session()
        theQry = session.query(models.UploadURL)
        for item in theQry:
            item.lastUpdate = thisTime
        session.flush()

        #-------- NABBED FROM initDB with some M-% 

        now = datetime.datetime.now()
        deploymentEnd = now + datetime.timedelta(days=2)
        house2Start = now + datetime.timedelta(days=1)


        #See if we need to add these items
        theDeployment = session.query(models.Deployment).filter_by(name="Sync").first()
        #if theQry is not None:
        #    return True
        if theDeployment is None:
            theDeployment = models.Deployment(name="Sync",
                                              description="Synchonisation DB",
                                              startDate = now,
                                              endDate = deploymentEnd,
                                              )

            session.add(theDeployment)
            session.flush()
        else:
            theDeployment.update(startDate=now,
                                 endDate=deploymentEnd)

        #I Also want to add a couple of houses
        #The First House runs for One day
        house1 = session.query(models.House).filter_by(address="sync1").first()
        if house1 is None:
            house1 = models.House(deploymentId = theDeployment.id,
                                  address = "sync1",
                                  startDate = now,
                                  endDate = deploymentEnd,
                                  )
            session.add(house1)
        else:
            house1.update(startDate = now,
                          endDate = deploymentEnd)

        house2 = session.query(models.House).filter_by(address="sync2").first()
        if house2 is None:
            house2 = models.House(deploymentId = theDeployment.id,
                                  address = "sync2",
                                  startDate = house2Start,
                                  endDate = deploymentEnd,
                                  )
            session.add(house2)
        else:
            house2.update(startDate = house2Start,
                          endDate = deploymentEnd)

        session.flush()

        #Lets Add Some Rooms (Using Bruseys new Room Paradigm)

        #Get the Relevant Room Types
        bedroomType = session.query(models.RoomType).filter_by(name="Kitchen").first()
        if bedroomType is None:
            bedroomType = models.RoomType(name="Kitchen")
            session.add(bedroomType)

        livingType = session.query(models.RoomType).filter_by(name="Living Room").first()
        if livingType is None:
            livingType = models.RoomType(name="Living Room")
            session.add(livingType)

        session.flush()

        #And the Specific Rooms themselves
        masterBed = session.query(models.Room).filter_by(name="Master Kitchen").first()
        if masterBed is None:
            #(Note) We can either add room type by Id
            masterBed = models.Room(name="Master Kitchen",roomTypeId=bedroomType.id)
            session.add(masterBed)

        secondBed = session.query(models.Room).filter_by(name="Second Kitchen").first()
        if secondBed is None:
            #Or We can do it the easier way
            secondBed = models.Room(name="Second Kitchen")
            secondBed.roomType = bedroomType
            session.add(secondBed)

        #Add a Living Room too
        livingRoom = session.query(models.Room).filter_by(name="Living Room").first()
        if livingRoom is None:
            livingRoom = models.Room(name="Living Room")
            livingRoom.roomType = livingType
            session.add(livingRoom)

        session.flush()

        #Each House Should have a Master Bed room
        loc1_Master = session.query(models.Location).filter_by(houseId=house1.id,roomId = masterBed.id).first()
        if loc1_Master is None:
            loc1_Master = models.Location(houseId = house1.id,
                                        roomId = masterBed.id)
            session.add(loc1_Master)

        loc2_Master = session.query(models.Location).filter_by(houseId=house2.id,roomId = masterBed.id).first()
        if loc2_Master is None:
            loc2_Master = models.Location(houseId = house2.id,
                                        roomId = masterBed.id)
            session.add(loc2_Master)

        #Each House Should Also have a Living Rooms
        loc1_Living = session.query(models.Location).filter_by(houseId=house1.id,roomId=livingRoom.id).first()
        if loc1_Living is None:
            loc1_Living = models.Location(houseId = house1.id,
                                          roomId = livingRoom.id)
            session.add(loc1_Living)

        loc2_Living = session.query(models.Location).filter_by(houseId=house2.id,roomId=livingRoom.id).first()
        if loc2_Living is None:
            loc2_Living = models.Location(houseId = house2.id,
                                          roomId = livingRoom.id)
            session.add(loc2_Living)

        #And Lets be Generous and Give the First House a Second Kitchen
        loc1_Second = session.query(models.Location).filter_by(houseId = house1.id,
                                                               roomId = secondBed.id).first()
        if loc1_Second is None:
            loc1_Second = models.Location(houseId = house1.id,
                                          roomId = secondBed.id)
            session.add(loc1_Second)



        session.flush()

        #Create Nodes and Sensors

        node37 = session.query(models.Node).filter_by(id=40037).first()
        if node37 is None:
            node37 = models.Node(id=40037)
            session.add(node37)

        node38 = session.query(models.Node).filter_by(id=40038).first()
        if node38 is None:
            node38 = models.Node(id=40038)
            session.add(node38)

        node39 = session.query(models.Node).filter_by(id=40039).first()
        if node39 is None:
            node39 = models.Node(id=40039)
            session.add(node39)

        node40 = session.query(models.Node).filter_by(id=40040).first()
        if node40 is None:
            node40 = models.Node(id=40040)
            session.add(node40)

        node69 = session.query(models.Node).filter_by(id=40069).first()
        if node69 is None:
            node69 = models.Node(id=40069)
            session.add(node69)

        node70 = session.query(models.Node).filter_by(id=40070).first()
        if node70 is None:
            node70 = models.Node(id=40070)
            session.add(node70)


        #We want to work only with temperature database
        tempType = session.query(models.SensorType).filter_by(name="Temperature").first()   
        if tempType is None:
            tempType = models.SensorType(id=0,name="Temperature")
            session.add(tempType)
        session.flush()

        #To make iterating through locations a little easier when adding samples
        locs = [node37,node38,node39,node40,node69,node70]

        #While Technically it would be a good idea to have sensor's 
        #We may be able to get away with just having sensor types
        #However they are needed for the Visualiser so we can add them here.
        for item in locs:
            theSensor = session.query(models.Sensor).filter_by(sensorTypeId =tempType.id,
                                                               nodeId=item.id).first()
            if theSensor is None:
                theSensor = models.Sensor(sensorTypeId=tempType.id,
                                          nodeId=item.id,
                                          calibrationSlope=1,
                                          calibrationOffset=0)
                session.add(theSensor)

        session.flush()

        #Zap all old data
        for item in locs:
            theQry = session.query(models.Reading).filter_by(nodeId=item.id,
                                                             typeId=tempType.id)
            theQry.delete()

        #Next Add some data for each node

        #Deployment 1 Lasts for 2 Days, Pretend we have a sampling rate of 1 samples per hour
        #Match Nodes and Locations (1 Node for Each Kitchen + 2 in the Living Room)
        node37.location = loc1_Master
        node38.location = loc1_Second
        node39.location = loc1_Living

        session.flush()

        #Add Data (Deal with node 40 seperately as this is a corner case

        locs = [node37,node38,node39]
        for x in range(2*24):
        #for x in range(3):
            insertDate = now+datetime.timedelta(hours = x)
            for item in locs:
                #Composite Key not working in Reading
                session.add(models.Reading(time=insertDate,
                                           nodeId=item.id,
                                           typeId=tempType.id,
                                           locationId=item.location.id,
                                           value=item.id + x))
        session.flush()

        #But we also get overZealous with Node 40
        #For the first week it is in the Living Room
        node40.location = loc1_Living
        for x in range(1*24):
            insertDate = now+datetime.timedelta(hours = x)
            session.add(models.Reading(time =insertDate,
                                       nodeId=node40.id,
                                       typeId=tempType.id,
                                       locationId=node40.location.id,
                                       value=node40.id+x))

        session.flush()
        #But we then move it to the Master Kitchen
        node40.location = loc1_Master
        for x in range(1*24):
            insertDate = house2Start+datetime.timedelta(hours = x)
            session.add(models.Reading(time =insertDate,
                                       nodeId=node40.id,
                                       typeId=tempType.id,
                                       locationId=node40.location.id,
                                       value=node40.id+(24+x)))

        #TODO: Our Data for the Living room node 40 disapears in the visualiser
        session.flush()

        #We then Go to Deployment 2 it lasts for 1 day
        #Match nodes and Locations 1 Node in Bed and Living Room
        node69.location = loc2_Master
        node70.location = loc2_Living

        locs = [node69,node70]
        for x in range(1*24):
        #for x in range(3):
            insertDate = house2Start+datetime.timedelta(hours = x)
            for item in locs:
                #Composite Key not working in Reading
                session.add(models.Reading(time=insertDate,
                                           nodeId=item.id,
                                           typeId=tempType.id,
                                           locationId=item.location.id,
                                           value=item.id + x))
        session.flush()
        session.commit()
        session.close()





        self._syncData()

        pass


if __name__ == "__main__":
    unittest.main()
