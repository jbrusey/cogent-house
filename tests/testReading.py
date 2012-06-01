"""
Testing for the Deployment Module

:author: Dan Goldsmith <djgoldsmith@googlemail.com>
"""


#Python Library Imports
import unittest
import datetime

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
      
        theReading = models.Reading(time=datetime.datetime.now(),
                                    nodeId = 70,
                                    typeId = 0,
                                    locationId = 1,
                                    value = 20.0)
        session = self.session
        session.add(theReading)
        session.flush()
      

    def testHouse1(self):
        """Test Our Global Database for House1"""
        session = self.session

        #Get the House
        theHouse = session.query(models.House).filter_by(address="add1").first()

        #Get the Sensor Type
        tempType = session.query(models.SensorType).filter_by(name="Temperature").first() 

        #Get the Locations
        locations = theHouse.locations
        #So we can fetch all of the readings by Location
        #If We Remember back to the test Case then
        for location in locations:
            readings = session.query(models.Reading).filter_by(typeId=tempType.id,
                                                               locationId = location.id)

    def testGenerator(self):
        """Test if our calibrated reading generator works as expected"""
        session = self.session
        
        readings = session.query(models.Reading).filter_by(nodeId=37,
                                                           typeId = 0,
                                                           locationId = 1)

        #Define Generator
        calibReadings = models.reading.calibrateReadings(readings)

        cal = [x for x in calibReadings]
        self.assertEqual(cal,readings.all())

    def testSecondGenerator(self):
        """Test if our readings are actually calibrated using the generator"""
        session = self.session

        theSensor = session.query(models.Sensor).filter_by(nodeId=37,sensorTypeId=0).first()
        theSensor.calibrationOffset = 10
        session.flush()

        #session.commit()

        #Then Get Readings
        readings = session.query(models.Reading).filter_by(nodeId=37,
                                                           typeId=0,
                                                           locationId = 1)
        values = [x.value + 10 for x in readings]
        calibReadings = models.reading.calibrateReadings(readings)
        cValues = [x.value for x in calibReadings]
        self.assertEqual(values,cValues)
        
        


    def testJSONGenerator(self):

        session = self.session
        
        readings = session.query(models.Reading).filter_by(nodeId=37,
                                                           typeId = 0,
                                                           locationId = 1)
        #Define Generator
        calibReadings = models.reading.calibrateJSON(readings)
        
if __name__ == "__main__":
    unittest.main()
