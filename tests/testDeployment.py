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


class TestDeployment(unittest.TestCase):
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

    def testDeployment(self):
        """Can we Create Deployments"""

        thisDeployment = models.Deployment()
        self.assertIsInstance(thisDeployment,models.Deployment)

        thisDeployment = models.Deployment(description="Test")
        self.assertEqual(thisDeployment.description,"Test")

    # def testDeploymentUpdate(self):
    #     """Can we update deployments"""
    
    #     thisDeployment = models.Deployment()
        
    #     thisDeployment.update(description="A Test Deployment")
    #     self.assertEqual(thisDeployment.description,"A Test Deployment")

    #     #Check if we can do multiple inserts and not loose previous stuff
    #     today = datetime.datetime.now()
    #     thisDeployment.update(startDate = today,endDate=today)
    #     self.assertEqual(thisDeployment.startDate,today)
    #     self.assertEqual(thisDeployment.endDate,today)
    #     self.assertEqual(thisDeployment.description,"A Test Deployment")

        
    def testDeploymentMeta(self):
        """Can we create deployment Meta objects"""

        thisMeta = models.DeploymentMetadata()
        self.assertIsInstance(thisMeta,models.DeploymentMetadata)

    def testFk(self):
        """Test if deployment foreign keys are stored correctly"""
        session = self.session
        
        theDeployment = models.Deployment(name="TestDeployment",
                                          description="A Test Deployment")

        session.add(theDeployment)
        session.flush()

        metaData = models.DeploymentMetadata(deploymentId = theDeployment.id,
                                             name="Test Metadata",
                                             description="A Bit more MetaData",
                                             units="Units",
                                             value = 12.0)


        session.add(metaData)

        theHouse = models.House(deploymentId = theDeployment.id,
                                address="10 Greenhill st")
        session.add(theHouse)


        #Now see if we can get the stuff back

        session = self.session
        depQuery = session.query(models.Deployment).filter_by(name="TestDeployment").first()       
        
        #Now try and find the metaData
        depMeta = depQuery.meta

        self.assertEqual(depMeta[0].name,"Test Metadata")

        houses = depQuery.houses
        self.assertEqual(houses[0].address,"10 Greenhill st")
                 
        #Similarly we should also get the parent object back when we query
        self.assertEqual(depMeta[0].deployment.id,theDeployment.id)
        self.assertEqual(houses[0].deployment.id, theDeployment.id)

        
    def testMetaInsert(self):
        """Trial Function, can we insert metadata straight into the deployment object.

        Turns out we can which is pretty frickin cool.
        """
        session = self.session
        
        theDeployment = models.Deployment(name="TestDeployment",
                                          description="A Test Deployment")

        metaData = models.DeploymentMetadata(name="Test Metadata",
                                             description="A Bit more MetaData",
                                             units="Units",
                                             value = 12.0)
        session.add(theDeployment)
        #Dont bother adding the metadata to the session, just append to backref
        theDeployment.meta.append(metaData)
        
        theHouse = models.House()
        theDeployment.houses.append(theHouse)
        session.flush()

        self.assertEqual(theDeployment.id,metaData.deploymentId)
        self.assertEqual(theHouse.deploymentId,theDeployment.id)

        #And References back to parent
        self.assertEqual(metaData.deployment.id,theDeployment.id)
        self.assertEqual(theHouse.deployment.id,theDeployment.id)


    def testGlobals(self):
        """Test the 'Global' Version works correctly"""
        session = self.session

        theDeployment = session.query(models.Deployment).first()
        #print ""
        #print "~"*40
        print theDeployment


        self.assertIsInstance(theDeployment,models.Deployment)
        
        #And Fetch Houses
        theHouses = session.query(models.House).all()
        #print theHouses

        self.assertEqual(theHouses,theDeployment.houses)
        #print "~"*40

        for item in theDeployment.houses:
            self.assertEqual(item.deployment, theDeployment)


if __name__ == "__main__":
    unittest.main()
