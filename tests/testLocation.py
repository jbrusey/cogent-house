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

    #@unittest.expectedFailure
    def testBackrefs(self):
        """We should fail if more than one location for the same place exists"""

        session = self.session
        

        theHouse = models.House(address="theAddress")
        theRoom = models.Room(name="roomName")
        secondRoom = models.Room(name="secondRoom")
        session.add(theHouse)
        session.add(theRoom)
        session.add(secondRoom)
        session.flush()
        
        theLocation = models.Location()
        theLocation.houseId = theHouse.id
        theLocation.roomId = theRoom.id

        secLocation = models.Location()
        secLocation.houseId = theHouse.id
        secLocation.roomId = secondRoom.id

        session.add(theLocation)
        session.add(secLocation)
        session.flush()
        
        #Now lets get the objects vai the Backrefs
        hLoc = theHouse.locations
        self.assertEqual(len(hLoc),2) #There should be two locations for this house

        
        #expected locations
        expLoc = [theLocation,secLocation]
        self.assertEqual(hLoc,expLoc)

        #We can then get the rooms for each Location

        self.assertEqual(theLocation.room,theRoom)

        #So the full code to link the two should begin
        self.assertEqual(theHouse.locations[0].room,theRoom)

if __name__ == "__main__":
    unittest.main()
