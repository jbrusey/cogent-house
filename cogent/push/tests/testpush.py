""" Unittests for the push script


NOTE:  Not as atomic as they should be.  However, testing becomes a tad tricksy
       when you cannot garuentee that the code runs in order
"""


import unittest
import os
import datetime

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
        #REINIT = True
        if REINIT:
            print "INITIALISING DATABASE"
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
        cls.rSession = sqlalchemy.orm.sessionmaker(bind = remoteengine)

        server = RestPusher.PushServer(configfile="test.conf")
        cls.pusher = server.synclist[0]

        #And a link to that classes session (so we can check everything)
        cls.Session = cls.pusher.localsession

    def setUp(self):
        """Reset all the mappings before running any tests"""
        # Storage for mappings between local -> Remote 
        self.pusher.mappedDeployments = {} 
        self.pusher.mappedHouses = {} 
        self.pusher.mappedRooms = {} 
        self.pusher.mappedLocations = {} 
        self.pusher.backmappedLocations = {} 
        self.pusher.mappedRoomTypes = {} 
        self.pusher.mappedSensorTypes = {} 
        self.pusher.log.setLevel(logging.WARNING)

    @unittest.skip
    def test_connection(self):
        """Can we get an connection"""
        
        self.assertTrue(self.pusher.checkConnection(),
                        msg="No Connection to the test server... Is it running?")

    @unittest.skip
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

        self.pusher.sync_nodetypes()

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
        self.assertEquals(qry.name, "ClusterHead CO2")
        qry = session.query(models.NodeType).filter_by(id=11).first()
        self.assertTrue(qry)
        self.assertEquals(qry.name, "ClusterHead AQ")
        
        #Finally add a new sensor type on the remote server (its a corner case)
        session = self.Session()
        newtype = models.NodeType(id = 5000,
                                  name = "Testing Node")
        session.add(newtype)
        session.commit()
        
        self.pusher.sync_nodetypes()
        #Does it exist on the remote
        session = self.rSession()
        qry = session.query(models.NodeType).filter_by(id = 5000).first()
        print "QUERY {0} ({1}),  Name {2}".format(qry, type(qry), qry.name)
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

    @unittest.skip
    def test_nodetypes_fails(self):
        """Does the NodeType fail if we have bad sensortypes"""
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
        

    @unittest.skip
    def test_sensortypes_remote(self):
        """Does Synching of sensortypes work as expected
        
        Sensortypes should be synchronised across all servers.
        Additionally, no sensortype should have an id conflict.
        """

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
        sensor = models.SensorType(id = 5000,
                                   name = "Foo Sensor")
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
        

    @unittest.skip
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


    @unittest.skip
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
        theroom = models.RoomType(id = 10,
                                  name = "More Testing")
        requests.post(rurl, data = theroom.json())
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

    @unittest.skip
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
        theroom = models.Room(id = 20,
                              name = "Another Testing",
                              roomTypeId = 1)
        #Add to remote via rest
        requests.post(rurl, data = theroom.json())
        
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


    @unittest.skip
    def test_syncDeployments(self):
        """Does Syncronising deployments work correctly

        Another Bi-Directional Sync"""

        # Make sure the DB is in a sensible state before we get started
        session = self.Session()
        qry = session.query(models.House).filter(models.House.id > 2)
        qry.delete()
        qry = session.query(models.Deployment).filter(models.Deployment.id > 1)
        qry.delete()
        session.flush()
        session.commit()
        session.execute("ALTER TABLE Deployment AUTO_INCREMENT = 1;") #Reset AutoIncrememebt
        session.close()
        

        session = self.rSession()
        qry = session.query(models.House).filter(models.House.id > 2)
        qry.delete()
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

    @unittest.skip
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

    @unittest.skip
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
        qry = session.query(models.Node).filter(models.Node.id > 2000)
        qry.delete()
        session.flush()
        
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
        qry = session.query(models.Node).filter(models.Node.id > 2000)
        qry.delete()
        session.flush()

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
        backdict = {1:1, 2:2, 3:3, 4:4}
        self.assertEqual(locdict, self.pusher.mappedLocations)
        self.assertEqual(backdict, self.pusher.backmappedLocations)
        
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
        backdict[5] = 5
        backdict[6] = 6
        self.assertEqual(locdict, self.pusher.mappedLocations)
        self.assertEqual(backdict, self.pusher.backmappedLocations)

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
        backdict[7] = 10
        backdict[8] = 11

        self.assertEqual(locdict, self.pusher.mappedLocations)
        self.assertEqual(backdict, self.pusher.backmappedLocations)
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


    @unittest.skip 
    def test_syncnodes(self):
        #Skip this test as the syncnodes functionaly has changed significantly.
        #Instead the nodelocation test will test the syncnode functionalty
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
        qry = session.execute("TRUNCATE Sensor")
        session.flush()
        session.commit()
        qry = session.query(models.Node).filter(models.Node.id > 1100)
        qry.delete()
        qry = session.query(models.Location).filter(models.Location.id > 6)
        qry.delete()
        session.flush()
        session.commit()
        session.close()

        session = self.rSession()
        qry = session.execute("TRUNCATE NodeLocation")
        qry = session.execute("TRUNCATE Sensor")
        session.commit()
        session.flush()
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

        #Test we can update local nodes only (With a fake mapping)
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
        self.pusher.backmappedLocations[10] = 20

        #The push
        self.pusher.sync_nodes()
        
        #And check it has been updated correctly
        session = self.rSession()
        qry = session.query(models.Node).filter_by(id=2003).first()
        self.assertTrue(qry)
        self.assertEquals(qry.locationId, 10) #Has it mapped properly
        session.close()

        #Check we can pull new nodes from the remote server too
        session = self.rSession()
        newnode = models.Node(id=2005,
                              locationId = 10,
                              nodeTypeId = 1)
        session.add(newnode)
        session.flush()
        session.commit()
        session.close()

        #Is this pulled correctly
        self.pusher.sync_nodes()
        
        session = self.Session()
        qry = session.query(models.Node).filter_by(id=2005).first()
        self.assertTrue(qry)
        self.assertEquals(qry.nodeTypeId, 1)
        self.assertEquals(qry.locationId, 20) #This should map to location 20
        
       
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
    def test_getlastupdate(self):
        """Can we get the date of the last update accurately"""
        #Hopefully nothing yet esists

        session = self.Session()
        thehouse = session.query(models.House).filter_by(id=1).first()
        print thehouse
        lastupdate = self.pusher.get_lastupdate(thehouse)
        expectdate = datetime.datetime(2013,1,10,23,55,00)
        #expectdate = None
        self.assertEqual(lastupdate, expectdate)

    @unittest.skip
    def test_uploadreadings(self):
        """Does the uploading of readings happen correctly"""

        self.pusher.log.setLevel(logging.DEBUG)
        #Clean up
        cutdate = datetime.datetime(2013,2,1,0,0,0)
        session = self.Session()
        qry = session.query(models.Reading).filter(models.Reading.time >= cutdate)
        qry.delete()
        session.flush()
        session.commit()
        session.close()

        session = self.rSession()
        qry = session.query(models.Reading).filter(models.Reading.time >= cutdate)
        qry.delete()
        session.flush()
        session.commit()
        session.close()

        self.pusher.mappingConfig["lastupdate"] = {}
        
        #We also need to fake the mappings
        self.pusher.mappedLocations = {1:1,2:2,3:3,4:4}

        session = self.Session()
        thehouse = session.query(models.House).filter_by(id=1).first()
        secondhouse = session.query(models.House).filter_by(id=2).first()
        output = self.pusher.upload_readings(thehouse, cutdate) #Limit to stuff after the cutoff date
        #The First time around we should have no readings transferred (as everthing should match)
        txcount, lasttx = output

        #expectdate = datetime.datetime(2013,1,10,23,55,00)
        self.assertEqual(txcount, 0)
        self.assertEqual(lasttx, cutdate)

        
        #So lets transfer some readings
        currentdate = cutdate
        enddate = datetime.datetime(2013,2,2,0,0,0) #One day
        session = self.Session()
        while currentdate < enddate:
            thesample = models.Reading(time = currentdate, 
                                       nodeId = 837,
                                       locationId = 1,
                                       typeId = 0,
                                       value = 200)
            session.add(thesample)
            currentdate = currentdate + datetime.timedelta(minutes=5)
        session.flush()
        session.commit()

        output = self.pusher.upload_readings(thehouse, cutdate)
        txcount, lasttx = output
        self.assertEqual(txcount, 287)
        self.assertEqual(lasttx, currentdate-datetime.timedelta(minutes=5)) #Remove 5 mins as that is the actual last sample transferred

        #We should also now have about 11 days worth of samples

        #expectedcount = ((288*10)*2)+288
        session = self.rSession()
        qry = session.query(models.Reading)
        qry = qry.filter(models.Reading.time >= cutdate)
        qry = qry.filter(models.Reading.time <= currentdate)
        self.assertEqual(287, qry.count())
        session.close()

        #And now if we transfer there should be nothing pushed across
        output = self.pusher.upload_readings(thehouse, currentdate)
        txcount, lasttx = output
        self.assertEqual(txcount, 0)
        self.assertEqual(lasttx, currentdate)
        
        #So lets add readings for multiple locations and houses
        enddate = datetime.datetime(2013,2,3,0,0,0) #One day
        session = self.Session()
        while currentdate <= enddate:
            thesample = models.Reading(time = currentdate, 
                                       nodeId = 837,
                                       locationId = 1,
                                       typeId = 0,
                                       value = 400)
            session.add(thesample)
            thesample = models.Reading(time = currentdate, 
                                       nodeId = 838,
                                       locationId = 2,
                                       typeId = 0,
                                       value = 400)
            session.add(thesample)
            thesample = models.Reading(time = currentdate, 
                                       nodeId = 1061,
                                       locationId = 3,
                                       typeId = 0,
                                       value = 400)
            session.add(thesample)
            thesample = models.Reading(time = currentdate, 
                                       nodeId = 1063,
                                       locationId = 4,
                                       typeId = 0,
                                       value = 400)
            session.add(thesample)

            currentdate = currentdate + datetime.timedelta(minutes=5)
        session.flush()
        session.commit()

        cutdate = lasttx
        output = self.pusher.upload_readings(thehouse, cutdate)
        txcount, lasttx = output
        self.assertEqual(txcount,288*2)
        self.assertEqual(lasttx, currentdate-datetime.timedelta(minutes=5))

        #And double check everything on the remote server
        session = self.rSession()
        #House 1, locaition 1 Should now have 12 days of readings (11 with 2 locations 1 with only one)
        expected = (12*288) - 1
        theqry = session.query(models.Reading).filter_by(nodeId=837)
        self.assertEqual(theqry.count(), expected)
        #House 1 location 2 should have 11
        theqry = session.query(models.Reading).filter_by(nodeId=838)
        expected = 11*288
        self.assertEqual(theqry.count(), expected)

        #House two gets a tad more tricksy as we skipped samples for yield calculations
        expected = (288/2)*10 #Skips every other sample
        theqry = session.query(models.Reading).filter_by(nodeId=1061)
        self.assertEqual(theqry.count(), expected)
        expected = round((288*0.6666) * 10) #Approximately 1/3 missing
        theqry = session.query(models.Reading).filter_by(nodeId=1063)
        self.assertEqual(theqry.count(), expected)

        #Finally we want to push stuff from house 2
        session = self.Session()
        secondhouse = session.query(models.House).filter_by(id=2).first()
        output = self.pusher.upload_readings(secondhouse, cutdate)
        txcount,lasttx = output
        self.assertEqual(txcount, 288*2)
        self.assertEqual(lasttx, currentdate - datetime.timedelta(minutes=5))
        session.close()

        cutdate = lasttx

        #Finally, what happens if we hit the maximum number of samples to be transmitted
        self.pusher.pushLimit = 144 #1/2 day
        #self.pusher.log.setLevel(logging.DEBUG)
        #Add some samples
        session = self.Session()
        enddate = datetime.datetime(2013,2,4,0,0,0) #One day
        while currentdate < enddate:
            thesample = models.Reading(time = currentdate, 
                                       nodeId = 837,
                                       locationId = 1,
                                       typeId = 0,
                                       value = 600)
            session.add(thesample)
            thesample = models.Reading(time = currentdate, 
                                       nodeId = 838,
                                       locationId = 2,
                                       typeId = 0,
                                       value = 600)
            session.add(thesample)
            currentdate = currentdate + datetime.timedelta(minutes=5)
        session.flush()
        session.commit()
        session.close()

       
        session = self.Session()
        thehouse = session.query(models.House).filter_by(id=1).first()

        output = self.pusher.upload_readings(thehouse, lasttx)
        txcount, lasttx = output
        self.assertEqual(txcount, (288-1)*2)
        
        #Then we want to ensure that there is nothing left
        output = self.pusher.upload_readings(thehouse, lasttx)
        txcount, lasttx = output
        self.assertEqual(txcount, 0)

        cutdate = datetime.datetime(2013,2,1,0,0,0)
        session = self.Session()
        qry = session.query(models.Reading).filter(models.Reading.time >= cutdate)
        qry.delete()
        session.flush()
        session.commit()
        session.close()

        session = self.rSession()
        qry = session.query(models.Reading).filter(models.Reading.time >= cutdate)
        qry.delete()
        session.flush()
        session.commit()
        session.close()

        

    #@unittest.skip
    def test_uploadnodestate(self):
        """Do we upload nodestates correctly"""
        #self.pusher.log.setLevel(logging.DEBUG)
        cutdate = datetime.datetime(2013,2,1,0,0,0)
        session = self.Session()
        qry = session.query(models.NodeState).filter(models.NodeState.time >= cutdate)
        qry.delete()
        qry = session.query(models.Reading).filter(models.Reading.time >= cutdate)
        qry.delete()
        session.flush()
        session.commit()
        session.close()

        session = self.rSession()
        qry = session.query(models.NodeState).filter(models.NodeState.time >= cutdate)
        qry.delete()
        qry = session.query(models.Reading).filter(models.Reading.time >= cutdate)
        qry.delete()
        session.flush()
        session.commit()
        session.close()

        #So now its time to check if nodestates are updated correctly
        session = self.Session()
        thehouse = session.query(models.House).filter_by(id=1).first()
        #As this will get passed in by the upload readings we need to fetch it now
        lastupdate = self.pusher.get_lastupdate(thehouse)
        expectdate = datetime.datetime(2013,1,10,23,55,00)
        self.assertEqual(lastupdate, expectdate)

        #First off lets make sure that a run without anything to transfer works properly        
        txcount = self.pusher.upload_nodestate(thehouse, lastupdate)
        self.assertEqual(txcount, 0)

        #Now add a load of nodestates for house One
        currentdate = cutdate

        enddate = datetime.datetime(2013,2,2,0,0,0) #One day
        session = self.Session()
        while currentdate < enddate:
            theitem = models.NodeState(time = currentdate,
                                       nodeId = 837)
            session.add(theitem)
            theitem = models.Reading(time = currentdate,
                                     nodeId = 837,
                                     locationId = 1)
            session.add(theitem)
            currentdate = currentdate + datetime.timedelta(minutes=5)
        session.flush()
        session.commit()


        txcount = self.pusher.upload_nodestate(thehouse, lastupdate)
        #Modify last update
        
        self.assertEqual(txcount, 288)
        lastupdate = currentdate

        #currentdate = currentdate - datetime.timedelta(minutes=5)
        #Add nodestates for house One and Two but only push house 1
        enddate = datetime.datetime(2013,2,3,0,0,0)
        while currentdate <= enddate:
            theitem = models.NodeState(time = currentdate,
                                       nodeId = 837)
            session.add(theitem)
            theitem = models.Reading(time = currentdate,
                                     nodeId = 837,
                                     locationId = 1)
            session.add(theitem)
            theitem = models.NodeState(time = currentdate,
                                       nodeId = 838)
            session.add(theitem)
            theitem = models.Reading(time = currentdate,
                                     nodeId = 838,
                                     locationId = 2)
            session.add(theitem)
            theitem = models.NodeState(time = currentdate,
                                       nodeId = 1061)
            session.add(theitem)
            theitem = models.Reading(time = currentdate,
                                     nodeId = 1061,
                                     locationId = 3)
            session.add(theitem)
            theitem = models.NodeState(time = currentdate,
                                       nodeId = 1063)
            session.add(theitem)
            theitem = models.Reading(time = currentdate,
                                     nodeId = 1063,
                                     locationId = 4)
            session.add(theitem)           
            currentdate = currentdate + datetime.timedelta(minutes=5)
        session.flush()
        session.commit()
        session.close()
        txcount = self.pusher.upload_nodestate(thehouse, lastupdate)
        self.assertEqual(txcount, 288*2)

        #Check nothing has been transfered to house2
        node1061expected = 144*10
        node1063expected = 1920 #round(288*0.666*10)
        session = self.rSession()
        qry = session.query(models.NodeState).filter_by(nodeId=837)
        self.assertEqual(qry.count(), 288*12)
        qry = session.query(models.NodeState).filter_by(nodeId=838)
        self.assertEqual(qry.count(), 288*11)
        qry = session.query(models.NodeState).filter_by(nodeId=1061)
        self.assertEqual(qry.count(), node1061expected)
        qry = session.query(models.NodeState).filter_by(nodeId=1063)
        self.assertEqual(qry.count(), node1063expected)
        session.close()

        #Push house2
        session = self.Session()
        thehouse = session.query(models.House).filter_by(id=2).first()
        txcount = self.pusher.upload_nodestate(thehouse, lastupdate)
        self.assertEqual(txcount, 288*2)
        session.close()

        session = self.rSession()
        qry = session.query(models.NodeState).filter_by(nodeId=837)
        self.assertEqual(qry.count(), 288*12)
        qry = session.query(models.NodeState).filter_by(nodeId=838)
        self.assertEqual(qry.count(), 288*11)
        qry = session.query(models.NodeState).filter_by(nodeId=1061)
        self.assertEqual(qry.count(), node1061expected+288)
        qry = session.query(models.NodeState).filter_by(nodeId=1063)
        self.assertEqual(qry.count(), node1063expected+288)
        session.close()
        
        #return
        session = self.Session()
        qry = session.query(models.NodeState).filter(models.NodeState.time >= cutdate)
        qry.delete()
        qry = session.query(models.Reading).filter(models.Reading.time >= cutdate)
        qry.delete()
        session.flush()
        session.commit()
        session.close()

        session = self.rSession()
        qry = session.query(models.NodeState).filter(models.NodeState.time >= cutdate)
        qry.delete()
        qry = session.query(models.Reading).filter(models.Reading.time >= cutdate)
        qry.delete()
        session.flush()
        session.commit()
        session.close()



    @unittest.skip
    def test_uploadnodestate_and_reading(self):
        """Does the sync process work for both nodestate and house?"""

        self.pusher.mappingConfig["lastupdate"] = {}
        cutdate = datetime.datetime(2013,2,1,0,0,0)

        session = self.Session()
        qry = session.query(models.NodeState).filter(models.NodeState.time >= cutdate)
        qry.delete()
        qry = session.query(models.Reading).filter(models.Reading.time >= cutdate)
        qry.delete()
        session.flush()
        session.commit()
        session.close()

        session = self.rSession()
        qry = session.query(models.NodeState).filter(models.NodeState.time >= cutdate)
        qry.delete()
        qry = session.query(models.Reading).filter(models.Reading.time >= cutdate)
        qry.delete()
        session.flush()
        session.commit()
        session.close()

        

        #Check that both the nodestate and reading uploads work together
        #First nothing should be pushed
        session = self.Session()
        thehouse = session.query(models.House).filter_by(id=1).first()
        lastupdate = self.pusher.get_lastupdate(thehouse)
        
        self.pusher.mappedLocations = {1:1,2:2,3:3,4:4}

        #And push
        output = self.pusher.upload_readings(thehouse, lastupdate)
        txcount, lasttx = output
        self.assertEqual(txcount, 0)
        output = self.pusher.upload_nodestate(thehouse, lastupdate)
        self.assertEqual(output,0)

        #Add some readings and nodestates
        currentdate = datetime.datetime(2013,2,1,0,0,0)
        enddate = datetime.datetime(2013,2,2,0,0,0)
        while currentdate < enddate:
            theitem = models.NodeState(time = currentdate,
                                       nodeId = 837,
                                       parent = 1)
            session.add(theitem)
            theitem = models.Reading(time = currentdate,
                                     nodeId = 837,
                                     locationId = 1)
            session.add(theitem)

            theitem = models.NodeState(time = currentdate,
                                       nodeId = 838,
                                       parent = 1)
            session.add(theitem)
            theitem = models.Reading(time = currentdate,
                                     nodeId = 838,
                                     locationId = 2)
            session.add(theitem)

            theitem = models.NodeState(time = currentdate,
                                       nodeId = 1061,
                                       parent = 1)
            session.add(theitem)
            theitem = models.Reading(time = currentdate,
                                     nodeId = 1061,
                                     locationId = 3)
            session.add(theitem)

            theitem = models.NodeState(time = currentdate,
                                       nodeId = 1063,
                                       parent = 1)
            session.add(theitem)
            theitem = models.Reading(time = currentdate,
                                     nodeId = 1063,
                                     locationId = 4)
            session.add(theitem)   
        
            currentdate = currentdate + datetime.timedelta(minutes=5)


        session.flush()
        session.commit()
        session.close()

        #Push House 1

        session = self.Session()
        thehouse = session.query(models.House).filter_by(id=1).first()
        lastupdate = self.pusher.get_lastupdate(thehouse)
        output = self.pusher.upload_readings(thehouse, lastupdate)
        txcount, lasttx = output
        self.assertEqual(txcount, 288*2)
        output = self.pusher.upload_nodestate(thehouse, lastupdate)
        self.assertEqual(output, 288*2)
        session.close()


        #And House 2
        session = self.Session()
        thehouse = session.query(models.House).filter_by(id=2).first()
        lastupdate = self.pusher.get_lastupdate(thehouse)
        output = self.pusher.upload_readings(thehouse, lastupdate)
        txcount, lasttx = output
        self.assertEqual(txcount, 288*2)
        output = self.pusher.upload_nodestate(thehouse, lastupdate)
        self.assertEqual(output, 288*2)
        session.close()

        #Check against expected output.
        session = self.Session()
        lqry = session.query(models.Reading)
        rsession = self.rSession()
        rqry = session.query(models.Reading)

        self.assertEqual(lqry.count(), rqry.count())
        for item in zip(lqry,rqry):
            self.assertEqual(item[0], item[1])
        

        #Check against expected output.
        session = self.Session()
        lqry = session.query(models.NodeState)
        rsession = self.rSession()
        rqry = session.query(models.NodeState)

        self.assertEqual(lqry.count(), rqry.count())
        for item in zip(lqry,rqry):
            self.assertEqual(item[0], item[1])
        


        session = self.Session()
        qry = session.query(models.NodeState).filter(models.NodeState.time >= cutdate)
        qry.delete()
        qry = session.query(models.Reading).filter(models.Reading.time >= cutdate)
        qry.delete()
        session.flush()
        session.commit()
        session.close()

        session = self.rSession()
        qry = session.query(models.NodeState).filter(models.NodeState.time >= cutdate)
        qry.delete()
        qry = session.query(models.Reading).filter(models.Reading.time >= cutdate)
        qry.delete()
        session.flush()
        session.commit()
        session.close()

    def test_update_nodelocations(self):
        
        #Cleanup
        session = self.Session()
        qry = session.query(models.Node).filter(models.Node.id > 2000)
        qry.delete()
        session.flush()
        session.commit()

        session = self.rSession()
        qry = session.query(models.Node).filter(models.Node.id > 2000)
        qry.delete()
        session.flush()
        session.commit()
        

        session = self.Session()
        thehouse = session.query(models.House)
        print "{0} Local Houses {0}".format("-"*20)
        for item in thehouse:
            print "--> {0}".format(item)

        rsession = self.rSession()
        thehouse = session.query(models.House)
        print "{0} Remote Houses {0}".format("-"*20)
        for item in thehouse:
            print "--> {0}".format(item)


        targethouse = thehouse[0]
        secondhouse = thehouse[1]    

        thenode = session.query(models.Node)
        print "{0} Local Nodes {0}".format("-"*20)
        for item in thenode:
            print "--> {0}".format(item)


        rsession = self.rSession()
        thenode = session.query(models.Node)
        print "{0} Remote Nodes {0}".format("-"*20)
        for item in thenode:
            print "--> {0}".format(item)
        rsession.close()

        #Fake location mappings
        self.pusher.mappedLocations = {1:1,
                                       2:1, #Fake mapping of 2 to 1
                                       3:3,
                                       4:4}

        print "{0} Mapped Locations {0}".format("-"*20)

        print self.pusher.mappedLocations
        
        #First test it to see if nodes without a location get 
        #updated properly.
        newnode = models.Node(id=2001)
        session.add(newnode)
        session.flush()
        session.commit()

        #Synchronise
        self.pusher.sync_nodes()
        #self.pusher.sync_nodeLocations(targethouse)
        rsession = self.rSession()
        qry = rsession.query(models.Node).filter_by(id = 2001).first()
        self.assertTrue(qry)
        self.assertEquals(qry.locationId, None)
        rsession.close()

        print "="*80
        print "="*80

        #Next test is to check if new nodes with locations are added correctly
        newnode = models.Node(id=2002,
                              locationId = 1)
        session.add(newnode)
        session.flush()
        session.commit()

        #Synchronise
        #self.pusher.sync_nodeLocations(targethouse)
        self.pusher.sync_nodes()
        rsession = self.rSession()
        qry = rsession.query(models.Node).filter_by(id = 2002).first()
        self.assertTrue(qry)
        self.assertTrue(qry.locationId, 1)
        rsession.close()

        #What happens if a node without a location (ie hasn't been synched) now has one
        qry = session.query(models.Node).filter_by(id = 2001).first()
        qry.locationId = 1
        session.flush()
        session.commit()

        #self.pusher.sync_nodeLocations(targethouse)
        self.pusher.sync_nodes()
        rsession = self.rSession()
        qry = rsession.query(models.Node).filter_by(id = 2001).first()
        self.assertTrue(qry)
        self.assertTrue(qry.locationId, 1)
        rsession.close()

        print "="*80
        print "="*80


        #Move a node to a new house
        qry = session.query(models.Node).filter_by(id = 2001).first()
        qry.locationId = 3
        session.flush()
        session.commit()

        self.pusher.sync_nodes()
        rsession = self.rSession()
        qry = rsession.query(models.Node).filter_by(id = 2001).first()
        self.assertTrue(qry)
        self.assertTrue(qry.locationId, 2)
        rsession.close()
        
        self.pusher.sync_nodes()
        rsession = self.rSession()
        qry = rsession.query(models.Node).filter_by(id = 2001).first()
        self.assertTrue(qry)
        self.assertTrue(qry.locationId, 3)
        rsession.close()        
        
        #Finally add a few more nodes to our second house
        newnode = models.Node(id=2005,
                              locationId = 4)
        session.add(newnode)

        newnode = models.Node(id=2006,
                              locationId = 4)
        session.add(newnode)

        qry = session.query(models.Node).filter_by(id = 2001).first()
        qry.locationId = 4
        session.flush()
        session.commit()

        #self.pusher.sync_nodeLocations(targethouse)
        self.pusher.sync_nodes()
        #self.pusher.sync_nodeLocations(secondhouse)
        
        #Check all is where it should be
        rsession = self.rSession()
        qry = rsession.query(models.Node).filter_by(id = 2001).first()
        self.assertTrue(qry)
        self.assertTrue(qry.locationId, 4)
        
        qry = rsession.query(models.Node).filter_by(id = 2002).first()
        self.assertTrue(qry)
        self.assertTrue(qry.locationId, 2)

        qry = rsession.query(models.Node).filter_by(id = 2005).first()
        self.assertTrue(qry)
        self.assertTrue(qry.locationId, 4)

        qry = rsession.query(models.Node).filter_by(id = 2006).first()
        self.assertTrue(qry)
        self.assertTrue(qry.locationId, 4)
       
        rsession.close()        
        
        #Finally does the mapping part of the code work correctly
        qry = session.query(models.Node).filter_by(id = 2001).first()
        qry.locationId = 2
        session.commit()
        

        #self.pusher.sync_nodeLocations(targethouse)
        self.pusher.sync_nodes()
        
        #As we have faked a mapping between locations 2 -> 1
        #Expect locationid to be 1

        rsession = self.rSession()
        qry = rsession.query(models.Node).filter_by(id=2001).first()
        self.assertTrue(qry.locationId, 1)


        session = self.Session()
        qry = session.query(models.Node).filter(models.Node.id > 2000)
        qry.delete()
        session.flush()
        session.commit()

        session = self.rSession()
        qry = session.query(models.Node).filter(models.Node.id > 2000)
        qry.delete()
        session.flush()
        session.commit()
        
     
    def test_rpc(self):
        print "==== TESTING RPC FUNCTIONALTY ===="

        #Check to see if there is the tunnel command for salford21
        commands = self.pusher.checkRPC(hostname="salford21")
        self.assertEqual(commands[1], ["tunnel"])

        #Check to see if there as no command for a random name
        commands = self.pusher.checkRPC(hostname="random42")
        self.assertFalse(commands[1])

    
    @unittest.skip
    def test_RPCTunnel(self):
        commands = self.pusher.checkRPC(hostname="salford21")
        self.assertEqual(commands[1], ["tunnel"])
        self.pusher.processRPC(commands[0], commands[1])

                            
        
        
        
