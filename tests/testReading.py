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
        """Can we create Readings,

        :TODO: Fix integrity (Referential) error here"""
        pass
        """
        theReading = models.Reading(time=datetime.datetime.now(),
                                    nodeId = 1,
                                    typeId = 1,
                                    locationId = 1,
                                    value = 20.0)
        session = self.session
        session.add(theReading)
        session.flush()
        """

    def testHouse1(self):
        """Test Our Global Database for House1"""
        session = self.session

        print ""
        print "="*40

        #Get the House
        theHouse = session.query(models.House).filter_by(address="add1").first()
        #print theHouse

        #Get the Sensor Type
        tempType = session.query(models.SensorType).filter_by(name="Temperature").first() 

        #Get the Locations
        locations = theHouse.locations
        #for item in locations:
        #    print item

        #So we can fetch all of the readings by Location
        #If We Remember back to the test Case then
        for location in locations:
            readings = session.query(models.Reading).filter_by(typeId=tempType.id,
                                                               locationId = location.id)
            print "{0} Readings for Location {1}".format(readings.count(),location)
                                                                   
                                                           
        
        print "="*40
        pass

if __name__ == "__main__":
    unittest.main()
