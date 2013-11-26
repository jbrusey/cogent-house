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

class TestNode(testmeta.BaseTestCase):
    """
    Deal with tables in the Node module
    """
    def testCreate(self):
        theNode = models.Node()
        self.assertIsInstance(theNode,models.Node)

        theNodeT = models.NodeType()
        self.assertIsInstance(theNodeT,models.NodeType)

    def testFK(self):
        """Can we do Node ForeignKeys and Backrefs
        :TODO: We need to fix this to work with the InnoDB requirements
        """

        pass
        # session = self.session
        # theNodeT = models.NodeType(id=1,name="test")
        # theLocation = models.Location(houseId=10,roomId=10)
        # session.add(theNodeT)
        # session.add(theLocation)
        # session.flush()
        # theNode = models.Node(nodeTypeId = theNodeT.id,
        #                       locationId = theLocation.id)
        
        # session.add(theNode)
        # session.flush()
                                      
        # self.assertEqual(theNode.nodeType,theNodeT)

    def testGlobals(self):
        session = self.session

        #We can enter this test at the Room
        
        #Check if a Node we know about exists
        #theQry

        # theQry = session.query(models.Node).all()               
        # self.assertEqual(len(theQry),4)

        # #Can we link nodes back to the Room they belong to.
        
        # theQry = session.query(models.Node).filter_by(id=111).first()
        # #Using the Locaiton Backref
        # self.assertEqual(theQry.location.room.name,"Bedroom_H1")

        # #Or the Associative Array
        # self.assertEqual(theQry.rooms[0].name,"Bedroom_H1")
        
        # #Node 121 has been moved betwen the bathrooms
        # theQry = session.query(models.Node).filter_by(id=121).first()
        # self.assertEqual(theQry.location.id,4) #LocBath1
        # self.assertNotEqual(theQry.location.id,3) #LocBath2

if __name__ == "__main__":
    unittest.main()
