"""
Testing for the Deployment Module

:author: Dan Goldsmith <djgoldsmith@googlemail.com>
"""



"""
.. versionadded:: 0.1
    Found a better way than all those try catch blocks,
    Move them into the meta class, and let that deal with the pain in
    one place.

"""

import logging
log = logging.getLogger(__name__)


#import testmeta
import base
import cogentviewer.models as models

import unittest

@unittest.skip("Base Class, Skip for most purposes")
class TestStub(base.BaseTestCase):
    """
    Deal with tables in the deployment module
    """
    def testSomething(self):
        #Test if this passes
        self.assertTrue(True)
        session = self.session
        
        theQry = session.query(models.SensorType).limit(10)

    def testAdd(self):
        #This should not exist in the database after the tests are run
        session = self.session

        theDeployment = models.Deployment(name="test")

        session.add(theDeployment)
        session.flush()
        session.commit()

    def testCreate(self):
        pass



    def testUpdate(self):
        pass


    def testToDict(self):
        pass

    def testFromJSON(self):
        pass


