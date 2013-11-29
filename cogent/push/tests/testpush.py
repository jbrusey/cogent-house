""" Unittests for the push script


NOTE:  Not as atomic as they should be.  However, testing becomes a tad tricksy
       when you cannot garuentee that the code runs in order
"""


import unittest
import os

import configobj
import requests


RESTURL = "http://127.0.0.1:6543/rest/"

import cogent.push.RestPusher as RestPusher
import cogent.base.model as models

import init_testingdb

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

        REINIT = False
        
        if REINIT:
            if os.path.exists(confpath):
                print "DELETING EXISTING CONFIG FILE"
                os.remove(confpath)

            #TODO: Fix this so no majic strings
            #and create the database
            init_testingdb.main("mysql://chuser@localhost/push_test")
            #And the remote DB
            init_testingdb.main("mysql://chuser@localhost/test")

            #TODO:  Fix this so theres a bit less magic strings
            #We also want to initialise the testing DB
            #init_testingdb.main("sqlite:///home/dang/coding/webinterface/viewer-repo/cogent-house.devel/test.db")

        server = RestPusher.PushServer(configfile="test.conf")
        cls.pusher = server.synclist[0]

        #And a link to that classes session (so we can check everything)
        cls.Session = cls.pusher.localsession

    @unittest.skip
    def test_connection(self):
        """Can we get an connection"""
        
        self.assertTrue(self.pusher.checkConnection(),
                        msg="No Connection to the test server... Is it running?")
        
    @unittest.skip
    def test_sensortypes_remote(self):
        """Does Synching of sensortypes work as expected"""

        #First thing to check is that our local version of the database is as expected
        session = self.Session()
        qry = session.query(models.SensorType)

        #As many sensor types as expected
        self.assertEqual(qry.count(), 59)

        #So Lets delete a couple of sensortypes
        qry = session.query(models.SensorType).filter_by(id=1)
        qry.delete()
        qry = session.query(models.SensorType).filter_by(id=3)
        qry.delete()
        session.flush()
        session.commit()

        session = self.Session()
        qry = session.query(models.SensorType)
        self.assertEqual(qry.count(), 57)
        qry = session.query(models.SensorType).filter_by(name="Delta Temperature")
        self.assertFalse(qry.first())
        qry = session.query(models.SensorType).filter_by(name="Delta Humidity")
        self.assertFalse(qry.first())
        session.flush()
        session.commit()
        session.close()
        
        #So now we have removed the sensortypes we need to check they come back
        self.pusher.sync_sensortypes()

        session = self.Session()
        qry = session.query(models.SensorType)
        #As many sensor types as expected
        self.assertEqual(qry.count(), 59)

        """What happens if we have more on the local server"""
        session = self.Session()
        sensor = models.SensorType(id=5000,
                                   name="Foo Sensor")
        session.add(sensor)
        session.flush()
        session.commit()
        
        #Check we have what we expect
        qry = session.query(models.SensorType)
        self.assertEqual(qry.count(), 60)

        rurl = "{0}sensortype/".format(RESTURL)
        qry = requests.get(rurl)
        self.assertEqual(len(qry.json()), 59)
        
        #Now push
        self.pusher.sync_sensortypes()
        qry = requests.get(rurl)
        self.assertEqual(len(qry.json()), 60)

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

        #Check everything is as expected
        session = self.Session()
        qry = session.query(models.RoomType)
        self.assertEqual(qry.count(), 4)

        #And we also want to make sure the remote has what we expect
        rurl = "{0}roomtype/".format(RESTURL)
        qry = requests.get(rurl)
        self.assertEqual(len(qry.json()),4)
               
        #First makesure nothing is added or taken away
        self.assertTrue(self.pusher.sync_roomtypes())

        qry = session.query(models.RoomType)
        self.assertEqual(qry.count(), 4)


        #So Lets add a local room type
        theroom = models.RoomType(id=5,
                                  name="Testing Room",
                                  )    
        session.add(theroom)
        session.flush()
        session.commit()

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

    @unittest.skip
    def test_syncRooms(self):
        """Check if sync-rooms works correctly"""

        session = self.Session()
        rurl = "{0}room/".format(RESTURL)

        qry = session.query(models.Room)
        #Do we have the expected number of rooms
        self.assertEqual(qry.count(), 12)

        qry = requests.get(rurl)
        self.assertEqual(len(qry.json()), 12)

        #So syncing shouldnt change anything
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

    @unittest.skip
    def test_syncDeployments(self):
        """Another Bi-Directional Sync"""

        rurl = "{0}deployment/".format(RESTURL)

        session = self.Session()
        qry = session.query(models.Deployment)
        self.assertEqual(qry.count(), 1)

        qry = requests.get(rurl)
        self.assertEqual(len(qry.json()), 1)

        #Add a local deployment
        theDeployment = models.Deployment(id=2,
                                          name="Test Deployment",
                                          desctiption="Test")
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
        thedict = {1:1,2:2}
        self.assertEqual(thedict, self.pusher.mappedDeployments)

        #And add a remote version
        theHouse = models.House(id=10,
                                name="Foobar",
                                )

        requests.post(rurl, theHouse.json())

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
        print "------ ORIGINAL MAPPING ---------"
        print self.pusher.mappingConfig
        print "---------------------------------"
        #For this version we need to do a forced restart of the push server
        server = RestPusher.PushServer(configfile="test.conf")
        pusher = server.synclist[0]
        #print "Second version"
        #print pusher.mappingConfig

        # #Now remove everything we have just set and reload
        # pusher.mappedDeployments = {}
        # pusher.mappedHouses = {}
        # pusher.mappedLocations = {}
        # pusher.mappedRooms = {}

        pusher.load_mappings()
        # self.assertEqual(pusher.mappedDeployments, deployments)
        # self.assertEqual(pusher.mappedHouses, houses)
        # self.assertEqual(pusher.mappedLocations, locations)
        # self.assertEqual(pusher.mappedRooms, rooms)
        # #self.Fail()

    @unittest.skip
    def test_syncnodes(self):
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
        self.Fail()


    @unittest.skip
    def test_uploadreadings(self):
        """Does the uploading of readings happen correctly"""
        self.Fail()

    @unittest.skip
    def test_uploadnodestate(self):
        """Do we upload nodestates correctly"""
        self.Fail()
