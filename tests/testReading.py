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

class TestReading(unittest.TestCase):
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
        """Can we create Readings"""
        theReading = models.Reading(time=datetime.datetime.now(),
                                    nodeId = 1,
                                    typeId = 1,
                                    locationId = 1,
                                    value = 20.0)
        session = self.session
        session.add(theReading)
        session.flush()

    def testGlobals_Bed1(self):
        """Test against Testing Database"""
        session = self.session
        
        #Reading is, time,nodeid,typeid,locationid,value

        #Consevably room,node will come from the User


        #Find Temperture sensor tpye
        sType = session.query(models.SensorType).filter_by(name="temp").first()
        
        #Temperature Data for Bedroom_H1
        theRoom = session.query(models.Room).filter_by(name="Bedroom_H1").first()
        #From this we can get the Location
        theLocation = theRoom.location[0]
        #And the Nodes
        theNode = theRoom.nodes[0] 

        #Now we are ready to get the data 
        dataQry = session.query(models.Reading).filter_by(nodeId=theNode.id,
                                                          typeId=sType.id,
                                                          locationId=theLocation.id)
        #There should only be 10 Readings
        self.assertEqual(dataQry.count(),10)
        
        #And they should all be 1.0
        for item in dataQry:
            self.assertEqual(item.getRawValues()[1], 1.0)
            self.assertEqual(item.getCalibValues()[1],1.0)
            #print item


    def testGlobals_Bath1(self):
        """Test against Testing Database"""
        session = self.session
        
        #Reading is, time,nodeid,typeid,locationid,value

        #Find Temperture sensor tpye
        sType = session.query(models.SensorType).filter_by(name="temp").first()
        
        # --------------------- House 1 Bathroom 1 -----------------------------------
        #Break this down
        theRoom = session.query(models.Room).join(models.Location).join(models.House)
        theRoom = theRoom.filter(models.Room.name=="bathroom" and models.House.address=="add1").first()

        theLocation = theRoom.location[0]
        #And the Nodes
        theNode = theRoom.nodes[0] 

        #Now we are ready to get the data 
        dataQry = session.query(models.Reading).filter_by(nodeId=theNode.id,
                                                          typeId=sType.id,
                                                          locationId=theLocation.id)
        #There should only be 10 Readings
        self.assertEqual(dataQry.count(),10)
        
        #And they should all be 1.0 for the Raw Data, and 2.0 for the Calibrated
        for item in dataQry:
            self.assertEqual(item.getRawValues()[1], 1.0)
            #: TODO: Turn this back on at some point
            #self.assertEqual(item.getCalibValues()[1],2.0)



    def testGlobals_Bed2(self):
        """Test against Testing Database"""
        session = self.session
        
        #Reading is, time,nodeid,typeid,locationid,value

        #Find Temperture sensor tpye
        sType = session.query(models.SensorType).filter_by(name="temp").first()


        # -------------------- HOUSE 2 BEDROOM 1 ------------------------------
        theRoom = session.query(models.Room).filter_by(name="Bedroom_H2").first()


        """Bit of a Weird Bug Here, Getting the Location from those attached to the room is
        inconsistent, ie Sometimes it returns locationA, otherwise it returns location B
        Very Strange"""

        #From this we can get the Location
        theLocation = theRoom.location[0]
        #print theRoom.location
        #And the Nodes
        theNode = theRoom.nodes[0] 

        #Now we are ready to get the data 
        dataQry = session.query(models.Reading).filter_by(nodeId=theNode.id,
                                                          typeId=sType.id,
                                                          locationId=theLocation.id)
        #There should only be 10 Readings
        self.assertEqual(dataQry.count(),10)
        
        #And they should all be 1.0
        for item in dataQry:
            self.assertEqual(item.getRawValues()[1], 1.0)
            #TODO: Turn this back on too.
            #self.assertEqual(item.getCalibValues()[1],1.0)
            #print item

        # ---- There is also a second node here ----- 
        #theLocation = theRoom.location[1]
        theNode = theRoom.nodes[1]
        dataQry = session.query(models.Reading).filter_by(nodeId=theNode.id,
                                                          typeId=sType.id,
                                                          locationId=theLocation.id)
        #There should only be 10 Readings
        self.assertEqual(dataQry.count(),10)
        
        #And they should all be 1.0
        for item in dataQry:
            self.assertEqual(item.getRawValues()[1], 2.0)
            self.assertEqual(item.getCalibValues()[1],2.0)
            #print item            

        #Finally I suppose we could get all samples associated with this room
        dataQry = session.query(models.Reading).filter_by(typeId=sType.id,
                                                          locationId=theLocation.id)

        self.assertEqual(dataQry.count(),20)


    def testGlobals_Bath2(self):
        """Test against Testing Database"""
        session = self.session
        
        #Reading is, time,nodeid,typeid,locationid,value

        #Find Temperture sensor tpye
        sType = session.query(models.SensorType).filter_by(name="temp").first()
                
        # ---------------------- BATHROOM 2 ----------------------------------------
        #This is the interesting one, as it shares a node with bathroom 1,
        #If we have problems here then we know the DB is borked

        theRoom = session.query(models.Room).join(models.Location).join(models.House)
        theRoom = theRoom.filter(models.Room.name=="bathroom" and models.House.address=="add2").first()

        theLocation = theRoom.location[0]
        #And the Nodes
        theNode = theRoom.nodes[0] 

        dataQry = session.query(models.Reading).filter_by(nodeId=theNode.id,
                                                          typeId=sType.id,
                                                          locationId=theLocation.id)
        #There should only be 10 Readings
        self.assertEqual(dataQry.count(),10)
        
        
        # ------------------ DATA FOR BATHROOM NODE --------------
        # As this node is in two locations, then we can check if it has 20 samples, by removing the Location
        dataQry = session.query(models.Reading).filter_by(nodeId=theNode.id,
                                                          typeId=sType.id)
        #There should only be 10 Readings
        self.assertEqual(dataQry.count(),20)
    
if __name__ == "__main__":
    unittest.main()
