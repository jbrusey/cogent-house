"""
Testing for the Deployment Module

:author: Dan Goldsmith <djgoldsmith@googlemail.com>
"""

#Python Library Imports
import unittest
from datetime import datetime

#Python Module Imports
import sqlalchemy.exc


import base
import json
import cogentviewer.models as models


import logging
log = logging.getLogger(__name__)


class TestNode(base.BaseTestCase):
    """
    Deal with tables in the Node module
    """
    def testCreate(self):
        theNode = models.Node()
        self.assertIsInstance(theNode,models.Node)

        theNodeT = models.NodeType()
        self.assertIsInstance(theNodeT,models.NodeType)

    def testToDict(self):
        theNode = models.Node(id=1,
                              locationId = 1,
                              nodeTypeId = None,
                              )

        testDict = {"__table__":"Node",
                    "id":1,
                    "locationId":1,
                    "nodeTypeId":None
                    }

        theDict = theNode.toDict()
        log.debug(theDict)
                    
        self.assertEqual(theDict,testDict)

    def testSerialise(self):
        theObject = models.Node(id=1,
                                locationId = 1,
                                nodeTypeId = None,
                                )

        self.doSerialise(theObject)

