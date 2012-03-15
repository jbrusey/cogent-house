"""
Testing for the Push Module Functionality

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
#REMOTE_URL = "sqlite:///remote.db"
REMOTE_URL = "mysql://root:Ex3lS4ga@127.0.0.1:3307/testStore"
LOCAL_URL = "sqlite:///test.db"


import subprocess

#Pooling for connections


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
        #models.initialise_sql(self.engine,True)


        engine = create_engine(REMOTE_URL)
        
        remoteSession = sqlalchemy.orm.sessionmaker(bind=engine)
        self.remoteSession = remoteSession
        self.engine = engine

        self.remoteEngine = sqlalchemy.create_engine(REMOTE_URL)
        self.localEngine =  sqlalchemy.create_engine(LOCAL_URL)

        print "Starting SSH Tunnel"
        theProcess = subprocess.Popen("ssh -L 3308:localhost:3307 dang@127.0.0.1",
                                      shell=True,
                                      close_fds=True)

        self.theProcess = theProcess
        #print theProcess.communicate()

        cleanDB = True
        #cleanDB = False

        #Make sure that the local and remote databases are "clean"
        models.initialise_sql(self.localEngine,cleanDB)
        testmeta.createTestDB()

        models.initialise_sql(self.remoteEngine,cleanDB,remoteSession())
        #testmeta.createTestDB(remoteSession())

        #models.init_data(remoteSession())
        #models.init_data(localSession())

        #Add an Update Time.  This can be used to increment the "Last update"
        #And avoid problems with the testing script running stuff out of order
        #As our testing DB has 2 days worth of data in it, we need this to be now + 2 days
        #So Lets make it 5 days to be sure
        now = datetime.datetime.now() + datetime.timedelta(days=5)

        #Add a remote URL to the local database
        session = testmeta.Session()
        uploadurl = models.UploadURL(url="127.0.0.1",
                                     dburl=REMOTE_URL,
                                     lastUpdate=now)
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

    def setUp(self):
        pass
    
    def tearDown(self):
        pass

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
       
    @unittest.skip("Skip this for a second")   
    def testPush_UpdateReadings(self):
        """Can we update the remote database readings
        
        Add a load of "new" readings to the local database and ensure they are updated correctly

        OK
        """
        
        #Given a known node and location can we update the data we have
        #print "{0} TEST UPDATE READINGS {0}".format("-"*20)
        #Fake the last upadate
        lSession = testmeta.Session()
        lSession.flush()
        theNode = lSession.query(models.Node).filter_by(id=38).first()
        tempSensor = lSession.query(models.SensorType).filter_by(name="Temperature").first()

        #We need to fake that we have had an update to this point in time
        theQry = lSession.query(models.UploadURL).filter_by(url="127.0.0.1",
                                                            dburl=REMOTE_URL).first()
        #Add about 10 days so there are no clashes in timestamps
        #print "--> DB Time {0}".format(theQry)
        thisTime = theQry.lastUpdate + datetime.timedelta(days=1)
        #print "---> Current Time {0}".format(thisTime)
        #theQry.lastUpdate = thisTime
        #for item in theQry:
        #    item.lastUpdate = thisTime
            
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
            #print "--> Item Added {0}".format(theReading)
            thisTime += datetime.timedelta(seconds=1)
        
        lSession.flush()
        lSession.commit()
        lSession.close()
        #self.thisTime = thisTime
        self._syncData()

    @unittest.skip("Skip this for a second")   
    def testUpdateNodes(self):
        """Does the Update work if we have some new nodes

        """
        #print
        #print "{0} TEST UPDATE NODES {0}".format("-"*20)
        lSession = testmeta.Session()

        #Make Sure we update the last Synch Time so it plays nicely with unittest
        theQry = lSession.query(models.UploadURL).filter_by(url="127.0.0.1",
                                                            dburl=REMOTE_URL).first()
        #Add about 10 days so there are no clashes in timestamps
        #print "--> DB Time {0}".format(theQry)
        thisTime = theQry.lastUpdate + datetime.timedelta(days=1)
        #print "--> This Time {0}".format(thisTime)

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
            #print "Sensor Added {0}".format(theTempSensor)
            theHumSensor = models.Sensor(sensorTypeId=humType.id,
                                         nodeId=item.id,
                                         calibrationSlope=1,
                                         calibrationOffset=0)
            lSession.add(theHumSensor)

        lSession.flush()
        lSession.commit()

        #return

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
        lSession.close()
        self._syncData()  

    #-------------------------------------------          

    @unittest.skip("Skip this for a second")   
    #FAIL HERE
    def testUpdateLocations(self):
        """Does the update work if we have a new location

        This will add not only new readings, but move one of the nodes to a new Location
        """

        lSession = testmeta.Session()

        #Make Sure we update the last Synch Time so it plays nicely with unittest
        theQry = lSession.query(models.UploadURL).filter_by(url="127.0.0.1",
                                                            dburl=REMOTE_URL).first()
        #Add about 10 days so there are no clashes in timestamps
        print "--> DB Time {0}".format(theQry)
        thisTime = theQry.lastUpdate + datetime.timedelta(days=1)
        print "--> This Time {0}".format(thisTime)

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
        #thisTime = self.thisTime + datetime.timedelta(days=10)

        #theQry = lSession.query(models.UploadURL).first()
        #theQry.lastUpdate = thisTime
        #for item in theQry:
        #    item.lastUpdate = thisTime
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
            thisTime += datetime.timedelta(seconds=1)
        

            

        lSession.flush()
        lSession.commit()
        lSession.close()
        self._syncData()
        #pass

    #@unittest.skip("Skip this for a second")   
    def testUpdateComplete(self):
        """
        Does the update work if we we add a new deployment downwards

        Basically Ripped off from the testmeta.initDB class
        """
        
        #thisTime = self.thisTime + datetime.timedelta(days=10)

        session = testmeta.Session()

        theQry = session.query(models.UploadURL).filter_by(url="127.0.0.1",
                                                           dburl=REMOTE_URL).first()
        #Add about 10 days so there are no clashes in timestamps
        print "--> DB Time {0}".format(theQry)
        thisTime = theQry.lastUpdate + datetime.timedelta(days=1)
        print "--> This Time {0}".format(thisTime)

        #theQry = session.query(models.UploadURL).first()
        #for item in theQry:
        #    item.lastUpdate = thisTime
        #session.flush()
        #lSession.commit()

        #-------- NABBED FROM initDB with some M-% 

        now = thisTime
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

        #self.thisTime = thisTime
        self._syncData()

        pass


if __name__ == "__main__":
    unittest.main()
