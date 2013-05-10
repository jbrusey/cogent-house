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


class TestRoom(testmeta.BaseTestCase):
    """
    Deal with Rooms
    """

    def testGlobals(self):
        """Test Against Global Data

        :TODO: This also needs fixing to take acocunt of the Updated DB Structure
        """
        
        # session = self.session
        
        # #Can we link back to the relevant House
        # theQry = session.query(models.Room).filter_by(name="Bedroom_H1").all()
        # self.assertEqual(len(theQry),1)
        # theQry = theQry[0]

        # #In the Testing DB a room can only be in one house therefore
        # location = theQry.location[0]
        # #print location
        # theHouse = location.house       
        # self.assertEqual(theHouse.address,"add1")


        # theQry = session.query(models.Room).filter_by(name="Bedroom_H2").all()
        # self.assertEqual(len(theQry),1)
        # theQry = theQry[0]

        # #In the Testing DB a room can only be in one house therefore
        # location = theQry.location[0]
        # theHouse = location.house       
        # self.assertEqual(theHouse.address,"add2")
        
        
        # #Now it gets a bit more funky in the case of bathrooms, as I
        # #put two with the same name.  But as in the general case I
        # #expect to go house -> room rather than the other way around
        # #this Should not be a problem

        # theQry = session.query(models.Room).join(models.Location).join(models.House).filter(models.Room.name=="bathroom",
        #                                                                                     models.House.address=="add1").all()


        # #print theQry
        # #Megastring(TM) to get the original object back
        # self.assertEqual(theQry[0].location[0].house.address,"add1")

        
        # #Rooms Should also have a type
        # theQry = session.query(models.Room).filter_by(name="Bedroom_H1").first()
        # self.assertEqual(theQry.roomType.name, "bedroom")

        # theQry = session.query(models.Room).filter_by(name="bathroom").all()
        # for item in theQry:
        #     self.assertEqual(item.roomType.name, "bathroom")

        # #Can we Link Rooms and Nodes
        # theQry = session.query(models.Room).filter_by(name="Bedroom_H1").first()
        # theLoc = theQry.location[0] #Again we should only have 1 location per room
        # theQry = session.query(models.Node).filter_by(locationId=theLoc.id).all()
        # self.assertEqual(len(theQry),1)
        # self.assertEqual(theQry[0].id,111)

        # #And the Simple (append) way
        # theQry = session.query(models.Room).filter_by(name="Bedroom_H1").first()
        # roomNodes = theQry.nodes
        # self.assertEqual(len(roomNodes),1)
        # self.assertEqual(roomNodes[0].id,111)

        # #Similarly we expect the two bathrooms to have the same Node in them
        # #Using the Room-Node Association Table 
        # #(See the testNode code for a place where this fails)
        # bath1 = session.query(models.Room).join(models.Location).join(models.House).filter(models.Room.name=="bathroom",
        #                                                                                     models.House.address=="add1").first()

        # bath2 = session.query(models.Room).join(models.Location).join(models.House).filter(models.Room.name=="bathroom",
        #                                                                                     models.House.address=="add2").first()

        # self.assertEqual(bath1.nodes[0],bath2.nodes[0])

if __name__ == "__main__":
    unittest.main()
