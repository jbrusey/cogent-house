""" 
Unit Tests for JSON functionality

We make a few assumptions here:

1. That the asDict() and fromDict() functions are tested individually for each
   model
"""


### Import SQL Alchemy so we can check things are actually added to the database
import sqlalchemy
#from sqlalchemy import create_engine
#from sqlalchemy.orm import scoped_session, sessionmaker

import unittest

#Pyramid Unittests
from pyramid import testing
import transaction

#Import the Models and Meta Classes

import cogentviewer.models as models
import cogentviewer.models.meta as meta   

config = testing.setUp()

import os
import datetime

#import restful_lib
#BASEURL = "http://127.0.0.1:6543/rest/deployment"
#BASEURL = "http://127.0.0.1:6543/rest/deployment"

import json



class JSONTests(unittest.TestCase):
    """Class to Unittest our functions to convert to and from JSON

    This will test the generator functions in models,
    along with the json encoding functionalty included in the meta.InnoDBMix Class
    """

    def testAsDict(self):
        """Test the meta.InnoDBMix.asDict function"""

        startDate = datetime.datetime.now()
        endDate = datetime.datetime.now() + datetime.timedelta(days=1)

        theDeployment = models.Deployment(name="Test",
                                          id=1,
                                          description="A Description",
                                          startDate = startDate,
                                          endDate = endDate)

        #Convert to dictonary
        theItem = theDeployment.toDict()

        #Make a dictionary version of this
        testDict = {"name": "Test",
                    "id": 1,
                    "description": "A Description",
                    "startDate": startDate.isoformat(),
                    "endDate": endDate.isoformat(),
                    "__table__": "Deployment"}
        self.assertEqual(theItem, testDict)

        #Then To JSON
        jsonItem = json.dumps(theItem)
        
        #And Convert the Object Back
        retItem = models.Deployment()
        retItem.fromJSON(jsonItem)
        #retItem.fromJSON(jsonItem)
        
        self.assertEqual(theDeployment,retItem)

        #And try as a class method
        retItem = models.Deployment()
        retItem.fromJSON(jsonItem)
        self.assertEqual(theDeployment,retItem)

    def testGenerator(self):
        """Test if we can auto de-serialise the objects"""

        startDate = datetime.datetime.now()
        endDate = datetime.datetime.now() + datetime.timedelta(days=1)

        theDeployment = models.Deployment(name="Test",
                                          id=1,
                                          description="A Description",
                                          startDate = startDate,
                                          endDate = endDate)

        #Convert to JSON dictonary
        theItem = theDeployment.toDict()
        jsonItem = json.dumps(theItem)

        #JSON objects with non string keys, may not necessary test for
        #Eqality, so we cannot do a simple dict based check here.

        #Then load the object back
        #newObj = models.clsFromJSON(jsonItem)
        newObj = models.clsFromJSON(theItem)

        outList = list(newObj)


        #As it is a generator we need to turn our orginal item into a list
        self.assertEqual([theDeployment], outList)

    def testMultipleGenerator(self):
        """Test the Generator with multiple objects of the same type"""
        #Lets test with multiple objects too

        startDate = datetime.datetime.now()
        endDate = datetime.datetime.now() + datetime.timedelta(days=1)

        theDeployment = models.Deployment(name="Test",
                                          id=1,
                                          description="A Description",
                                          startDate = startDate,
                                          endDate = endDate)

        newDeployment = models.Deployment(name="Test 2",
                                          id=2,
                                          description="Another Description",
                                          startDate = startDate,
                                          endDate = endDate)

        objList = [theDeployment, newDeployment]
        jsonItem = json.dumps([x.toDict() for x in objList])
        
        objGen = models.clsFromJSON(jsonItem)
        objGen = list(objGen)
        
        #objGen = models.clsFromJSON(jsonItem)
        self.assertEqual(objList,objGen)


    def testMultipleTypes(self):
        """Test our Generator with multiple object types"""

        startDate = datetime.datetime.now()
        endDate = datetime.datetime.now() + datetime.timedelta(days=1)

        objList = []

        theDeployment = models.Deployment(name="Test",
                                          id=1,
                                          description="A Description",
                                          startDate = startDate,
                                          endDate = endDate)

        objList.append(theDeployment)

        newDeployment = models.Deployment(name="Test 2",
                                          id=2,
                                          description="Another Description",
                                          startDate = startDate,
                                          endDate = endDate)

        objList.append(newDeployment)

        theHouse = models.House(id=1,
                                deploymentId = 1,
                                address="Test",
                                startDate = startDate,
                                endDate = endDate)
        objList.append(theHouse)

        theNode = models.Node(id=1,
                              locationId=1)
        objList.append(theNode)

        theReading = models.Reading(time=startDate,
                                    nodeId=1,
                                    typeId=1,
                                    locationId=1,
                                    value=42.0,
                                    )

        objList.append(theReading)

        #Convert to JSON
        jsonItem = json.dumps([x.toDict() for x in objList])
        #Then back again
        objGen = models.clsFromJSON(jsonItem)
        jsonList = list(objGen)

        self.assertEqual(objList,jsonList)
