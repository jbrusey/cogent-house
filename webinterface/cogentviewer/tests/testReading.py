"""
Testing for the Reading Module

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

class TestReading(base.BaseTestCase):
    """
    Test Cases for Readings
    """

    def testCreate(self):
        """Can we create Readings,

        :TODO: Fix integrity (Referential) error here"""

        session = self.session

        theNode = session.query(models.Node).first()
        now = datetime.now()

        theReading = models.Reading(nodeId=1,
                                    time=now,
                                    typeId=0,
                                    locationId = 2,
                                    value=20.0
                                    )

        session.add(theReading)
        session.flush()


    def testToDict(self):
        now = datetime.now()
        theObject = models.Reading(nodeId=1,
                                   time=now,
                                   typeId=0,
                                   locationId = 2,
                                   value=20.0
                                   )

        #session.add(theObject)
        #session.flush()
        #The toDict should return a dictionary representation of the object (time values isoformatted)
        #With an entry for each column,  also a __table__ appended
        #Representing the table name

        depDict = {"__table__": "Reading",
                   "nodeId":1,
                   "type":0,
                   "locationId":2,
                   "time":now.isoformat(),
                   "value":20.0
                   }
                  

        theDict = theObject.toDict()
        self.assertEqual(theDict,depDict)
        pass

    def testSerialise(self):
        now = datetime.now()
        theObject = models.Reading(nodeId=1,
                                   time=now,
                                   typeId=0,
                                   locationId = 2,
                                   value=20.0
                                   )

        self.doSerialise(theObject)

        
      

    # def testGenerator(self):
    #     """Test if our calibrated reading generator works as expected"""
    #     session = self.session
        
    #     readings = session.query(models.Reading).filter_by(nodeId=37,
    #                                                        typeId = 0,
    #                                                        locationId = 1)

    #     #Define Generator
    #     calibReadings = models.reading.calibrateReadings(readings)

    #     cal = [x for x in calibReadings]
    #     self.assertEqual(cal,readings.all())


    # def testJSONGenerator(self):

    #     session = self.session
        
    #     readings = session.query(models.Reading).filter_by(nodeId=37,
    #                                                        typeId = 0,
    #                                                        locationId = 1)
    #     #Define Generator
    #     calibReadings = models.reading.calibrateJSON(readings)
        
if __name__ == "__main__":
    unittest.main()
