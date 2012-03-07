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


class TestNode(unittest.TestCase):
    """
    Deal with tables in the Node module
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
        theNode = models.Node()
        self.assertIsInstance(theNode,models.Node)

        theNodeT = models.NodeType()
        self.assertIsInstance(theNodeT,models.NodeType)

    def testFK(self):
        """Can we do Node ForeignKeys and Backrefs
        :TODO: We need to fix this to work with the InnoDB requirements
        """

        pass
        # session = self.session
        # theNodeT = models.NodeType(id=1,name="test")
        # theLocation = models.Location(houseId=10,roomId=10)
        # session.add(theNodeT)
        # session.add(theLocation)
        # session.flush()
        # theNode = models.Node(nodeTypeId = theNodeT.id,
        #                       locationId = theLocation.id)
        
        # session.add(theNode)
        # session.flush()
                                      
        # self.assertEqual(theNode.nodeType,theNodeT)

    def testGlobals(self):
        session = self.session

        #We can enter this test at the Room
        
        #Check if a Node we know about exists
        #theQry

        # theQry = session.query(models.Node).all()               
        # self.assertEqual(len(theQry),4)

        # #Can we link nodes back to the Room they belong to.
        
        # theQry = session.query(models.Node).filter_by(id=111).first()
        # #Using the Locaiton Backref
        # self.assertEqual(theQry.location.room.name,"Bedroom_H1")

        # #Or the Associative Array
        # self.assertEqual(theQry.rooms[0].name,"Bedroom_H1")
        
        # #Node 121 has been moved betwen the bathrooms
        # theQry = session.query(models.Node).filter_by(id=121).first()
        # print "-------> ",theQry.location
        # self.assertEqual(theQry.location.id,4) #LocBath1
        # self.assertNotEqual(theQry.location.id,3) #LocBath2

if __name__ == "__main__":
    unittest.main()
