"""
Test Cases for the Sensor Classes
"""

#Python Library Imports
import unittest
from datetime import datetime

#Python Module Imports
import sqlalchemy.exc

import testmeta

models = testmeta.models


import sqlalchemy.exc
from sqlalchemy.exc import FlushError
from sqlalchemy.exc import IntegrityError

class TestSensor(testmeta.BaseTestCase):
    """
    Deal with tables in the deployment module
    """

    def testCreate(self):
        """Can We Create Sensor Objects"""
        theSensor = models.Sensor()
        self.assertIsInstance(theSensor, models.Sensor)

        theSensorType = models.SensorType()
        self.assertIsInstance(theSensorType,models.SensorType)

    def testParams(self):
        """Can we create and update with parameters"""
        
        theSensor = models.Sensor(calibrationSlope = 1.0,
                                  calibrationOffset = 1.0)

        self.assertEqual(theSensor.calibrationSlope,1.0)
        self.assertEqual(theSensor.calibrationOffset,1.0)

        
    def testUpdate(self):
        theSensor = models.Sensor()
        self.assertIsNone(theSensor.calibrationSlope)
    
        theSensor.update(calibrationSlope = 1.0,
                         calibrationOffset = 1.0)

        self.assertEqual(theSensor.calibrationSlope,1.0)
        self.assertEqual(theSensor.calibrationOffset,1.0)
    
    def testFK(self):
        """
        Test Foreign Keys and backrefs
        """
        session = self.session
        theNode = models.Node(id=1001)
        theSType = models.SensorType(id=1001,name="test")

        session.add(theNode)
        session.add(theSType)

        theSensor = models.Sensor(sensorTypeId=theSType.id,
                                  nodeId = theNode.id)
        
        session.add(theSensor)
        session.flush()

        #Test that Backrefts to this object work correctly
        self.assertEqual(theSensor.sensorType,theSType)
        self.assertEqual(theSensor.node,theNode)        
        #And from the "parent Objects"
        self.assertIn(theSensor,theNode.sensors)
        self.assertIn(theSensor,theSType.sensors)

    def testAltFK(self):
        """
        Test the Alternate FK allocation
        """
        session = self.session
        theNode = models.Node(id=1001)
        theSType = models.SensorType(id=1001,name="test")
        theSensor = models.Sensor()
        theSensor.sensorType=theSType
        theSensor.node = theNode
        session.add(theSensor)

        self.assertEqual(theSensor.sensorType,theSType)
        self.assertEqual(theSensor.node,theNode)        
        #And from the "parent Objects"
        self.assertIn(theSensor,theNode.sensors)
        self.assertIn(theSensor,theSType.sensors)

    def testGlobals(self):
        """Test against premade database
        
        :TODO: Make sure this is reimplmeneted
        """
        
        #First off we want to check if Sensors we have put together are the right types
        session = self.session

        #Check we have the right type of sensor (3* 2) temp + 1*3 (voc)
        theQry = session.query(models.Sensor).count()
        #self.assertEqual(theQry,9)

        
        #There sould be 4 temperaure sensors
        #sType = session.query(models.SensorType).filter_by(name="temp").first()

        #theQry = session.query(models.Sensor).filter_by(sensorTypeId=sType.id)
        #self.assertEqual(theQry.count(), 4)

class TestSensorType(testmeta.BaseTestCase):
    """
    TestCases for Sensor Types
    """
    def testCreate(self):
        session = self.session

        theSType = models.SensorType(id=1001,name="test")

        self.assertIsInstance(theSType,models.SensorType)
        session.add(theSType)
        session.flush()

    def testCreateError(self):
        """All sensor types should have an Id,
        Creating one without an Id SHOULD fail"""
        session = self.session
        theSType = models.SensorType(name="test")
        
        session.add(theSType)
        with self.assertRaises(FlushError):
            session.flush()

    def testGloals(self):
        """Test Against the Premade Database
        
        """
        session = self.session
        #See if we have a temperature Sensor
        theQry = session.query(models.SensorType).filter_by(name="Temperature").first()        
        self.assertEqual(theQry.id,0)

        #And the VOC Sensor
        theQry = session.query(models.SensorType).filter_by(id=10).first()

        self.assertEqual(theQry.name,"VOC")

if __name__ == "__main__":
    unittest.main()

