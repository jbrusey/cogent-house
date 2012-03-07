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

import testmeta

print "TEST META IS {0}".format(testmeta)
print "MODELS ARE {0}".format(testmeta.models)
print "META is {0}".format(testmeta.meta)

print "TETMETA viewer {0}".format(testmeta.viewer)

models = testmeta.models

if testmeta.viewer:
    #If we are dealing with the viewer class
    from pyramid import testing
    import transaction

class TestHouse(unittest.TestCase):
    """
    Deal with tables in the house module
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
            connection = testmeta.engine.connect()
            self.transaction = connection.begin()
            self.session = testmeta.Session()
            self.session.bind=connection

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

    def testHouse(self):
        """Can we Create Houses"""
        
        #Bring it forward into the correct namespace
        thisHouse = models.House()
        self.assertIsInstance(thisHouse,models.House)
        
        thisHouse = models.House(address="Main")
        self.assertEqual(thisHouse.address,"Main")

    def testHouseUpdate(self):
        """Can we update houses"""
        thisHouse = models.House()

        thisHouse.update(address="Main")

        self.assertEqual(thisHouse.address,"Main")       

        #And mupltiple attribs
        today = datetime.datetime.now()
        thisHouse.update(startDate = today,endDate=today)
        self.assertEqual(thisHouse.startDate,today)
        self.assertEqual(thisHouse.endDate,today)
        self.assertEqual(thisHouse.address,"Main")

    def testHouseMetadata(self):
        """Can we create HouseMetadata objects"""

        thisMeta = models.HouseMetadata()
        self.assertIsInstance(thisMeta,models.HouseMetadata)
        
        thisMeta = models.HouseMetadata(description = "Test")
        self.assertIsInstance(thisMeta,models.HouseMetadata)
        self.assertTrue(thisMeta.description,"Test")

    def testHouseFK(self):
        """Test if Houses Foreign Keys and Backrefs work correctly"""
    
        session = self.session

        theHouse = models.House(address="house")
        session.add(theHouse)
        session.flush()

        houseMeta = models.HouseMetadata(houseId=theHouse.id,name="meta")

        session.add(houseMeta)

        session.flush()

        #And does it come back 
        houseQry = session.query(models.House).filter_by(address="house").first()

        self.assertEqual(houseQry.meta[0].name,"meta")
        self.assertEqual(houseMeta.house.id,theHouse.id)

        #And Occupiers
        theOccupier = models.Occupier(name="Fred",houseId=theHouse.id)
        session.add(theOccupier)
        session.flush()
        self.assertEqual(theOccupier.house,theHouse)
        self.assertEqual(theHouse.occupiers[0].id,theOccupier.id)


    def testGlobals(self):
        """Test against the 'Global Database

        To Be honest I am not massivly worried about metadata or Occupiers
        As I am very unlikely to use them.

        If we do, Make sure a testcase or two goes here.
        """
        session = self.session
        houses = session.query(models.House).all()
        self.assertEqual(len(houses),2)

        theDeployment = session.query(models.Deployment).first()
        for item in houses:
            #Is the the Right Deployment
            self.assertEqual(item.deployment,theDeployment)
            #And Do we have some locations
            self.assertGreater(len(item.locations),1)

        #And Test the Locations we have for each house are as expected
        theHouse = session.query(models.House).filter_by(address="add1").first()
        roomNames = [x.name for x in theHouse.getRooms()]

        #Make sure these are as expected
        expectedNames = ["Master Bedroom","Second Bedroom","Living Room"]
        self.assertItemsEqual(roomNames,expectedNames)

        #Try it a second way
        theHouse = session.query(models.House).filter_by(address="add2").first()
        roomNames = [x.room.name for x in theHouse.locations]
        expectedNames = ["Master Bedroom","Living Room"]
        self.assertItemsEqual(roomNames,expectedNames)


if __name__ == "__main__":
    unittest.main()
