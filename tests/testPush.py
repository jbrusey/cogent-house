"""
Testing for the Push Module Functionality

It should be noted that the push functionality does not work properly with sqlite.
See the pusher documentation for details

:author: Dan Goldsmith <djgoldsmith@googlemail.com>
"""

#Python Library Imports
import unittest
from datetime import datetime, timedelta

import ConfigParser

#Python Module Imports
from sqlalchemy import create_engine
import sqlalchemy.exc

import testmeta

models = testmeta.models
populateData = testmeta.populateData

import cogent.push.Pusher as Pusher

import subprocess

#Pooling for connections
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

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

        For the SSH Tunnel it may be worth investigating paramiko
        """

        #This is a little bit hackey, but it works quite nicely at the moment.
        #Basically creates an empty remote database that we can connect to.

        #As well as the Push we want to create a direct connection to the remote database
        #This means we can query to ensure the output from each is the same

        #What is pretty cool is the idea we can also  recreate the database to clean it out each time
        #Create the Local and Remote Database Engines and sessions

        try:
            confFile = open("setup.conf")
        except IOError:
            confFile = open("tests/setup.conf")

        config = ConfigParser.ConfigParser()
        #Read the File
        config.readfp(confFile)
        
        #And pull out the DB Url
        remoteUrl = config.get("TestDB","remoteDB")
        localUrl = config.get("TestDB","localDB")
        log.debug("Remote Database: {0}".format(remoteUrl))
        log.debug("Local Database: {0}".format(localUrl))

        self.configUrl = remoteUrl


        self.remoteEngine = sqlalchemy.create_engine(remoteUrl)
        self.remoteSession = sqlalchemy.orm.sessionmaker(bind=self.remoteEngine)

        self.localEngine =  sqlalchemy.create_engine(localUrl)
        self.localSession = sqlalchemy.orm.sessionmaker(bind=self.localEngine)

        cleanDB = True
        #cleanDB = False

        #Make sure that the local and remote databases are "clean" then populate with data
        log.debug("Init Remote DB")
        models.initialise_sql(self.remoteEngine,cleanDB)
        models.populate_data(self.remoteSession())
        testmeta.createTestDB(self.remoteSession())

        log.debug("Init Local DB")
        models.initialise_sql(self.localEngine,cleanDB)
        models.populate_data(self.localSession())
        testmeta.createTestDB(self.localSession())

        #Add an Update Time.  This can be used to increment the "Last update"
        #And avoid problems with the testing script running stuff out of order
        #As our testing DB has 2 days worth of data in it, we need this to be now + 2 days
        #So Lets make it 5 days to be sure
        #return
        now = datetime.now() + timedelta(days=5)

        #Add a remote URL to the local database
        session = self.localSession()
        uploadurl = models.UploadURL(url="127.0.0.1",
                                     dburl=remoteUrl,
                                     lastUpdate=now)

        theQry = session.query(models.UploadURL).filter_by(url="127.0.0.1",
                                                           dburl=remoteUrl).first()
        if not theQry:
            session.add(uploadurl)
            session.flush()
            session.commit()

        #Setup the Pushing Class
        push = Pusher.Pusher(localUrl)
        self.remoteUrl = session.query(models.UploadURL).filter_by(url="127.0.0.1").first()
        #Initalise the connection
        push.initRemote(self.remoteUrl)

        push.initLocal(self.localEngine)
        self.push = push

        log.debug("{0} Starting Tests {0}".format("="*30))

    #@classmethod
    #def tearDownClass(self):
    #    #As this class adds a load of cruft. It is best we drop everything and start again
    #    models.initialise_sql(self.localEngine,True)

    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def _syncData(self):
        """Helper function to Synchonse the database"""
        #Synchonise Nodes
        push = self.push
        push.syncNodes()

        #Synchronise State
        push.syncState()
        
        #Synchronise Readings
        push.syncReadings()
        

        #Check Everything is Equal
        lSession = self.localSession()
        rSession = self.remoteSession()
        lQry = lSession.query(models.Reading)
        rQry = rSession.query(models.Reading)
        self.assertEqual(lQry.count(),rQry.count())
       
    def testPush_UpdateReadings(self):
        """Can we update the remote database readings
        
        Add a load of "new" readings to the local database and ensure they are updated correctly.
        """
        
        lSession = self.localSession()

        #We need to fake that we have had an update to this point in time
        theQry = lSession.query(models.UploadURL).filter_by(url="127.0.0.1",
                                                            dburl=self.configUrl).first()

        thisTime = theQry.lastUpdate + timedelta(days=1)


        lSession.flush()
        lSession.commit()

        #Get Node and Sensor Parameters
        theNode = lSession.query(models.Node).filter_by(id=38).first()
        tempSensor = lSession.query(models.SensorType).filter_by(name="Temperature").first()

        nodeId = theNode.id
        typeId = tempSensor.id
        locationId = theNode.location.id

        log.debug("Adding Readings:")
        log.debug("--> Start Time {0}".format(thisTime))
        for x in range(10):
            theReading = models.Reading(time=thisTime,
                                        nodeId=nodeId,
                                        typeId=typeId,
                                        locationId = locationId,
                                        value=x)
            lSession.add(theReading)
            thisTime += timedelta(seconds=1)

        log.debug("--> End Time: {0}".format(thisTime))

        lSession.flush()
        lSession.commit()
        lSession.close()
        #self.thisTime = thisTime
        self._syncData()

    def testUpdateLocations_Complex(self):
        """Does the update work if we have a somewhat more complex set of locations

        Checking if a possible corner case is correctly fixed.
        Say we have one house -> Deploymet combo (Say Summer Deplyments),  then revist at a later time (Winter Depooyments)

        The Following should happen,
        
        Deployment1 -> House1 --(Location1)->  Room1 -> Node1 ...
        Deployment2 -> House2 --(Location2)->  Room1 -> Node1 ...

        But I think our current update may do this as it currently based on house Address.

        Deployment1 -> House1 --(Location1)->  Room1 -> Node1 ...
        Deployment2 -> House1 --(Location1)->  Room1 -> Node1 ...
        """
        
        lSession = self.localSession()
        rSession = self.remoteSession()

        #Simulate another DB Synching
        otherDeployment = models.Deployment(name="Other")
        rSession.add(otherDeployment)
        rSession.flush()
        rSession.commit()
        #otherHouse = models.House(address="Other",deploymentId = otherDeployment.id)
        #rSession.add(otherHouse)
        #rSession.flush()
        #rSession.commit()

        #Get times to insert Readings
        theQry = lSession.query(models.UploadURL).filter_by(url="127.0.0.1",
                                                            dburl=self.configUrl).first()
  
        thisTime = theQry.lastUpdate + timedelta(days=1)

        #Build the dataset
        summerDeployment = models.Deployment(name="Summer")
        winterDeployment = models.Deployment(name="Winter")

        lSession.add(summerDeployment)
        lSession.add(winterDeployment)
        lSession.flush()


        summerHouse = models.House(address="Address1",
                                deploymentId = summerDeployment.id,
                                )
        lSession.add(summerHouse)

        winterHouse = models.House(address="Address1",
                                   deploymentId = winterDeployment.id)
        lSession.add(winterHouse)
        lSession.flush()

        #Get some Rooms
        masterBed = lSession.query(models.Room).filter_by(name="Master Bedroom").first()
        secondBed = lSession.query(models.Room).filter_by(name="Second Bedroom").first()


        #And Locations
        summerMaster = models.Location(houseId = summerHouse.id,
                                       roomId = masterBed.id)
        summerSecond = models.Location(houseId = summerHouse.id,
                                       roomId = secondBed.id)

        winterMaster = models.Location(houseId = winterHouse.id,
                                       roomId = masterBed.id)
        winterSecond = models.Location(houseId = winterHouse.id,
                                       roomId = secondBed.id)            

        lSession.add(summerMaster)
        lSession.add(summerSecond)
        lSession.add(winterMaster)
        lSession.add(winterSecond)
        lSession.flush()

        #Add Nodes to each Location
        node37 = lSession.query(models.Node).filter_by(id=37).first()
        node38 = lSession.query(models.Node).filter_by(id=38).first()

        node37.location = summerMaster
        node38.location = summerSecond
        lSession.flush()

        #And add readings for each of these Nodes one should be enough to trigger any updates
        for node in [node37,node38]:
            theReading = models.Reading(time=thisTime,
                                        nodeId = node.id,
                                        locationId = node.locationId,
                                        value = 100,
                                        typeId = 0)
            lSession.add(theReading)
            
        lSession.flush()

        node37.location = winterMaster
        node38.location = winterSecond
        lSession.flush()

        for node in [node37,node38]:
            theReading = models.Reading(time=thisTime + timedelta(days=1),
                                        nodeId = node.id,
                                        locationId = node.locationId,
                                        value = 100,
                                        typeId = 0)
            lSession.add(theReading)

        lSession.flush()
        lSession.commit()
        lSession.close()


        

        #Check if we have any nodes to Sync
        push = self.push
        checkNodes = push.checkNodes()
        log.debug("Nodes to Sync {0}".format(checkNodes))
        #This should return an empty list
        self.assertEqual(checkNodes,[])

        
        #This should check that the number of readings match
        self._syncData()

        #And Check that all the items Match
        lSession = self.localSession()
        rSession = self.remoteSession()
       

        #Deployments
        log.debug("Check Deployments")
        lQry = lSession.query(models.Deployment)
        rQry = rSession.query(models.Deployment)
        #Remove one from remote count as we added a "fake" item above
        self.assertEqual(lQry.count(),rQry.count()-1)

        #Houses
        log.debug("Check Houses")
        lQry = lSession.query(models.House)
        rQry = rSession.query(models.House)
        self.assertEqual(lQry.count(),rQry.count(),"Houses Do Not Match")

        #Locations
        log.debug("Check Locations")
        lQry = lSession.query(models.Location)
        rQry = rSession.query(models.Location)
        self.assertEqual(lQry.count(),rQry.count(),"Locations Do Not Match")        
        
    
    def testUpdateNodes(self):
        """Does the Update work if we have some new nodes

        """
        lSession = self.localSession()

        #Make Sure we update the last Synch Time so it plays nicely with unittest
        theQry = lSession.query(models.UploadURL).filter_by(url="127.0.0.1",
                                                            dburl=self.configUrl).first()
        thisTime = theQry.lastUpdate + timedelta(days=1)


        #Get our Sensor Types
        tempType = lSession.query(models.SensorType).filter_by(name="Temperature").first()
        humType = lSession.query(models.SensorType).filter_by(name="Humidity").first()
        
        #Create Nodes and Sensors
        newNode1 = models.Node(id=201010)
        newNode2 = models.Node(id=201012)
        lSession.add(newNode1)
        lSession.add(newNode2)

        #The Nodes also need a location,  Lets use an Exisitng One
        theLocation = lSession.query(models.Location).first()
        newNode1.location = theLocation
        newNode2.location = theLocation
        lSession.flush()


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

        lSession.flush()
        lSession.commit()

        #return

        #Add a load more Readings

        log.debug("Adding Readings:")
        log.debug("--> Start Time {0}".format(thisTime))

        for x in range(10):
            for node in [newNode1,newNode2]:
                for sensor in node.sensors:
                    theReading = models.Reading(time=thisTime,
                                                nodeId=node.id,
                                                typeId=sensor.sensorTypeId,
                                                locationId = node.locationId,
                                                value=x)
                    lSession.add(theReading)

            thisTime += timedelta(seconds=1)
        
        log.debug("--> End Time: {0}".format(thisTime))
        lSession.flush()
        lSession.commit()
        lSession.close()
        self._syncData()  

    def testUpdateLocations(self):
        """Does the update work if we have a new location

        This will add not only new readings, but move one of the nodes to a new Location
        """

        lSession = self.localSession()

        #Make Sure we update the last Synch Time so it plays nicely with unittest
        theQry = lSession.query(models.UploadURL).filter_by(url="127.0.0.1",
                                                            dburl=self.configUrl).first()
        thisTime = theQry.lastUpdate + timedelta(days=1)

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
            
        
        lSession.flush()
        lSession.commit()
        
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
            thisTime += timedelta(seconds=1)
        

            

        lSession.flush()
        lSession.commit()
        lSession.close()
        self._syncData()
        #pass

    def testUpdateComplete(self):
        """
        Does the update work if we we add a new deployment downwards

        Basically Ripped off from the testmeta.initDB class
        """
        
        #thisTime = self.thisTime + timedelta(days=10)

        session = self.localSession()

        theQry = session.query(models.UploadURL).filter_by(url="127.0.0.1",
                                                           dburl=self.configUrl).first()

        thisTime = theQry.lastUpdate + timedelta(days=1)

        #-------- NABBED FROM initDB with some M-% 

        now = thisTime
        deploymentEnd = now + timedelta(days=2)
        house2Start = now + timedelta(days=1)


        #See if we need to add these items
        theDeployment = session.query(models.Deployment).filter_by(name="Sync").first()

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
            insertDate = now+timedelta(hours = x)
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
            insertDate = now+timedelta(hours = x)
            session.add(models.Reading(time =insertDate,
                                       nodeId=node40.id,
                                       typeId=tempType.id,
                                       locationId=node40.location.id,
                                       value=node40.id+x))

        session.flush()
        #But we then move it to the Master Kitchen
        node40.location = loc1_Master
        for x in range(1*24):
            insertDate = house2Start+timedelta(hours = x)
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
            insertDate = house2Start+timedelta(hours = x)
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

        #self.thisTime = thisTime
        self._syncData()

    def testPush_UpdateNodeState(self):
        """Does the node state update correctly"""
        push = self.push
        #push.syncNodes()
        
        #We need to add some states to update
        lSession = self.localSession()

        #We need to fake that we have had an update to this point in time
        theQry = lSession.query(models.UploadURL).filter_by(url="127.0.0.1",
                                                            dburl=self.configUrl).first()

        thisTime = theQry.lastUpdate + timedelta(days=1)

        #And Add some new nodestates
        theNodes = lSession.query(models.Node).limit(10)
        
        for item in theNodes:
        #for x in range(10):
           lSession.add(models.NodeState(time=thisTime,
                                         nodeId=item.id,
                                         parent=1024,
                                         localtime = 0))

        lSession.flush()
        lSession.commit()
                         
        


        push.syncState(thisTime)

        lSession = self.localSession()
        rSession = self.remoteSession()
        lQry = lSession.query(models.NodeState)
        rQry = rSession.query(models.NodeState)
        self.assertEqual(lQry.count(),rQry.count())        
        


if __name__ == "__main__":
    unittest.main()
