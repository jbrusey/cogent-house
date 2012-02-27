"""
Test Cases for the Sensor Classes
"""

"""
Testing for the Deployment Module

:author: Dan Goldsmith <djgoldsmith@googlemail.com>
"""

"""
Unfortunately there is quite a bit of try,except blocks here.
This does mean that the same test cases can be shared between the
Pyramid Code, and the Standard Version

If anyone comes up with a better way then let me know.
"""

#Python Library Imports
import unittest
import datetime

#Python Module Imports
import sqlalchemy.exc

try:
    import cogent
except ImportError:
    #Assume we are running from the test directory
    print "Unable to Import Cogent Module Appending Path"
    import sys
    sys.path.append("../")

#Are we working from the base version
try:
    import cogent.base.model as models
    import testmeta
    Session = testmeta.Session
    engine = testmeta.engine
except ImportError,e:
    print "Unable to Import Cogent.base.models Assuming running from Pyramid"
    print "Error was {0}".format(e)

#Or the Pyramid Version
try:
    from pyramid import testing
    import cogentviewer.models as models
    import cogentviewer.models.meta as meta
    import testmeta
    import transaction
except ImportError,e:
    print "Unable to Import Pyramid, Assuming we are working in the Base directory"
    print "Error was {0}".format(e)

from sqlalchemy.exc import FlushError

class TestSensor(unittest.TestCase):
    """
    Deal with tables in the deployment module
    """
    @classmethod
    def setUpClass(self):
        """Called the First time this class is called.
        This means that we can Init the testing database once per testsuite
        """
        testmeta.createTestDB()

    def setUp(self):
        """Called each time a test case is called, I wrap each
        testcase in a transaction, this means that nothing is saved to
        the database between testcases, while still allowing "fake" commits
        in the individual testcases.

        This means there should be no unexpected items in the DB."""

        #Pyramid Version
        try:
            self.config = testing.setUp()
            #Wrap In Transaction to ensure nothing gets saved between test cases
            self.transaction = transaction.begin()
            self.session = meta.Session
        except:
            #We have to do it slightly different for non pyramid applications.
            #We do however get the same functionality.
            connection = engine.connect()
            self.transaction = connection.begin()
            self.session = Session(bind=connection)

    def tearDown(self):
        """
        Called after each testcase,
        Uncommits any changes that test case made
        """
        
        #Pyramid
        try:
            self.transaction.abort()
            testing.tearDown()
        except:
            self.transaction.rollback()
            self.session.close()

    def testCreate(self):
        """Can We Create Sensor Objects"""
        theSensor = models.Sensor()
        self.assertIsInstance(theSensor, models.Sensor)

        theSensorType = models.SensorType()
        self.assertIsInstance(theSensorType,models.SensorType)

    def testParams(self):
        """Can we create and update with parameters"""
        
        theSensor = models.Sensor(calibrationSlope = 1.0,
                                  calibrationOffset = 1.0)

        self.assertEqual(theSensor.calibrationSlope,1.0)
        self.assertEqual(theSensor.calibrationOffset,1.0)

        
    def testUpdate(self):
        theSensor = models.Sensor()
        self.assertIsNone(theSensor.calibrationSlope)
    
        theSensor.update(calibrationSlope = 1.0,
                         calibrationOffset = 1.0)

        self.assertEqual(theSensor.calibrationSlope,1.0)
        self.assertEqual(theSensor.calibrationOffset,1.0)
    
    def testFK(self):
        """
        Test Foreign Keys and backrefs
        """
        session = self.session
        theNode = models.Node(id=11)
        theSType = models.SensorType(id=1,name="test")

        session.add(theNode)
        session.add(theSType)

        theSensor = models.Sensor(sensorTypeId=theSType.id,
                                  nodeId = theNode.id)
        
        session.add(theSensor)
        session.flush()

        #Test that Backrefts to this object work correctly
        self.assertEqual(theSensor.sensorType,theSType)
        self.assertEqual(theSensor.node,theNode)        
        #And from the "parent Objects"
        self.assertIn(theSensor,theNode.sensors)
        self.assertIn(theSensor,theSType.sensors)

        # print ""
        # print "+"*50
        
        # print theSensor.sensorType
        # print theSensor.node
        # print theNode.sensors
        # print theSType.sensors
        # print "+"*50

    def testAltFK(self):
        """
        Test the Alternate FK allocation
        """
        session = self.session
        theNode = models.Node(id=11)
        theSType = models.SensorType(id=1,name="test")
        theSensor = models.Sensor()
        theSensor.sensorType=theSType
        theSensor.node = theNode
        session.add(theSensor)

        self.assertEqual(theSensor.sensorType,theSType)
        self.assertEqual(theSensor.node,theNode)        
        #And from the "parent Objects"
        self.assertIn(theSensor,theNode.sensors)
        self.assertIn(theSensor,theSType.sensors)

    def testGlobals(self):
        """Test against premade database"""
        
        #First off we want to check if Sensors we have put together are the right types
        session = self.session

        #Check we have the right type of sensor (3* 2) temp + 1*3 (voc)
        theQry = session.query(models.Sensor).count()
        self.assertEqual(theQry,9)

        
        #There sould be 4 temperaure sensors
        sType = session.query(models.SensorType).filter_by(name="temp").first()

        theQry = session.query(models.Sensor).filter_by(sensorTypeId=sType.id)
        self.assertEqual(theQry.count(), 4)
        
        #We should have a VOC sensor attached to the Bedroom_H2 Node
        theQry = session.query(models.Sensor).join(models.SensorType).filter(models.SensorType.name=="voc").first()
        #print ""
        #print "="*20
        #print theQry.node
        self.assertEqual(theQry.node.id,212)

        
        

class TestSensorType(unittest.TestCase):
    """
    TestCases for Sensor Types
    """
    @classmethod
    def setUpClass(self):
        """Called the First time this class is called.
        This means that we can Init the testing database once per testsuite
        """
        testmeta.createTestDB()

    def setUp(self):
        """Called each time a test case is called, I wrap each
        testcase in a transaction, this means that nothing is saved to
        the database between testcases, while still allowing "fake" commits
        in the individual testcases.

        This means there should be no unexpected items in the DB."""

        #Pyramid Version
        try:
            self.config = testing.setUp()
            #Wrap In Transaction to ensure nothing gets saved between test cases
            self.transaction = transaction.begin()
            self.session = meta.Session
        except:
            #We have to do it slightly different for non pyramid applications.
            #We do however get the same functionality.
            connection = engine.connect()
            self.transaction = connection.begin()
            self.session = Session(bind=connection)

    def tearDown(self):
        """
        Called after each testcase,
        Uncommits any changes that test case made
        """
        
        #Pyramid
        try:
            self.transaction.abort()
            testing.tearDown()
        except:
            self.transaction.rollback()
            self.session.close()

    def testCreate(self):
        session = self.session

        theSType = models.SensorType(id=1,name="test")

        self.assertIsInstance(theSType,models.SensorType)
        session.add(theSType)
        session.flush()

    def testCreateError(self):
        """All sensor types should have an Id,
        Creating one without an Id SHOULD fail"""
        session = self.session
        theSType = models.SensorType(name="test")
        
        session.add(theSType)
        with self.assertRaises(FlushError):
            session.flush()

    def testGloals(self):
        """Test Against the Premade Database"""
        
        session = self.session
        #See if we have a temperature Sensor
        theQry = session.query(models.SensorType).filter_by(name="temp").first()
        self.assertEqual(theQry.id,101)

        #And the VOC Sensor
        theQry = session.query(models.SensorType).filter_by(id=103).first()
        self.assertEqual(theQry.name,"voc")

if __name__ == "__main__":
    unittest.main()

