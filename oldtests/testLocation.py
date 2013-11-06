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

class TestLocation(testmeta.BaseTestCase):
    """
    Deal with tables in the location module
    """

    def testCreate(self):
        theLocation = models.Location()
        self.assertIsInstance(theLocation,models.Location)

    # #@unittest.expectedFailure
    # def testBackrefs(self):
    #     """We should fail if more than one location for the same place exists"""

    #     session = self.session
        

    #     theHouse = models.House(address="theAddress")
    #     theRoom = models.Room(name="roomName")
    #     secondRoom = models.Room(name="secondRoom")
    #     session.add(theHouse)
    #     session.add(theRoom)
    #     session.add(secondRoom)
    #     session.flush()
        
    #     theLocation = models.Location()
    #     theLocation.houseId = theHouse.id
    #     theLocation.roomId = theRoom.id

    #     secLocation = models.Location()
    #     secLocation.houseId = theHouse.id
    #     secLocation.roomId = secondRoom.id

    #     session.add(theLocation)
    #     session.add(secLocation)
    #     session.flush()
        
    #     #Now lets get the objects vai the Backrefs
    #     hLoc = theHouse.locations
    #     self.assertEqual(len(hLoc),2) #There should be two locations for this house

        
    #     #expected locations
    #     expLoc = [theLocation,secLocation]
    #     self.assertEqual(hLoc,expLoc)

    #     #We can then get the rooms for each Location

    #     self.assertEqual(theLocation.room,theRoom)

    #     #So the full code to link the two should begin
    #     self.assertEqual(theHouse.locations[0].room,theRoom)

    # def testGlobal(self):
    #     """ Test Against the Global Database """

    #     session = self.session
        
    #     #Check we get the expected Location
    #     theQry = session.query(models.Location).filter_by(id=1).first()
        
    #     self.assertEqual(theQry.houseId, 1)
    #     self.assertEqual(theQry.roomId, 1)
        
    #     self.assertEqual(theQry.house.address, "add1")
    #     self.assertEqual(theQry.room.name, "Master Bedroom")

    # def testJSON(self):
    #     """Does converting to JSON work as Expected"""

    #     #theQry = session.query(models.Location).filter_by(id=1).first()
    #     theQry = models.Location("id":1,
    #                              "name":"Master Bedroom",
    #                              "label":"Master Bedroom",
    #                              )
                                 

    #     #Expected JSON String should be
    #     expected = {"id":"L_1",
    #                "name":"Master Bedroom",
    #                "label":"Master Bedroom",
    #                "type":"location",
    #                "parent": "H_1",
    #                "children":[]
    #                }


    #     out = theQry.asJSON()

    #     self.assertEqual(out,expected)

    # def testGetReadings(self):
    #     """Do We Return the Exepected Number of Readings"""
    #     session = self.session
    #     theQry = session.query(models.Location).filter_by(id=1).first()

    #     readings = theQry.readings
    #     self.assertEqual(len(readings),72)

    # def testGetTypeReadings(self):
    #     session = self.session
    #     theQry = session.query(models.Location).filter_by(id=1).first()
    #     #raw_input("Start Get Readings")

    #     #Temperature (72)
    #     out = theQry.getReadings(0)
    #     self.assertEqual(len(out),72)
        
    #     #Delta Temperautre (None)
    #     out = theQry.getReadings(1)
    #     self.assertEqual(len(out),0)

    #     #Everything (72)
    #     out = theQry.getReadings()
    #     self.assertEqual(len(out),72)
    

if __name__ == "__main__":
    unittest.main()
