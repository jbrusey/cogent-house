"""
Testing for the House Module

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


class TestHouse(base.BaseTestCase):
    def testHouse(self):
        """Can we Create Houses"""
        
        #Bring it forward into the correct namespace
        thisHouse = models.House()
        self.assertIsInstance(thisHouse,models.House)
        
        thisHouse = models.House(address="Main")
        self.assertEqual(thisHouse.address,"Main")


    def testToDict(self):
        session = self.session

        now = datetime.now()
        theObject = models.House(id=1,
                                 deploymentId=1,
                                 address="10 Greenhill Street",
                                 startDate=now)
        #session.add(theObject)
        #session.flush()
        #The toDict should return a dictionary representation of the object (time values isoformatted)
        #With an entry for each column,  also a __table__ appended
        #Representing the table name

        depDict = {"id":1,
                   "deploymentId":1,
                   "address": "10 Greenhill Street",
                   "startDate":now.isoformat(),
                   "endDate":None,
                   "__table__": "House",
                   }
                  

        theDict = theObject.toDict()
        self.assertEqual(theDict,depDict)
        #log.debug(theDict)



    def testSerialise(self):
        theObject = models.House(id=1,
                                 deploymentId=1,
                                 address="10 Greenhill Street",
                                 startDate=datetime.now())

        self.doSerialise(theObject)
