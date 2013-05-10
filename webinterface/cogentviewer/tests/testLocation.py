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

class TestLocation(base.BaseTestCase):
    """
    Deal with tables in the location module
    """

    def testCreate(self):
        theLocation = models.Location(id=1,
                                      houseId=2,
                                      roomId=4)
        self.assertIsInstance(theLocation,models.Location)


    def testToDict(self):
        session = self.session

        theObject = models.Location(id=1,
                                      houseId=2,
                                      roomId=4)

        #The toDict should return a dictionary representation of the object (time values isoformatted)
        #With an entry for each column,  also a __table__ appended


        depDict = {"id":1,
                   "houseId":2,
                   "roomId": 4,
                   "__table__": "Location",
                   }
                  

        theDict = theObject.toDict()
        self.assertEqual(theDict,depDict)
        #log.debug(theDict)



    def testSerialise(self):
        theObject = models.Location(id=1,
                                      houseId=2,
                                      roomId=4)

        self.doSerialise(theObject)

