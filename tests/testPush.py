"""
Testing for the Deployment Module

:author: Dan Goldsmith <djgoldsmith@googlemail.com>
"""

"""

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
        rEngine = sqlalchemy.create_engine(remoteUrl.dburl)

        push.initRemote(rEngine)
        #SEtup Local Connection
        push.initLocal(self.localEngine)
        self.push = push
            
    #def setUp(self):
    #    """Overload the setup function so we do not do the transaction wrapping"""
    #    pass

    #def tearDown(self):
    #    """Overload the teardown function so we do not do the transaction wrapping"""
    #    pass

            
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

    #@unittest.skip("Skip this for a second")
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

        #Add the node back to the remoteDB
        remoteSession.add(models.Node(id=theNode.id,
                                      locationId=theNode.locationId,
                                      nodeTypeId=theNode.nodeTypeId))
        remoteSession.commit()

    #@unittest.skip("Skip this for a second")
    def testSingleSync(self):
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
        print "{0}".format("-="*30)
        print "Pre {0}".format(theNode)
        remoteSession.delete(theNode)
        remoteSession.flush()
        remoteSession.commit()
        print "Post: {0}".format(theNode)
        print "{0}".format("-="*30)
        #localNodes = localSession.query(models.Node).all()
        #remoteNodes = remoteSession.query(models.Node).all()
        #self.assertEqual(localNodes,remoteNodes)
        
        #So the node Comparison should return False (No Update Required)
        needsSync = push.checkNodes()
        print "Sync {0}".format(needsSync[0])
        self.assertEqual([theNode],needsSync)

        push.syncNodes(needsSync)
        
        lQry = localSession.query(models.Node).all()
        rQry = remoteSession.query(models.Node).all()
        self.assertEqual(lQry,rQry)

        rQry = remoteSession.query(models.Node).filter_by(id=40).first()
        self.assertTrue(rQry)
        #And Compare old and New databases to make sure they are the same
        #Add the node back to the remoteDB
        #remoteSession.add(theNode)
        #remoteSession.commit()

    #@unittest.skip("Skip this for a second")
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
        session.add(theHumSensor)
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

    

    


if __name__ == "__main__":
    unittest.main()
