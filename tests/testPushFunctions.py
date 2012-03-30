"""
Test individual functions in the Push Module

:author: Dan Goldsmith <djgoldsmith@googlemail.com>
"""

#Python Library Imports
import unittest
from datetime import datetime, timedelta

#Python Module Imports
from sqlalchemy import create_engine
import sqlalchemy.exc

import testmeta

models = testmeta.models

#from cogent.push import remoteModels as remoteModels
import cogent.push.Pusher as Pusher
#REMOTE_URL = "sqlite:///remote.db"
REMOTE_URL = "mysql://root:Ex3lS4ga@localhost/testStore"
LOCAL_URL = "sqlite:///test.db"

class TestPushFunctions(testmeta.BaseTestCase):
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

        #Add an Update Time.  This can be used to increment the "Last update"
        #And avoid problems with the testing script running stuff out of order
        #As our testing DB has 2 days worth of data in it, we need this to be now + 2 days
        #So Lets make it 5 days to be sure
        now = datetime.now() + timedelta(days=5)

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

    def testFunc_syncLocation(self):
        """Test the Push upadate location Function"""
        
        #First we want to pick a location we know about
        lSession = testmeta.Session()
        lQry = lSession.query(models.Location).first()
        remoteLoc = self.push.syncLocation(lQry.id)
        self.assertEqual(lQry.id,remoteLoc.id)
        
    def testFunc_syncLocationNew(self):
        """Test the Push Update Location Function with a new location"""
        lSession = testmeta.Session()
        #Add a new location to the second deployment 
        theHouse = lSession.query(models.House).filter_by(address = "add2").first()
        theRoom = lSession.query(models.Room).filter_by(name="Second Bedroom").first()

        theLocation = models.Location(houseId = theHouse.id,
                                      roomId = theRoom.id)
        lSession.add(theLocation)
        lSession.flush()
        lSession.commit()

        remoteLoc = self.push.syncLocation(theLocation.id)
        self.assertEqual(theLocation.id, remoteLoc.id)
        
        #What happens if we add a new rooms
        newRoom = models.Room(name="Third Bedroom",
                              roomTypeId=1)
        lSession.add(newRoom)
        lSession.flush()

        newLocation = models.Location(houseId = theHouse.id,
                                      roomId = newRoom.id)
        lSession.add(newLocation)
        lSession.flush()
        lSession.commit()

        remoteLoc = self.push.syncLocation(newLocation.id)
        self.assertEqual(newLocation.id,remoteLoc.id)


    def testFunc_syncLocationNewHouse(self):
        """Test if the Push Location Update can deal with new houses and deployments"""

        lSession = testmeta.Session()
        newDeployment = models.Deployment(name="Test Deployment")
        lSession.add(newDeployment)
        
        newHouse = models.House(address="newAddress")
        newHouse.deployment = newDeployment
        lSession.add(newHouse)
        lSession.flush()
        lSession.commit()

        #We also need a location in this House
        theRoom = lSession.query(models.Room).filter_by(name="Second Bedroom").first()
        newLocation = models.Location(houseId = newHouse.id,
                                      roomId = theRoom.id)
        lSession.add(newLocation)
        lSession.flush()
        lSession.commit()
        
        #print "New Location is {0}".format(newLocation)
        remoteLoc = self.push.syncLocation(newLocation.id)
        #print "Remote Location is {0}".format(remoteLoc)
        self.assertEqual(newLocation.id,remoteLoc.id)

    def testRemoteDirect(self):
        """Test to see if making a direct connection to the remote database returns what we expect"""
        push = self.push
        
        #Do we get the same items come back from the database
        #For the Remote
        remotePush = push.testRemoteQuery()
        session = self.remoteSession()
        remoteData = session.query(models.RoomType).all()
        self.assertEqual(remotePush,remoteData)

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

        #Add the node back to the remoteDB so it doesn't confuse future tests 
        remoteSession.add(models.Node(id=theNode.id,
                                      locationId=theNode.locationId,
                                      nodeTypeId=theNode.nodeTypeId))
        remoteSession.commit()


if __name__ == "__main__":
    unittest.main()
