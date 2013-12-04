""" Unittests for the push script


NOTE:  Not as atomic as they should be.  However, testing becomes a tad tricksy
       when you cannot garuentee that the code runs in order
"""


import unittest
import os

import configobj
import requests

import sqlalchemy

RESTURL = "http://127.0.0.1:6543/rest/"

import cogent.push.RestPusher as RestPusher
import cogent.base.model as models

import init_testingdb

import logging
logging.getLogger("nosecover3").setLevel(logging.WARNING)

@unittest.skip
class TestServer(unittest.TestCase):
    """Code to test that the push server works as expected"""

    def test_init(self):
        """Can we initialise a push server"""
        server = RestPusher.PushServer()
        self.assertIsInstance(server, RestPusher.PushServer)

    def test_readcondif(self):
        """Is the configuration file read correctly"""
        server = RestPusher.PushServer(configfile="test.conf")

        parser = server.configparser
        self.assertIsInstance(parser, configobj.ConfigObj)

        #And check that we have all the relevant sections        
        self.assertTrue(parser["general"])
        
        #What should we have in the general section
        tmpdict = {"localurl": "mysql://chuser@localhost/push_test",
                  "pushlimit": '10000',
                  "synctime": '10'}

        self.assertEqual(tmpdict, parser["general"])

        self.assertTrue(parser["locations"])

        tmpdict = {"local":'0',
                   "cogentee":'0',
                   "test":'1'}

        self.assertEqual(tmpdict, parser["locations"])


        tmpdict = {"resturl": "http://127.0.0.1:6543/rest/"}
        self.assertEqual(parser["local"], tmpdict)
        self.assertEqual(parser["test"], tmpdict)

        tmpdict = {"resturl": "http://cogentee.coventry.ac.uk/salford/rest/"}
        self.assertEqual(parser["cogentee"], tmpdict)

    def test_setupClient(self):
        """Does the push client get setup correctly"""

        server = RestPusher.PushServer(configfile="test.conf")
        
        pushlist = server.synclist
        self.assertEqual(len(pushlist),1)
        
        item = pushlist[0]
        self.assertEqual(item.restUrl,
                         "http://127.0.0.1:6543/rest/")

#@unittest.skip
class TestClient(unittest.TestCase):
    """ Code to test the rest client """


    @classmethod
    def setUpClass(cls):
        """Create just one instance of the push server to test"""

        #We want to remove any preexisting config files
        
        confpath = "localhost_push_test_map.conf"
        if os.path.exists(confpath):
            print "DELETING EXISTING CONFIG FILE"
            os.remove(confpath)

        import time
        t1 = time.time()

        REINIT = False     
        if REINIT:

            #TODO: Fix this so no majic strings
            #and create the database
            init_testingdb.main("mysql://chuser@localhost/push_test")
            print "Total Time Taken {0}".format(time.time() - t1)
            #And the remote DB
            init_testingdb.main("mysql://chuser@localhost/test")

            #TODO:  Fix this so theres a bit less magic strings
            #We also want to initialise the testing DB
            #init_testingdb.main("sqlite:///home/dang/coding/webinterface/viewer-repo/cogent-house.devel/test.db")
        
        #We also want to open a connection to the remote database (so everything can get cleaned up)
        remoteengine = sqlalchemy.create_engine("mysql://chuser@localhost/test")
        connection = remoteengine.connect()
        cls.rSession = sqlalchemy.orm.sessionmaker(bind=remoteengine)

        server = RestPusher.PushServer(configfile="test.conf")
        cls.pusher = server.synclist[0]

        #And a link to that classes session (so we can check everything)
        cls.Session = cls.pusher.localsession

        #cls.pusher.log.setLevel(logging.WARNING)

    def setUp(self):
        """Reset all the mappings before running any tests"""
        # Storage for mappings between local -> Remote 
        self.pusher.mappedDeployments = {} 
        self.pusher.mappedHouses = {} 
        self.pusher.mappedRooms = {} 
        self.pusher.mappedLocations = {} 
        self.pusher.mappedRoomTypes = {} 
        self.pusher.mappedSensorTypes = {} 

    #@unittest.skip
    def test_connection(self):
        """Can we get an connection"""
        
        self.assertTrue(self.pusher.checkConnection(),
                        msg="No Connection to the test server... Is it running?")


    def test_nodetypes_remote(self):
        """Can we properly synch nodetypes

        Like sensor types node types should be synchronised across all server.
        If there is a conflict on node type Id, we should Fail

        """
        rurl = "{0}nodetype/".format(RESTURL)

        #Cleanup
        session = self.Session()
        qry = session.query(models.NodeType).filter_by(id = 5000)
        qry.delete()
        session.flush()
        session.commit()

        session = self.rSession()
        qry = session.query(models.NodeType).filter_by(id = 5000)
        qry.delete()
        session.flush()
        session.commit()
        
        #Check that the numebrs are as expected
        session = self.Session()
        qry = session.query(models.NodeType)
        lcount = qry.count()
        session.close()
        session = self.rSession()
        qry = session.query(models.NodeType)
        rcount = qry.count()
        session.close()
        self.assertEqual(lcount, rcount)
        
        self.pusher.sync.nodetypes()
        session = self.Session()
        qry = session.query(models.NodeType)
        self.assertEqual(lcount, qry.count())

        #Delete nodetypes in the local database
        session = self.Session()
        qry = session.query(models.NodeType).filter_by(id=10)
        qry.delete()
        qry = session.query(models.NodeType).filter_by(id=11)
        qry.delete()
        session.commit()

        #And check they come back
        self.pusher.sync_nodetypes()
        session = self.Session()
        qry = session.query(models.NodeType)
        self.assertEqual(qry.count(), lcount)

        qry = session.query(models.NodeType).filter_by(id=10).first()
        self.assertTrue(qry)
        self.assertEquals(qry.Name, "ClusterHead CO2")
        qry = session.query(models.NodeType).filter_by(id=11).first()
        self.assertTrue(qry)
        self.assertEquals(qry.Name, "ClusterHead AQ")
        
        #Finally add a new sensor type on the remote server (its a corner case)
        session = self.Session()
        newtype = models.SensorType(id=5000,
                                    name="Testing Node")
        session.add(newtype)
        session.commit()
        
        self.pusher.sync_nodetypes()
        #Does it exist on the remote
        session = self.rSession()
        qry = session.query(models.SensorType).filter_by(id=5000).first()
        self.assertTrue(qry)
        self.assertEqual(qry.name, "Testing Node")
        
        #Cleanup
        session = self.Session()
        qry = session.query(models.NodeType).filter_by(id = 5000)
        qry.delete()
        session.flush()
        session.commit()

        session = self.rSession()
        qry = session.query(models.NodeType).filter_by(id = 5000)
        qry.delete()
        session.flush()
        session.commit()

    #@unittest.skip
    def test_nodetypes_fails(self):
        """Does the sensortype fail if we have bad sensortypes"""
        session = self.Session()
        qry = session.query(models.NodeType).filter_by(id=0)
        #change the paramertes
        sensor = qry.first()
        sensor.name="FOOBAR"
        session.flush()
        session.commit()
        session.close()

        with self.assertRaises(RestPusher.MappingError):
            self.pusher.sync_nodetypes()

        #And reset the details of the node
        session = self.Session()
        qry = session.query(models.NodeType).filter_by(id=0)
        #change the paramertes
        sensor = qry.first()
        sensor.name="Base"
        session.flush()
        session.commit()
        session.close()
        

    #@unittest.skip
    def test_sensortypes_remote(self):
        """Does Synching of sensortypes work as expected
        
        Sensortypes should be synchronised across all servers.
        Additionally, no sensortype should have an id conflict.
        """


        rurl = "{0}sensortype/".format(RESTURL)


        #First thing to check is that our local version of the database is as expected
        session = self.Session()
        qry = session.query(models.SensorType)

        #As many sensor types as expected
        self.assertEqual(qry.count(), 59)

        #So Lets delete a couple of sensortypes and check they get added back
        qry = session.query(models.SensorType).filter_by(id=1)
        qry.delete()
        qry = session.query(models.SensorType).filter_by(id=3)
        qry.delete()
        session.flush()
        session.commit()
        
        #So now we have removed the sensortypes we need to check they come back
        self.pusher.sync_sensortypes()

        session = self.Session()
        qry = session.query(models.SensorType)
        #As many sensor types as expected
        self.assertEqual(qry.count(), 59)
        qry = session.query(models.SensorType).filter_by(name="Delta Temperature")
        item = qry.first()
        self.assertTrue(item)
        self.assertEquals(item.id, 1)
        qry = session.query(models.SensorType).filter_by(name="Delta Humidity")
        item = qry.first()
        self.assertTrue(item)
        self.assertEquals(item.id, 3)
        session.flush()
        session.commit()
        session.close()


        """What happens if we have more on the local server"""
        session = self.Session()
        sensor = models.SensorType(id=5000,
                                   name="Foo Sensor")
        session.add(sensor)
        session.flush()
        session.commit()
        
        #Now push
        self.pusher.sync_sensortypes()
        qry = requests.get(rurl)
        self.assertEqual(len(qry.json()), 60)

        self.assertEqual(qry.json()[59]["name"], "Foo Sensor")

        #Finally remove the new objects we have added
        session = self.Session()
        qry = session.query(models.SensorType).filter_by(id = 5000)
        qry.delete()
        session.flush()
        session.commit()

        session = self.rSession()
        qry = session.query(models.SensorType).filter_by(id = 5000)
        qry.delete()
        session.flush()
        session.commit()
        

    #@unittest.skip
    def test_sensortypes_fails(self):
        """Does the sensortype fail if we have bad sensortypes"""
        session = self.Session()
        qry = session.query(models.SensorType).filter_by(id=0)
        #change the paramertes
        sensor = qry.first()
        sensor.name="FOOBAR"
        session.flush()
        session.commit()
        session.close()

        with self.assertRaises(RestPusher.MappingError):
            self.pusher.sync_sensortypes()

        #And reset the details of the node
        session = self.Session()
        qry = session.query(models.SensorType).filter_by(id=0)
        #change the paramertes
        sensor = qry.first()
        sensor.name="Temperature"
        session.flush()
        session.commit()
        session.close()


    #unittest.skip
    def test_sync_roomtypes(self):
        """Does the sync_roomtypes() code work

        #Houses should have three types of behaviour.
        
        1) If nothing has changed then we want to leave the items as is
        2) If there are room on the local that are not on the remote, we upload them
        3) If there are rooms on the remote that are not on the local then they get downloaded.

        However, there may be a difference in roomIds (this is stored as a mapping)
        """

        # Make sure the DB is in a sensible state before we get started
        session = self.Session()
        qry = session.query(models.RoomType).filter(models.RoomType.id > 4)
        qry.delete()
        session.flush()
        session.commit()
        session.close()
        import time
        time.sleep(1)
        session = self.Session()
        session.execute("ALTER TABLE RoomType AUTO_INCREMENT = 1;") #Reset AutoIncrememebt
        session.close()
        

        session = self.rSession()
        qry = session.query(models.RoomType).filter(models.RoomType.id > 4)
        qry.delete()
        session.flush()
        session.commit()
        session.close()
        session = self.rSession()
        session.execute("ALTER TABLE RoomType AUTO_INCREMENT = 1;")
        session.commit()
        session.close()  
        

        #And we also want to make sure the remote has what we expect
        rurl = "{0}roomtype/".format(RESTURL)
               
        #First makesure nothing is added or taken away
        self.assertTrue(self.pusher.sync_roomtypes())

        session = self.Session()
        qry = session.query(models.RoomType)
        self.assertEqual(qry.count(), 4)

        #So Lets add a local room type
        theroom = models.RoomType(id=5,
                                  name="Testing Room",
                                  )    
        session.add(theroom)
        session.flush()
        session.commit()
        session.close()

        session = self.Session()
        qry = session.query(models.RoomType)
        self.assertEqual(qry.count(), 5)
        self.assertTrue(self.pusher.sync_roomtypes())
        #See if it has appeared
        qry = requests.get(rurl)
        self.assertEqual(len(qry.json()),5)
        self.assertEqual(qry.json()[4],
                         {"__table__": "RoomType",
                          "name": "Testing Room",
                          "id": 5})                                  

        #Then add one to the remote side of things
        theroom = models.RoomType(id=10,
                                  name="More Testing")
        requests.post(rurl,data=theroom.json())
        qry = requests.get(rurl)
        #self.assertEqual(len(qry.json()),6)
        session.close()

        self.assertTrue(self.pusher.sync_roomtypes())

        
        session = self.Session()
        #We should now have a room type with a different Id
        qry = session.query(models.RoomType).filter_by(name="More Testing").first()
        self.assertTrue(qry)
        self.assertEquals(qry.id, 6)

        #We need to also make sure that the mapping is correct
        mappings =  self.pusher.mappedRoomTypes
        #Should be dict of {remote : local}
        thedict = {1:1, 2:2, 3:3, 4:4, 5:5, 10:6}
        self.assertEqual(mappings, thedict)

        # ------  Clean up after ourselves ----------

        session = self.Session()
        qry = session.query(models.RoomType).filter(models.RoomType.id > 4)
        qry.delete()
        session.flush()
        session.commit()
        session.close()
        

        session = self.rSession()
        qry = session.query(models.RoomType).filter(models.RoomType.id > 4)
        qry.delete()
        session.flush()
        session.commit()
        session.close()   

        self.pusher.mappedRoomTypes = {}

    #@unittest.skip
    def test_syncRooms(self):
        """Check if sync-rooms works correctly"""

        # Make sure the DB is in a sensible state before we get started
        session = self.Session()
        qry = session.query(models.Room).filter(models.Room.id > 12)
        qry.delete()
        session.flush()
        session.commit()
        session.execute("ALTER TABLE Room AUTO_INCREMENT = 1;") #Reset AutoIncrememebt
        session.close()
        

        session = self.rSession()
        qry = session.query(models.Room).filter(models.Room.id > 12)
        qry.delete()
        session.flush()
        session.commit()
        session.execute("ALTER TABLE Room AUTO_INCREMENT = 1;")
        session.close()  

        session = self.Session()
        rurl = "{0}room/".format(RESTURL)

        #Initial Synching shouldnt change anything
        self.assertTrue(self.pusher.sync_rooms())
        qry = session.query(models.Room)
        #Do we have the expected number of rooms
        self.assertEqual(qry.count(), 12)

        rurl = "{0}room/".format(RESTURL)
        qry = requests.get(rurl)
        self.assertEqual(len(qry.json()), 12)

        #Check our mappings are correct
        thedict = {}
        for x in range(1,13):
            thedict[x] = x

        self.assertEqual(thedict, self.pusher.mappedRooms)

        #Add a local room
        theRoom = models.Room(id=13,
                              name="Testing Room",
                              roomTypeId=1)
        session.add(theRoom)
        session.flush()
        session.commit()
        session.close()

        self.assertTrue(self.pusher.sync_rooms())

        session = self.Session()
        qry = session.query(models.Room)
        #Do we have the expected number of rooms
        self.assertEqual(qry.count(), 13)

        qry = requests.get(rurl)
        self.assertEqual(len(qry.json()), 13)

        #And a new remote room
        theroom = models.Room(id=20,
                              name="Another Testing",
                              roomTypeId=1)
        #Add to remote via rest
        requests.post(rurl, data=theroom.json())
        
        session.close()
        
        self.assertTrue(self.pusher.sync_rooms())

        session = self.Session()
        qry = session.query(models.Room)
        #Do we have the expected number of rooms
        self.assertEqual(qry.count(), 14)

        qry = requests.get(rurl)
        self.assertEqual(len(qry.json()), 14)
        
        thedict[13] = 13
        thedict[20] = 14

        self.assertEqual(thedict, self.pusher.mappedRooms)

        #And Cleanup
        session = self.Session()
        qry = session.query(models.Room).filter(models.Room.id > 12)
        qry.delete()
        session.flush()
        session.commit()
        session.close()
        
        session = self.rSession()
        qry = session.query(models.Room).filter(models.Room.id > 12)
        qry.delete()
        session.flush()
        session.commit()
        session.close()  

        self.pusher.mappedRooms = {}


    #@unittest.skip
    def test_syncDeployments(self):
        """Does Syncronising deployments work correctly

        Another Bi-Directional Sync"""

        # Make sure the DB is in a sensible state before we get started
        session = self.Session()
        qry = session.query(models.Deployment).filter(models.Deployment.id > 1)
        qry.delete()
        session.flush()
        session.commit()
        session.execute("ALTER TABLE Deployment AUTO_INCREMENT = 1;") #Reset AutoIncrememebt
        session.close()
        

        session = self.rSession()
        qry = session.query(models.Deployment).filter(models.Deployment.id > 1)
        qry.delete()
        session.flush()
        session.commit()
        session.execute("ALTER TABLE Deployment AUTO_INCREMENT = 1;")
        session.close()  

        rurl = "{0}deployment/".format(RESTURL)

        session = self.Session()
        qry = session.query(models.Deployment)
        self.assertEqual(qry.count(), 1)

        qry = requests.get(rurl)
        self.assertEqual(len(qry.json()), 1)

        #Add a local deployment
        theDeployment = models.Deployment(id=2,
                                          name="Test Deployment",
                                          description="Test")
        session.add(theDeployment)
        session.flush()
        session.commit()
        session.close()

        self.pusher.sync_deployments()

        #We should now have two at each end
        session = self.Session()
        qry = session.query(models.Deployment)
        self.assertEqual(qry.count(), 2)

        qry = requests.get(rurl)
        self.assertEqual(len(qry.json()), 2)
        session.close()
        
        #Check Mappings
        thedict = {1:1, 2:2}
        self.assertEqual(thedict, self.pusher.mappedDeployments)

        #And add a remote version
        theDeployment = models.Deployment(id=10,
                                name="Foobar",
                                )

        requests.post(rurl, theDeployment.json())

        self.pusher.sync_deployments()        

        #We should now have three at each end
        session = self.Session()
        qry = session.query(models.Deployment)
        self.assertEqual(qry.count(), 3)

        qry = requests.get(rurl)
        self.assertEqual(len(qry.json()), 3)
        session.close()
        
        #Check Mappings
        thedict = {1:1, 2:2, 10:3}
        self.assertEqual(thedict, self.pusher.mappedDeployments)
       
        # Make sure the DB is in a sensible state before we get started
        session = self.Session()
        qry = session.query(models.Deployment).filter(models.Deployment.id > 1)
        qry.delete()
        session.flush()
        session.commit()
        #session.execute("ALTER TABLE Deployment AUTO_INCREMENT = 1;") #Reset AutoIncrememebt
        session.close()
        

        session = self.rSession()
        qry = session.query(models.Deployment).filter(models.Deployment.id > 1)
        qry.delete()
        session.flush()
        session.commit()
        #session.execute("ALTER TABLE Deployment AUTO_INCREMENT = 1;")
        session.close()  

        self.pusher.mappedDeployment = {}

    @unittest.skip
    def test_loadsavemappings(self):
        """Test the Load / Save mappings function

        Code based on what is saved in the save mappings function.
        IE we should get back what we saved
        """

        #First up lets test the save mappings
        #deployment / house / location / room

        #Create some fake mappings
        deployments = {1:1}
        houses = {1:1, 2:2, 5:3}
        locations = {1:1, 2:2, 3:3, 4:6, 5:5, 6:4}
        rooms = {1:1, 2:2}

        self.pusher.mappedDeployments = deployments
        self.pusher.mappedHouses = houses
        self.pusher.mappedLocations = locations
        self.pusher.mappedRooms = rooms
        
        self.pusher.save_mappings()

        #For this version we need to do a forced restart of the push server
        server = RestPusher.PushServer(configfile="test.conf")
        pusher = server.synclist[0]

        # #Now remove everything we have just set and reload
        # pusher.mappedDeployments = {}
        # pusher.mappedHouses = {}
        # pusher.mappedLocations = {}
        # pusher.mappedRooms = {}

        pusher.load_mappings()
        self.assertEqual(pusher.mappedDeployments, deployments)
        self.assertEqual(pusher.mappedHouses, houses)
        self.assertEqual(pusher.mappedLocations, locations)
        self.assertEqual(pusher.mappedRooms, rooms)
        # #self.Fail()

    #@unittest.skip
    def test_sync_houses(self):

        # Make sure the DB is in a sensible state before we get started
        session = self.Session()
        qry = session.query(models.House).filter(models.House.id > 2)
        qry.delete()
        qry = session.query(models.Deployment).filter(models.Deployment.id > 1)
        qry.delete()
        session.flush()
        session.commit()
        session.execute("ALTER TABLE House AUTO_INCREMENT = 1;") #Reset AutoIncremement
        session.commit()
        session.close()
        

        session = self.rSession()
        qry = session.query(models.House).filter(models.House.id > 2)
        qry.delete()
        qry = session.query(models.Deployment).filter(models.Deployment.id > 1)
        qry.delete()
        session.flush()
        session.commit()
        session.execute("ALTER TABLE House AUTO_INCREMENT = 1;")
        session.execute("ALTER TABLE Deployment AUTO_INCREMENT = 1;") #We also need to reset deployments
        session.commit()
        session.close()  

        rurl = "{0}house/".format(RESTURL)
        #Reset mapped houses
        self.pusher.mappedHouses = {}
        #Check that the push works first time around
        houses = {1:1, 2:2}
        self.pusher.sync_houses()
        self.assertEqual(self.pusher.mappedHouses, houses)

        #Next test is a simple sync between houses with matching details
        testHouse = models.House(id=3,
                                 deploymentId=1,
                                 address="test address")
        session = self.Session()
        session.add(testHouse)
        session.flush()
        session.commit()


        #Push the same house to the remote db
        #req = requests.post(rurl, testHouse.json())

        session.close()
        #And see if our push updates correctly
        self.pusher.sync_houses()
        self.assertEqual(self.pusher.mappedHouses,
                         {1:1,2:2,3:3})
        

        #Now map a house to a new ID in the database
        testHouse = models.House(id=10,
                                 deploymentId=1,
                                 address="second test")
        session = self.Session()
        session.add(testHouse)
        session.flush()
        session.commit()

        #Remap to we have Id 10 instead
        jhouse = testHouse.dict()
        session.close()

        #req = requests.post(rurl, jhouse)
        
        #And check if we update coreretly
        self.pusher.sync_houses()
        self.assertEqual(self.pusher.mappedHouses,
                         {1:1, 2:2, 3:3, 10:4})

        # req = requests.get(rurl)
        # jsn = req.json()
        # self.assertEqual(len(jsn), 4)
        # self.assertEqual(jsn[0]["id"], 1)
        # self.assertEqual(jsn[1]["id"], 2)
        # self.assertEqual(jsn[2]["id"], 3)
        # self.assertEqual(jsn[3]["id"], 4)

        #We also want to make sure the deployments map properly
        #As this would normally be taken care of earlier in the process we need to 
        #Do a quick sync here
        session = self.Session()
        newdeployment = models.Deployment(id=10,
                                          name="Testing Deployment")
        session.add(newdeployment)
        session.flush()
        session.commit()
        self.pusher.sync_deployments()

        #Check deploymets worked properly
        self.assertEqual(self.pusher.mappedDeployments,
                         {1:1, 10:2})


        testHouse = models.House(id=6,
                                 deploymentId=10,
                                 address="Mixed Test")
        session.add(testHouse)
        session.flush()        
        session.commit()
        session.close()
        #self.pusher.log.setLevel(logging.DEBUG)
        self.pusher.sync_houses()

        #self.fail()
        #return
        #First do we have a new house mapped.
        self.assertEqual(self.pusher.mappedHouses,
                         {1:1, 2:2, 3:3, 10:4, 6:5})
        #return
        #But do we also have everything correct at the remote
        req = requests.get("{0}5".format(rurl))
        jsn = req.json()[0]
        
        self.assertEqual(jsn["id"], 5)
        self.assertEqual(jsn["deploymentId"], 2)

        
        
        #Finally we want to ensure that no remote houses are picked up
        newhouse = models.House(id=8,
                                address="Excluded House")
        requests.post(rurl,newhouse.json())
        self.pusher.sync_houses()

        #So is this local
        session = self.Session()
        qry = session.query(models.House)
        self.assertEqual(qry.count(), 5)

        qry = requests.get(rurl)
        jsn = qry.json()
        self.assertEqual(len(jsn), 6)

        #return
        #Cleanup
        session = self.Session()
        qry = session.query(models.House).filter(models.House.id > 2)
        qry.delete()
        qry = session.query(models.Deployment).filter(models.Deployment.id > 2)
        qry.delete()
        session.flush()
        session.commit()
        session.close()
        

        session = self.rSession()
        qry = session.query(models.House).filter(models.House.id > 2)
        qry.delete()
        qry = session.query(models.Deployment).filter(models.Deployment.id > 2)
        qry.delete()
        session.flush()
        session.commit()
        session.close()  


    def test_sync_locations(self):
        """Does Synching Locations work as expected.

        Syncing locations will add any new locations to the DB if they do
        not all ready exist.

        However, as with houses, there may be some differences between BOTH
        the houseid and the room Id.

        Therefore we need to test that:
        1) Simple Synchroniseation works and the ID's are mapped correctly
        2) No Locations are pulled from the remote server

        3) Sycnronisation on new items with existing houses / rooms works correctly
        4) Syncronisation of new items with new houses works correctly
        5) Synchronisation of new items with new rooms works correctly

        """

        session = self.Session()
        qry = session.query(models.Location).filter(models.Location.id > 4)
        qry.delete()
        qry = session.query(models.House).filter(models.House.id > 2)
        qry.delete()
        session.flush()
        session.commit()
        session.execute("ALTER TABLE Location AUTO_INCREMENT = 1;") #Reset AutoIncremement
        #session.execute("ALTER TABLE House AUTO_INCREMENT = 1;") #Reset AutoIncremement
        session.commit()
        session.close()
        

        session = self.rSession()
        qry = session.query(models.Location).filter(models.Location.id > 4)
        qry.delete()
        qry = session.query(models.House).filter(models.House.id > 2)
        qry.delete()
        session.flush()
        session.commit()
        session.execute("ALTER TABLE Location AUTO_INCREMENT = 1;")
        session.execute("ALTER TABLE House AUTO_INCREMENT = 1;") #Reset AutoIncremement
        session.commit()
        session.close()  


        rurl = "{0}Location/".format(RESTURL)


        self.pusher.sync_simpletypes()
        self.pusher.sync_houses()
        
        #Then check that locations work as expected
        self.pusher.sync_locations()
        #Initial set of loactions
        locdict = {1:1, 2:2, 3:3, 4:4}
        self.assertEqual(locdict, self.pusher.mappedLocations)
        
        #The next thing to test is wheter new locations get added using an existing rooms.
        self.assertEqual(self.pusher.mappedRooms[3], 3) #Sanity check
        self.assertEqual(self.pusher.mappedRooms[4], 4)

        session = self.Session()
        newloc = models.Location(houseId=1,
                                 roomId=3)
        session.add(newloc)
        newloc = models.Location(houseId=2,
                                 roomId=3)
        session.add(newloc)
        session.flush()
        session.commit()
        session.close()
        
        self.pusher.sync_locations()
        locdict[5] = 5
        locdict[6] = 6
        self.assertEqual(locdict, self.pusher.mappedLocations)

        req = requests.get(rurl)
        jsn = req.json()
        self.assertEqual(len(jsn), 6)


        #Then we can map locations with different ID's
        session = self.Session()
        newloc = models.Location(id=10,
                                 houseId=1,
                                 roomId=4)
        session.add(newloc)
        newloc = models.Location(id=11,
                                 houseId=2,
                                 roomId=4)
        session.add(newloc)
        session.flush()
        session.commit()
        session.close()
        
        self.pusher.sync_locations()
        #Add new items and check they exists
        locdict[10] = 7
        locdict[11] = 8
        self.assertEqual(locdict, self.pusher.mappedLocations)
        req = requests.get(rurl)
        jsn = req.json()
        self.assertEqual(len(jsn), 8)
        
        #Finally Check that locations that have nothing to do with this project are not in the DB

        session = self.rSession()
        newhouse = models.House(address="Location Test")
        session.add(newhouse)

        newitem = models.Location(id=9,
                                  houseId=newhouse.id,
                                  roomId=1)
        session.add(newitem)
        session.flush()
        session.commit()
        session.close()

        req = requests.get(rurl) #Does it exist on the remote
        jsn = req.json()
        for item in jsn:
            print item
        
        self.assertEqual(len(jsn), 9)
        
        session = self.Session()
        qry = session.query(models.Location)
        self.assertEqual(qry.count(), 8)


        #Cleanup
        session = self.Session()
        qry = session.query(models.Location).filter(models.Location.id > 4)
        qry.delete()
        qry = session.query(models.House).filter(models.House.id > 2)
        qry.delete()
        session.flush()
        session.commit()
        #session.execute("ALTER TABLE Location AUTO_INCREMENT = 1;") #Reset AutoIncremement
        #session.execute("ALTER TABLE House AUTO_INCREMENT = 1;") #Reset AutoIncremement
        session.commit()
        session.close()
        

        session = self.rSession()
        qry = session.query(models.Location).filter(models.Location.id > 4)
        qry.delete()
        qry = session.query(models.House).filter(models.House.id > 2)
        qry.delete()
        session.flush()
        session.commit()
        session.execute("ALTER TABLE Location AUTO_INCREMENT = 1;")
        session.execute("ALTER TABLE House AUTO_INCREMENT = 1;") #Reset AutoIncremement
        session.commit()
        session.close()  


    #@unittest.skip
    def test_Zsyncnodes(self):
        """Test the syncNodes function

        Node Syncing should do several things.

        1) Any nodes that do not exist at either end of the system should be
        added, along with corresponding node types / sensors etc.

        #Not currently implemented 

        2) If the location of the node has been
        updated on the sink, then this needs to be pulled to the remote device
        3) If the location of the node has been updated on the remote, then this
        needs to be pushed to the sink
        """
        
        #Clear out the cruft
        session = self.Session()
        qry = session.execute("TRUNCATE NodeLocation")
        qry = session.query(models.Node).filter(models.Node.id > 1100)
        qry.delete()
        qry = session.query(models.Location).filter(models.Location.id > 6)
        qry.delete()
        session.flush()
        session.commit()
        session.close()

        session = self.rSession()
        qry = session.execute("TRUNCATE NodeLocation")
        qry = session.query(models.Node).filter(models.Node.id > 1100)
        qry.delete()
        qry = session.query(models.Location).filter(models.Location.id > 6)
        qry.delete()
        session.flush()
        session.commit()
        session.close()

        #And fake mapping locations
        self.pusher.mappedLocations = {1:1, 2:2, 3:3, 4:4, 5:5, 6:6}
        
        rurl = "{0}node/".format(RESTURL)

        #Check everything is as we expect
        session = self.Session()
        qry = session.query(models.Node)
        self.assertEqual(qry.count(), 4)
        session.close()

        session = self.rSession()
        qry = session.query(models.Node)
        self.assertEqual(qry.count(), 4)
        session.close()

        #First test should be to check if we DONT actually sync anythin
        #As there should be no difference in the nodes
        self.pusher.sync_nodes()
        session = self.Session()
        qry = session.query(models.Node)
        self.assertEqual(qry.count(), 4)
        session.close()

        session = self.rSession()
        qry = session.query(models.Node)
        self.assertEqual(qry.count(), 4)
        session.close()
        
        #Lets add a new node to the local system (Without location or nodetype)
        session = self.Session()
        thenode = models.Node(id=2000,
                              locationId=None,
                              nodeTypeId=None)
        session.add(thenode)
        session.commit()

        self.pusher.sync_nodes()

        session = self.Session()
        qry = session.query(models.Node)
        self.assertEqual(qry.count(), 5)
        session.close()

        #So we should now have 5 nodes on both the source and sink
        session = self.rSession()
        qry = session.query(models.Node)
        self.assertEqual(qry.count(), 5)
        qry = session.query(models.Node).filter_by(id=2000).first()
        self.assertTrue(qry)
        self.assertEqual(qry.id, 2000)
        self.assertFalse(qry.locationId)
        self.assertFalse(qry.nodeTypeId)
        session.close()


        #Test if updates with both location and nodetype go through correctly
        #(Where there is a straight mapping)
        session = self.Session()
        newnode = models.Node(id=2001,
                              nodeTypeId=1,
                              locationId=1)
        session.add(newnode)

        newnode = models.Node(id=2002,
                              nodeTypeId=1,
                              locationId=None)
        session.add(newnode)
        session.commit()
        session.close()
        self.pusher.sync_nodes()
        
        session = self.rSession()
        qry = session.query(models.Node)
        self.assertEqual(qry.count(), 7)
        qry = session.query(models.Node).filter_by(id=2001).first()
        self.assertTrue(qry)
        self.assertEqual(qry.nodeTypeId, 1)
        self.assertEqual(qry.locationId, 1)

        qry = session.query(models.Node).filter_by(id=2002).first()
        
        self.assertTrue(qry)
        self.assertEqual(qry.nodeTypeId, 1)
        self.assertEqual(qry.locationId, None)        
        session.close()

        #Finally add a new location fake mappings and work with it
        session = self.Session()
        newloc = models.Location(id=20,
                                 houseId = 1,
                                 roomId = 5)
        session.add(newloc)
        newnode = models.Node(id=2003,
                              locationId = 20,
                              nodeTypeId = 1)
        session.add(newnode)
        session.commit()
        session.flush()

        session = self.rSession()
        newloc = models.Location(id=10,
                                 houseId = 1,
                                 roomId = 5)
        session.add(newloc)
        session.commit()
        session.flush()

        #Fake mapping the location
        self.pusher.mappedLocations[20] = 10

        #The push
        self.pusher.sync_nodes()
        
        #And check it has been updated correctly
        session = self.rSession()
        qry = session.query(models.Node).filter_by(id=2003).first()
        self.assertTrue(qry)
        self.assertEquals(qry.locationId, 10) #Has it mapped properly
        session.close()
       
        #self.Fail()
        #Clear out the cruft
        session = self.Session()
        qry = session.execute("TRUNCATE NodeLocation")
        qry = session.query(models.Node).filter(models.Node.id > 1100)
        qry.delete()
        qry = session.query(models.Location).filter(models.Location.id > 6)
        qry.delete()
        session.flush()
        session.commit()
        session.close()

        session = self.rSession()
        qry = session.execute("TRUNCATE NodeLocation")
        qry = session.query(models.Node).filter(models.Node.id > 1100)
        qry.delete()
        qry = session.query(models.Location).filter(models.Location.id > 6)
        qry.delete()
        session.flush()
        session.commit()
        session.close()



    @unittest.skip
    def test_uploadreadings(self):
        """Does the uploading of readings happen correctly"""
        self.Fail()

    @unittest.skip
    def test_uploadnodestate(self):
        """Do we upload nodestates correctly"""
        rSession = self.rSession()
        qry = rSession.query(models.House)
        print
        print "+______REMOPTE_______"
        for item in qry:
            print item


        session = self.Session()
        print "------- LOCAL --------"
        qry = session.query(models.House)
        for item in qry:
            print item
        self.Fail()


