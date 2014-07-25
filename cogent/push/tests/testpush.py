""" Unittests for the push script


NOTE:  Not as atomic as they should be.  However, testing becomes a tad tricksy
       when you cannot guarantee that the code runs in order

To get this to work properly we need to do severaal things:

 * Ensure the "remote" machine has an instance of the webserver running
   (use jenkins.ini)
 * Ensure both the local and remote machines have testing database initialised
   #init_pushtest.db
"""


import unittest2 as unittest
import os
import sys
import datetime

import configobj
import requests

import sqlalchemy



import cogent.push.RestPusher as RestPusher
import cogent.base.model as models

import init_testingdb

import logging
logging.getLogger("nosecover3").setLevel(logging.WARNING)

#GLOBALS FOR CHECKS
NUM_SENSORTYPES = 61
CREATE_URL = "http://127.0.0.1:6551/pushdb/testutil/create"
CLEAN_URL = "http://127.0.0.1:6551/pushdb/testutil/clean"
RESTURL = "http://127.0.0.1:6551/pushdb/rest/"
SYNCID = 0

CREATE_URL = "http://cogentee.coventry.ac.uk/pushdb/testutil/create"
CLEAN_URL = "http://cogentee.coventry.ac.uk/pushdb/testutil/clean"
RESTURL = "http://cogentee.coventry.ac.uk/pushdb/rest/"
SYNCID = 1

class TestServer(unittest.TestCase):
    """Code to test that the push server works as expected"""

    @classmethod
    def setUpClass(cls):
        """Unittest setup, ensure we use the correct path
        for the config file
        """
        if sys.prefix  == "/usr":
            conf_prefix = "/" #If its a standard "global" instalation
        else :
            conf_prefix = "{0}/".format(sys.prefix)

        configpath = os.path.join(conf_prefix,
                                  "etc",
                                  "cogent-house",
                                  "push-script")

        configfile = os.path.join(configpath,
                                  "synchronise.conf")

        logging.info("TEST CONFIG {0}".format(configfile))

        cls.configpath = configpath
        cls.configfile = configfile


    def test_init(self):
        """Can we initialise a push server"""
        server = RestPusher.PushServer(configfile=self.configfile)
        self.assertIsInstance(server, RestPusher.PushServer)

    def test_readcondif(self):
        """Is the configuration file read correctly"""
        server = RestPusher.PushServer(configfile="pushtest.conf")

        parser = server.configparser
        self.assertIsInstance(parser, configobj.ConfigObj)

        #And check that we have all the relevant sections
        self.assertTrue(parser["general"])

        #What should we have in the general section
        #tmpdict = {"localurl": "mysql://chuser@localhost/push_test",
        tmpdict = {"localurl": "sqlite:///push_test.db",
                  "pushlimit": '10000',
                  "synctime": '10'}

        self.assertEqual(tmpdict, parser["general"])

        self.assertTrue(parser["locations"])

        tmpdict = {"local":'0',
                   "cogentee":'0',
                   "test":'1',
                   "jenkins" : '1'}

        self.assertEqual(tmpdict, parser["locations"])


        tmpdict = {"resturl": "http://127.0.0.1:6543/rest/"}
        self.assertEqual(parser["local"], tmpdict)

        tmpdict = {"resturl": "http://127.0.0.1:6551/pushdb/rest/"}
        self.assertEqual(parser["test"], tmpdict)

        tmpdict = {"resturl": "http://cogentee.coventry.ac.uk/salford/rest/"}
        self.assertEqual(parser["cogentee"], tmpdict)


    def test_setupClient(self):
        """Does the push client get setup correctly"""

        server = RestPusher.PushServer(configfile="pushtest.conf")

        pushlist = server.synclist
        self.assertEqual(len(pushlist), 2)

        item = pushlist[0]
        self.assertEqual(item.restUrl,
                         "http://127.0.0.1:6551/pushdb/rest/")


class TestClient(unittest.TestCase):
    """ Code to test the rest client """

    @classmethod
    def setUpClass(cls):
        """Create just one instance of the push server to test"""

        #We want to remove any preexisting mapping files
        confpath = "sqlite:---push_test.db_map.conf"
        if os.path.exists(confpath):
            print "DELETING EXISTING CONFIG FILE"
            os.remove(confpath)

        #Relevant DB strings
        localdb = "sqlite:///push_test.db"

        REINIT = False
        #REINIT = True
        if REINIT:
            logging.debug("TEST: Init Database")
            #and initialise the local database
            init_testingdb.main(localdb)
            #And the remote DB
            out = requests.get(CREATE_URL)
            #init_testingdb.main(remotedb)

        #We also want to open a connection to the remote database (so everything
        #can get cleaned up)
        #remoteengine = sqlalchemy.create_engine(remotedb)
        #cls.rSession = sqlalchemy.orm.sessionmaker(bind = remoteengine)

        server = RestPusher.PushServer(configfile="pushtest.conf")
        #print [x.restUrl for x in server.synclist]

        #So If we want to switch to the jenkins db
        cls.pusher = server.synclist[SYNCID]

        #And a link to that classes session (so we can check everything)
        cls.Session = cls.pusher.localsession

    def setUp(self):
        """Reset all the mappings before running any tests"""
        # Storage for mappings between local -> Remote
        self.cleandb()
        self.pusher.mappedDeployments = {}
        self.pusher.mappedHouses = {}
        self.pusher.mappedRooms = {}
        self.pusher.mappedLocations = {}
        self.pusher.backmappedLocations = {}
        self.pusher.mappedRoomTypes = {}
        self.pusher.mappedSensorTypes = {}
        self.pusher.log.setLevel(logging.WARNING)

    def tearDown(self):
        self.cleandb()
    

    def cleandb(self):
        """Remove any testing items from the database"""
        session = self.Session()
        qry = session.query(models.NodeType).filter_by(id = 5000)
        qry.delete()
        session.flush()
        
        qry = session.query(models.Node).filter(models.Node.id > 2000)
        qry.delete()
        session.flush()
        
        qry = session.query(models.Location).filter(models.Location.id > 4)
        qry.delete()
        session.flush()
        
        qry = session.query(models.House).filter(models.House.id > 2)
        qry.delete()
        session.flush()

        qry = session.query(models.Room).filter(models.Room.id > 12)
        qry.delete()
        session.flush()

        qry = session.query(models.Deployment).filter(models.Deployment.id >1)
        qry.delete()
        session.flush()

        qry = session.query(models.SensorType).filter_by(id = 5000)
        qry.delete()
        session.flush()

        qry = session.query(models.RoomType).filter(models.RoomType.id > 4)
        qry.delete()
        session.flush()

        cutdate = datetime.datetime(2013, 2, 1, 0, 0, 0)
        qry = session.query(models.Reading).filter(models.Reading.time >= cutdate)
        qry.delete()
        session.flush()

        qry = session.query(models.NodeState).filter(models.NodeState.time >= cutdate)
        qry.delete()
        session.flush()

        session.commit()

        

        #Clean up remote database
        out = requests.get(CLEAN_URL)
        pass


    def test_connection(self):
        """Can we get an connection"""

        self.assertTrue(self.pusher.checkConnection(),
                        msg="No Connection to the test server.. Is it running?")


    def test_nodetypes_remote(self):
        """Can we properly synch nodetypes

        Like sensor types node types should be synchronised across all server.
        If there is a conflict on node type Id, we should Fail

        """
        rurl = "{0}nodetype/".format(RESTURL)

        #Check that the numbers are as expected
        session = self.Session()
        qry = session.query(models.NodeType)
        lcount = qry.count()
        session.close()

        qry = requests.get(rurl)
        self.assertEqual(len(qry.json()), lcount)

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

        qry = requests.get(rurl, params={"id":5000})
        self.assertEqual(qry.json()[0]["name"], "Testing Node")


    def test_nodetypes_fails(self):
        """Does the NodeType fail if we have bad sensortypes"""

        session = self.Session()
        qry = session.query(models.NodeType).filter_by(id=0)
        #change the name
        sensor = qry.first()
        sensor.name = "FOOBAR"
        session.flush()
        session.commit()
        session.close()

        with self.assertRaises(RestPusher.MappingError):
            self.pusher.sync_nodetypes()

        #And reset the details of the node
        session = self.Session()
        qry = session.query(models.NodeType).filter_by(id=0)
        sensor = qry.first()
        sensor.name = "Base"
        session.flush()
        session.commit()
        session.close()


    def test_sensortypes_remote(self):
        """Does Synching of sensortypes work as expected

        Sensortypes should be synchronised across all servers.
        Additionally, no sensortype should have an id conflict.
        """

        #Remove the new objects we have added
        rurl = "{0}sensortype/".format(RESTURL)

        #First thing to check is that our local version of the database is as
        #expected
        session = self.Session()
        qry = session.query(models.SensorType)

        #As many sensor types as expected
        self.assertEqual(qry.count(), NUM_SENSORTYPES)

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
        self.assertEqual(qry.count(), NUM_SENSORTYPES)
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
        self.assertEqual(len(qry.json()), NUM_SENSORTYPES + 1)

        self.assertEqual(qry.json()[NUM_SENSORTYPES]["name"], "Foo Sensor")


    def test_sensortypes_fails(self):
        """Does the sensortype fail if we have bad sensortypes"""
        session = self.Session()
        qry = session.query(models.SensorType).filter_by(id=0)
        #change the paramertes
        sensor = qry.first()
        sensor.name = "FOOBAR"
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
        sensor.name = "Temperature"
        session.flush()
        session.commit()
        session.close()

    def test_sync_roomtypes(self):
        """Does the sync_roomtypes() code work

        #Houses should have three types of behaviour.

        1) If nothing has changed then we want to leave the items as is
        2) If there are room on the local that are not on the remote:
              we upload them
        3) If there are rooms on the remote that are not on the local:
              they get downloaded.

        However, there may be a difference in roomIds
        (this is stored as a mapping)
        """

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
        self.assertEqual(len(qry.json()), 5)
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
        self.pusher.mappedRoomTypes = {}


    def test_syncRooms(self):
        """Check if sync-rooms works correctly"""

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
        for x in range(1, 13):
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
        self.pusher.mappedRooms = {}


    def test_syncDeployments(self):
        """Does Syncronising deployments work correctly

        Another Bi-Directional Sync"""

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

        self.pusher.mappedDeployment = {}


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
        server = RestPusher.PushServer(configfile="pushtest.conf")
        pusher = server.synclist[SYNCID]


        pusher.load_mappings()
        self.assertEqual(pusher.mappedDeployments, deployments)
        self.assertEqual(pusher.mappedHouses, houses)
        self.assertEqual(pusher.mappedLocations, locations)
        self.assertEqual(pusher.mappedRooms, rooms)


    def test_sync_houses(self):

        # Make sure the DB is in a sensible state before we get started
        session = self.Session()
   
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
        session.close()

        #And check if we update coreretly
        self.pusher.sync_houses()
        self.assertEqual(self.pusher.mappedHouses,
                         {1:1, 2:2, 3:3, 10:4})

        #We also want to make sure the deployments map properly As this would
        #normally be taken care of earlier in the process we need to Do a quick
        #sync here
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
        requests.post(rurl, newhouse.json())
        self.pusher.sync_houses()

        #So is this local
        session = self.Session()
        qry = session.query(models.House)
        self.assertEqual(qry.count(), 5)

        qry = requests.get(rurl)
        jsn = qry.json()
        self.assertEqual(len(jsn), 6)

    def test_sync_locations(self):
        """Does Synching Locations work as expected.

        Syncing locations will add any new locations to the DB if they do
        not all ready exist.

        However, as with houses, there may be some differences between BOTH
        the houseid and the room Id.

        Therefore we need to test that:
        1) Simple Synchroniseation works and the ID's are mapped correctly
        2) No Locations are pulled from the remote server

        3) Sycnronisation on new items with existing houses / rooms works
        4) Syncronisation of new items with new houses works correctly
        5) Synchronisation of new items with new rooms works correctly

        """

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

        #The next thing to test is wheter new locations get added using existing
        #rooms.
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

        #Finally Check that locations that have nothing to do with this project
        #are not in the DB

        #TODO: WORK OUT HOW TO REPLICATE THIS TEST

        # session = self.rSession()
        # newhouse = models.House(address="Location Test")
        # session.add(newhouse)

        # newitem = models.Location(id=9,
        #                           houseId=newhouse.id,
        #                           roomId=1)
        # session.add(newitem)
        # session.flush()
        # session.commit()
        # session.close()

        # req = requests.get(rurl) #Does it exist on the remote
        # jsn = req.json()
        # self.assertEqual(len(jsn), 9)

        # session = self.Session()
        # qry = session.query(models.Location)
        # self.assertEqual(qry.count(), 8)

    def test_getlastupdate(self):
        """Can we get the date of the last update accurately"""
        #Hopefully nothing yet esists

        session = self.Session()
        thehouse = session.query(models.House).filter_by(id=1).first()
        print thehouse
        lastupdate = self.pusher.get_lastupdate(thehouse)
        expectdate = datetime.datetime(2013, 1, 10, 23, 55, 1)
        #expectdate = None
        self.assertEqual(lastupdate, expectdate)


    def test_uploadreadings(self):
        """Does the uploading of readings happen correctly"""

        self.pusher.log.setLevel(logging.DEBUG)
        rurl = "{0}Reading/".format(RESTURL)
        #Clean up
        cutdate = datetime.datetime(2013, 2, 1, 0, 0, 0)

        self.pusher.mappingConfig["lastupdate"] = {}

        #We also need to fake the mappings
        self.pusher.mappedLocations = {1:1, 2:2, 3:3, 4:4}

        session = self.Session()
        thehouse = session.query(models.House).filter_by(id=1).first()
        secondhouse = session.query(models.House).filter_by(id=2).first()
        #Limit to stuff after the cutoff date
        output = self.pusher.upload_readings(thehouse, cutdate)
        #The First time around we should have no readings transferred (as
        #everthing should match)
        txcount, lasttx = output

        self.assertEqual(txcount, 0)
        self.assertEqual(lasttx, cutdate)


        #So lets transfer some readings
        currentdate = cutdate
        enddate = datetime.datetime(2013, 2, 2, 0, 0, 0) #One day
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
        #Remove 5 mins as that is the actual last sample transferred
        self.assertEqual(lasttx, currentdate-datetime.timedelta(minutes=5))

        #We should also now have about 11 days worth of samples
        #expectedcount = ((288*10)*2)+288
        qry = requests.get(rurl, params={"time":["ge_{0}".format(cutdate.isoformat()), 
                                                 "le_{0}".format(currentdate.isoformat())]})

        self.assertEqual(287, len(qry.json()))


        #And now if we transfer there should be nothing pushed across
        output = self.pusher.upload_readings(thehouse, currentdate)
        txcount, lasttx = output
        self.assertEqual(txcount, 0)
        self.assertEqual(lasttx, currentdate)

        #So lets add readings for multiple locations and houses
        enddate = datetime.datetime(2013, 2, 3, 0, 0, 0) #One day
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
        self.assertEqual(txcount, 288*2)
        self.assertEqual(lasttx, currentdate-datetime.timedelta(minutes=5))

        #And double check everything on the remote server
        #TODO:  REPLICATE THIS WITH REQURESTS
        # #House 1, locaition 1 Should now have 12 days of readings (11 with 2 locations 1 with only one)
        expected = (12*288) - 1
        qry = requests.get(rurl, params={"nodeId":837})
        self.assertEqual(expected, len(qry.json()))

        # #House 1 location 2 should have 11
        expected = 11*288
        qry = requests.get(rurl, params={"nodeId":838})
        self.assertEqual(expected, len(qry.json()))

        # #House two gets a tad more tricksy as we skipped samples for yield calculations
        expected = (288/2)*10 #Skips every other sample
        qry = requests.get(rurl, params={"nodeId":1061})
        self.assertEqual(expected, len(qry.json()))
        
        expected = round((288*0.6666) * 10) #Approximately 1/3 missing
        qry = requests.get(rurl, params={"nodeId":1063})
        self.assertEqual(expected, len(qry.json()))
        
        #Finally we want to push stuff from house 2
        session = self.Session()
        secondhouse = session.query(models.House).filter_by(id=2).first()
        output = self.pusher.upload_readings(secondhouse, cutdate)
        txcount, lasttx = output
        self.assertEqual(txcount, 288*2)
        self.assertEqual(lasttx, currentdate - datetime.timedelta(minutes=5))
        session.close()

        cutdate = lasttx

        #Finally, what happens if we hit the maximum number of samples to be transmitted
        self.pusher.pushLimit = 144 #1/2 day
        #self.pusher.log.setLevel(logging.DEBUG)
        #Add some samples
        session = self.Session()
        enddate = datetime.datetime(2013, 2, 4, 0, 0, 0) #One day
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


    def test_uploadnodestate(self):
        """Do we upload nodestates correctly"""
        #self.pusher.log.setLevel(logging.DEBUG)
        rurl = "{0}NodeState/".format(RESTURL)
        cutdate = datetime.datetime(2013, 2, 1, 0, 0, 0)

        #So now its time to check if nodestates are updated correctly
        session = self.Session()
        thehouse = session.query(models.House).filter_by(id=1).first()
        #As this will get passed in by the upload readings we need to fetch it now
        lastupdate = self.pusher.get_lastupdate(thehouse)
        expectdate = datetime.datetime(2013, 1, 10, 23, 55, 1)
        self.assertEqual(lastupdate, expectdate)

        #First off lets make sure that a run without anything to transfer works properly
        txcount = self.pusher.upload_nodestate(thehouse, lastupdate)
        self.assertEqual(txcount, 0)

        #Now add a load of nodestates for house One
        currentdate = cutdate

        enddate = datetime.datetime(2013, 2, 2, 0, 0, 0) #One day
        session = self.Session()
        while currentdate < enddate:
            theitem = models.NodeState(time = currentdate,
                                       nodeId = 837)
            session.add(theitem)
            theitem = models.Reading(time = currentdate,
                                     nodeId = 837,
                                     locationId = 1,
                                     typeId = 0)
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
        enddate = datetime.datetime(2013, 2, 3, 0, 0, 0)
        while currentdate <= enddate:
            theitem = models.NodeState(time = currentdate,
                                       nodeId = 837)
            session.add(theitem)
            theitem = models.Reading(time = currentdate,
                                     nodeId = 837,
                                     locationId = 1,
                                     typeId = 0)
            session.add(theitem)
            theitem = models.NodeState(time = currentdate,
                                       nodeId = 838)
            session.add(theitem)
            theitem = models.Reading(time = currentdate,
                                     nodeId = 838,
                                     locationId = 2,
                                     typeId = 0)
            session.add(theitem)
            theitem = models.NodeState(time = currentdate,
                                       nodeId = 1061)
            session.add(theitem)
            theitem = models.Reading(time = currentdate,
                                     nodeId = 1061,
                                     locationId = 3,
                                     typeId = 0)
            session.add(theitem)
            theitem = models.NodeState(time = currentdate,
                                       nodeId = 1063)
            session.add(theitem)
            theitem = models.Reading(time = currentdate,
                                     nodeId = 1063,
                                     typeId = 0,
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

        ##session = self.rSession()
        qry = requests.get(rurl, params={"nodeId":837})
        self.assertEqual(288*12, len(qry.json()))
        qry = requests.get(rurl, params={"nodeId":838})
        self.assertEqual(288*11, len(qry.json()))
        qry = requests.get(rurl, params={"nodeId":1061})
        self.assertEqual(node1061expected, len(qry.json()))
        qry = requests.get(rurl, params={"nodeId":1063})
        self.assertEqual(node1063expected, len(qry.json()))
        # qry = session.query(models.NodeState).filter_by(nodeId=837)
        # self.assertEqual(qry.count(), 288*12)
        # qry = session.query(models.NodeState).filter_by(nodeId=838)
        # self.assertEqual(qry.count(), 288*11)
        # qry = session.query(models.NodeState).filter_by(nodeId=1061)
        # self.assertEqual(qry.count(), node1061expected)
        # qry = session.query(models.NodeState).filter_by(nodeId=1063)
        # self.assertEqual(qry.count(), node1063expected)
        # session.close()

        #Push house2
        session = self.Session()
        thehouse = session.query(models.House).filter_by(id=2).first()
        txcount = self.pusher.upload_nodestate(thehouse, lastupdate)
        self.assertEqual(txcount, 288*2)
        session.close()


        qry = requests.get(rurl, params={"nodeId":837})
        self.assertEqual(288*12, len(qry.json()))
        qry = requests.get(rurl, params={"nodeId":838})
        self.assertEqual(288*11, len(qry.json()))
        qry = requests.get(rurl, params={"nodeId":1061})
        self.assertEqual(node1061expected+288, len(qry.json()))
        qry = requests.get(rurl, params={"nodeId":1063})
        self.assertEqual(node1063expected+288, len(qry.json()))

        # session = self.rSession()
        # qry = session.query(models.NodeState).filter_by(nodeId=837)
        # self.assertEqual(qry.count(), 288*12)
        # qry = session.query(models.NodeState).filter_by(nodeId=838)
        # self.assertEqual(qry.count(), 288*11)
        # qry = session.query(models.NodeState).filter_by(nodeId=1061)
        # self.assertEqual(qry.count(), node1061expected+288)
        # qry = session.query(models.NodeState).filter_by(nodeId=1063)
        # self.assertEqual(qry.count(), node1063expected+288)
        # session.close()


