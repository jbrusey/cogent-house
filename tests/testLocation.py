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

class TestLocation(unittest.TestCase):
    """
    Deal with tables in the location module
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
        theLocation = models.Location()
        self.assertIsInstance(theLocation,models.Location)

    #@unittest.expectedFailure
    def testBackrefs(self):
        """We should fail if more than one location for the same place exists"""

        session = self.session
        

        theHouse = models.House(address="theAddress")
        theRoom = models.Room(name="roomName")
        secondRoom = models.Room(name="secondRoom")
        session.add(theHouse)
        session.add(theRoom)
        session.add(secondRoom)
        session.flush()
        
        theLocation = models.Location()
        theLocation.houseId = theHouse.id
        theLocation.roomId = theRoom.id

        secLocation = models.Location()
        secLocation.houseId = theHouse.id
        secLocation.roomId = secondRoom.id

        session.add(theLocation)
        session.add(secLocation)
        session.flush()
        
        #Now lets get the objects vai the Backrefs
        hLoc = theHouse.locations
        self.assertEqual(len(hLoc),2) #There should be two locations for this house

        
        #expected locations
        expLoc = [theLocation,secLocation]
        self.assertEqual(hLoc,expLoc)

        #We can then get the rooms for each Location

        self.assertEqual(theLocation.room,theRoom)

        #So the full code to link the two should begin
        self.assertEqual(theHouse.locations[0].room,theRoom)

if __name__ == "__main__":
    unittest.main()
