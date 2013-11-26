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


"""
.. versionadded:: 0.1
    Found a better way than all those try catch blocks,
    Move them into the meta class, and let that deal with the pain in
    one place.

"""

#Python Library Imports
import unittest
from datetime import datetime

#Python Module Imports
import sqlalchemy.exc

import testmeta

import json

models = testmeta.models

class TestDeployment(testmeta.BaseTestCase):
    """
    Deal with tables in the deployment module
    """

    def testDeployment(self):
        """Can we Create Deployments"""

        thisDeployment = models.Deployment()
        self.assertIsInstance(thisDeployment, models.Deployment)

        thisDeployment = models.Deployment(description="Test")
        self.assertEqual(thisDeployment.description, "Test")

    def testDeploymentUpdate(self):
        """Can we update deployments"""

        thisDeployment = models.Deployment()

        thisDeployment.update(description="A Test Deployment")
        self.assertEqual(thisDeployment.description,"A Test Deployment")

        #Check if we can do multiple inserts and not loose previous stuff
        today = datetime.now()
        thisDeployment.update(startDate = today, endDate=today)
        self.assertEqual(thisDeployment.startDate, today)
        self.assertEqual(thisDeployment.endDate, today)
        self.assertEqual(thisDeployment.description, "A Test Deployment")

    def testDeploymentMeta(self):
        """Can we create deployment Meta objects"""

        thisMeta = models.DeploymentMetadata()
        self.assertIsInstance(thisMeta, models.DeploymentMetadata)

    # def testFk(self):
    #     """Test if deployment foreign keys are stored correctly"""
    #     session = self.session

    #     theDeployment = models.Deployment(name="TestDeployment",
    #                                       description="A Test Deployment")

    #     session.add(theDeployment)
    #     session.flush()

    #     metaData = models.DeploymentMetadata(deploymentId = theDeployment.id,
    #                                          name="Test Metadata",
    #                                          description="A Bit more MetaData",
    #                                          units="Units",
    #                                          value = 12.0)


    #     session.add(metaData)

    #     theHouse = models.House(deploymentId = theDeployment.id,
    #                             address="10 Greenhill st")
    #     session.add(theHouse)


    #     #Now see if we can get the stuff back

    #     session = self.session
    #     depQuery = session.query(models.Deployment)
    #     depQuery=depQuery.filter_by(name="TestDeployment").first()

    #     #Now try and find the metaData
    #     depMeta = depQuery.meta

    #     self.assertEqual(depMeta[0].name, "Test Metadata")

    #     houses = depQuery.houses
    #     self.assertEqual(houses[0].address, "10 Greenhill st")

    #     #Similarly we should also get the parent object back when we query
    #     self.assertEqual(depMeta[0].deployment.id, theDeployment.id)
    #     self.assertEqual(houses[0].deployment.id, theDeployment.id)


    # def testMetaInsert(self):
    #     """Trial Function, can we insert metadata straight into the deployment
    #     object.

    #     Turns out we can which is pretty frickin cool.
    #     """
    #     session = self.session

    #     theDeployment = models.Deployment(name="TestDeployment",
    #                                       description="A Test Deployment")

    #     metaData = models.DeploymentMetadata(name="Test Metadata",
    #                                          description="A Bit more MetaData",
    #                                          units="Units",
    #                                          value = 12.0)
    #     session.add(theDeployment)
    #     #Dont bother adding the metadata to the session, just append to backref
    #     theDeployment.meta.append(metaData)

    #     theHouse = models.House()
    #     theDeployment.houses.append(theHouse)
    #     session.flush()

    #     self.assertEqual(theDeployment.id, metaData.deploymentId)
    #     self.assertEqual(theHouse.deploymentId, theDeployment.id)

    #     #And References back to parent
    #     self.assertEqual(metaData.deployment.id, theDeployment.id)
    #     self.assertEqual(theHouse.deployment.id, theDeployment.id)


    # def testGlobals(self):
    #     """Test the 'Global' Version works correctly"""
    #     session = self.session

    #     theDeployment = session.query(models.Deployment).first()

    #     self.assertIsInstance(theDeployment, models.Deployment)
    #     #And Fetch Houses
    #     theHouses = session.query(models.House).all()

    #     self.assertEqual(theHouses, theDeployment.houses)

    #     for item in theDeployment.houses:
    #         self.assertEqual(item.deployment, theDeployment)

    def testJSON(self):
        theDeployment = models.Deployment(name="Foo",
                                          startDate = datetime.now())
        out =  theDeployment.toDict()

        #And Back Again
        newDeployment = models.Deployment()
        newDeployment.fromJSON(out)
        self.assertEqual(theDeployment, newDeployment)

        newDeployment.fromJSON(json.dumps(out))
        self.assertEqual(theDeployment, newDeployment)
