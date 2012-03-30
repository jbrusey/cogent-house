"""
Testing for the Deployment Module

:author: Dan Goldsmith <djgoldsmith@googlemail.com>
"""


#Python Library Imports
import unittest
from datetime import datetime

#Python Module Imports
import sqlalchemy.exc

import testmeta

models = testmeta.models


class TestReading(testmeta.BaseTestCase):
    """
    Test Cases for Readings
    """

    def testCreate(self):
        """Can we create Readings,

        :TODO: Fix integrity (Referential) error here"""
        pass
        """
        theReading = models.Reading(time=datetime.now(),
                                    nodeId = 1,
                                    typeId = 1,
                                    locationId = 1,
                                    value = 20.0)
        session = self.session
        session.add(theReading)
        session.flush()
        """

    def testHouse1(self):
        """Test Our Global Database for House1"""
        session = self.session

        print ""
        print "="*40

        #Get the House
        theHouse = session.query(models.House).filter_by(address="add1").first()
        #print theHouse

        #Get the Sensor Type
        tempType = session.query(models.SensorType).filter_by(name="Temperature").first() 

        #Get the Locations
        locations = theHouse.locations
        #for item in locations:
        #    print item

        #So we can fetch all of the readings by Location
        #If We Remember back to the test Case then
        for location in locations:
            readings = session.query(models.Reading).filter_by(typeId=tempType.id,
                                                               locationId = location.id)
            print "{0} Readings for Location {1}".format(readings.count(),location)
                                                                   
                                                           
        
        print "="*40
        pass

if __name__ == "__main__":
    unittest.main()
