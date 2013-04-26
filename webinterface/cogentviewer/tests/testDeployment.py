"""
Testing for the Deployment Module

:author: Dan Goldsmith <djgoldsmith@googlemail.com>
"""

from datetime import datetime

#Python Module Imports
import sqlalchemy.exc

import base
import json
import cogentviewer.models as models

import logging
log = logging.getLogger(__name__)


class TestDeployment(base.BaseTestCase):
    """
    Deal with tables in the deployment module
    """


    #GENERAL TESTS
    def testCreate(self):
        """Can we Create Deployments"""
        thisDeployment = models.Deployment()
        self.assertIsInstance(thisDeployment, models.Deployment)

        thisDeployment = models.Deployment(description="Test")
        self.assertEqual(thisDeployment.description, "Test")

    #Inherited from the Base Class
    def testUpdate(self):
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

    def testToDict(self):
        session = self.session
        theDeployment = models.Deployment(name="Test",description="Test")
        session.add(theDeployment)
        session.flush()
        #The toDict should return a dictionary representation of the object (time values isoformatted)
        #With an entry for each column,  also a __table__ appended
        #Representing the table name

        depDict = {"id":1,
                   "name":"Test",
                   "description":"Test",
                   "startDate":None,
                   "endDate":None,
                   "__table__": "Deployment",
                   }
                  

        theDict = theDeployment.toDict()
        self.assertEqual(theDict,depDict)
        #log.debug(theDict)

        #Check times
        now = datetime.now()
        
        theDeployment.startDate = now
        depDict["startDate"] = now.isoformat()
        
        theDict = theDeployment.toDict()
        self.assertEqual(theDict,depDict)

        return

    def testSerialise(self):
        theDeployment = models.Deployment(id=1,name="Test",description="Test",startDate=datetime.now())
        self.doSerialise(theDeployment)

