"""
Testing for the Deployment Module

:author: Dan Goldsmith <djgoldsmith@googlemail.com>

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

try:
    import unittest2 as unittest
except:
    import unittest

#@unittest.skip("Base Class, Skip for most purposes")
class TestStub(base.BaseTestCase):
    """
    Deal with tables in the deployment module
    """
    def testSomething(self):
        #Test if this passes
        self.assertTrue(True)


    def testAdd(self):
        #This should not exist in the database after the tests are run
        session = self.session

        theDeployment = models.Deployment(name="testA")

        session.add(theDeployment)
        session.flush()
        session.commit()

        qry = session.query(models.Deployment)
        for item in qry:
            print item

    def testCreate(self):
        #Test Creation of Objects
        session = self.session

        qry = session.query(models.Deployment)
        for item in qry:
            print item
        pass

    def testUpdate(self):
        #Test Update of Objects
        pass

    def testToDict(self):
        #Test toDict method
        pass

    def testFromJSON(self):
        #Test JSON method
        pass
