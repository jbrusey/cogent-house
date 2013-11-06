""" 
Unit Tests for the Rest Module
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

import restful_lib
import urllib
#BASEURL = "http://127.0.0.1:6543/rest/deployment"
#BASEURL = "http://127.0.0.1:6543/rest/deployment"
BASEURL = "http://127.0.0.1:6543/rest"

import json

class RestTests(unittest.TestCase):
    """Class to Unittest our rest functions
    """

    @classmethod
    def setUpClass(self):
        """Create a new test database to run the test cases

        Make sure the DBURL matches that in your pyramid config file.
        """
        engine = sqlalchemy.create_engine("sqlite:///test.db")
        models.initialise_sql(engine)

        self.engine = engine
        self.Session = sqlalchemy.orm.sessionmaker(bind=engine)

        #We also need to setup a REST client
        self.rest = restful_lib.Connection(BASEURL)

    def populateDB(self):        
        """Popultate our database with some initial information"""

        #Remove all deployments from the DB
        session = self.Session()
        theQry = session.query(models.Deployment)
        if theQry.count() == 2:
            pass
        else:
            #theQry.delete()

            theQry = session.query(models.Deployment).filter_by(id =1).first()
            if theQry is None:
                firstDeployment = models.Deployment(id=1,
                                                    name="First Deployment",
                                                    startDate = datetime.datetime.now() - datetime.timedelta(days = 10),
                                                    endDate = datetime.datetime.now() - datetime.timedelta(days = 5),
                                                    )
                print "Adding deployment 1"
                session.add(firstDeployment)

            theQry = session.query(models.Deployment).filter_by(id=2).first()
            if theQry is None:
                theDeployment = models.Deployment(id=2,
                                                  name="Second Deployment",
                                                  startDate = datetime.datetime.now() - datetime.timedelta(days=5),
                                                  endDate = datetime.datetime.now(),
                                                  )
                session.add(theDeployment)
                print "Adding deployment 2"

            session.flush()        

        session.commit()
    

        

    def setUp(self):
        """Wrap any database access in a transaction.  Hopefully this should keep the thing the same"""
        #Pyramid Version

        self.config = testing.setUp()
        self.populateDB()

    def tearDown(self):
        testing.tearDown()

    
    def testGetAll(self):
        """This should return all objects in the database"""

        #Check we have the two items I am expecting
        out = self.rest.request_get("deployment/")

        body = out['body']
        theBody = json.loads(body)

        #Check we get the same number of deployments back 
        session = self.Session()
        theQry = session.query(models.Deployment)

        self.assertEqual(len(theBody), theQry.count())
        
        #And is the response as expected
        self.assertEqual(out['headers']['status'],'200')        

    
    def testGetRange(self):
        """Does the Range Function work properly"""

        rangeArg = "items=0-5"
        out = self.rest.request_get("deployment/",headers={"Range":rangeArg})
        #Check we have the two items I am expecting
        body = out['body']
        theBody = json.loads(body)

        session = self.Session()
        theQuery = session.query(models.Deployment)
        theQuery = theQuery.filter(models.Deployment.id >= 0)
        theQuery = theQuery.filter(models.Deployment.id <= 5)
        
        self.assertEqual(len(theBody), theQuery.count())
        
        #And is the response as expected
        self.assertEqual(out['headers']['status'],'200')  

    
    def testGetParams(self):
        """Test our get function where we supply an Id paramter"""
        out = self.rest.request_get("deployment/1")
        theBody = json.loads(out['body'])
        self.assertEqual(len(theBody),1)
        #Remember that the body is still a list even with only one item
        self.assertEqual(theBody[0]['name'],'First Deployment')
        self.assertEqual(out['headers']['status'],'200')
        
    
    def testGetNone(self):
        """What happens if we ask for a deployment that doesnt exist"""
        out = self.rest.request_get("deployment/100")
        theBody = json.loads(out['body'])
        self.assertEqual(len(theBody),0)                           
        self.assertEqual(out['headers']['status'],'404')

    
    def testGetQuery(self):
        """Can we do a get using a query parameters"""

        out = self.rest.request_get("deployment/",args={"id":2})
        #Check we have the two items I am expecting
        body = out['body']
        theBody = json.loads(body)[0]

        self.assertEqual(theBody["id"],2)
        self.assertEqual(theBody["name"], "Second Deployment")
        
        #And is the response as expected
        self.assertEqual(out['headers']['status'],'200')  

    
    def testUpdate(self):
        
        theDeployment = models.Deployment(id=1,
                                          name="Update Test",
                                          description="Updated")


        newParams = json.dumps(theDeployment.toDict())
        out = self.rest.request_put("deployment/1",body=newParams)

        self.assertTrue(out['headers']['location'])
        self.assertEqual(out['headers']['status'],'201')

        #Run a query to see if the deployment has been Updated
        Session = self.Session()
        theQry = Session.query(models.Deployment).filter_by(id=1).first()
        self.assertEqual(theQry.name,"Update Test")
        self.assertEqual(theQry.description,"Updated")
        
        #As the Rest functionality is not wrapped we need to reset any values
        theQry.name = "First Deployment"
        theQry.description = None
        Session.flush()
        Session.commit()
        pass

    
    def testUpdateQuery(self):
        """Can we update an item based on a query"""
        theDeployment = models.Deployment(id=2,
                                          name="Second Deployment",
                                          description="Updated")

        theUrl = "deployment/?{0}".format(urllib.urlencode({"id":2}))
        out = self.rest.request_put(theUrl,body=json.dumps(theDeployment.toDict()))

        self.assertTrue(out['headers']['location'])
        self.assertEqual(out['headers']['status'],'201')

        session = self.Session()
        theQry = session.query(models.Deployment).filter_by(id=2).first()
        self.assertEqual(theQry.description,"Updated")
        
        session.flush()
        session.commit()

    
    def testUpdateDates(self):
        #Test if we can update an Item, this time dealing with dates
        #PUT is used to update
        #Fetch the first Item

        now = datetime.datetime.now()
        theDeployment = models.Deployment(id=1,
                                          name="Update Test",
                                          description="Updated",
                                          startDate = now,
                                          endDate = now
                                          )

        #session = self.Session()
        #theDeployment = session.query(models.Deployment).filter_by(id=1).first()
        
        #now = datetime.datetime.now()
        #theDeployment.endDate = now

        newParams = json.dumps(theDeployment.toDict())
        out = self.rest.request_put("deployment/1",body=newParams)

        self.assertTrue(out['headers']['location'])
        self.assertEqual(out['headers']['status'],'201')

        #Run a query to see if the deployment has been Updated
        Session = self.Session()
        theQry = Session.query(models.Deployment).filter_by(id=1).first()
        self.assertEqual(theQry.name,"Update Test")
        self.assertEqual(theQry.description,"Updated")
        self.assertEqual(theQry.startDate,now)
        self.assertEqual(theQry.endDate,now)
        
        
        #As the Rest functionality is not wrapped we need to reset any values
        theQry.name = "First Deployment"
        theQry.description = None
        Session.flush()
        Session.commit()
        pass

    
    def testAdd(self):
        #Create a new depoyment
        now = datetime.datetime.now()
        startD = now - datetime.timedelta(days = 2)
        theDeployment = models.Deployment(name = "New",
                                          startDate = startD,
                                          endDate = now)
        
        jsonBody = json.dumps(theDeployment.toDict())

        out = self.rest.request_post("deployment/",body=jsonBody)

        self.assertTrue(out['headers']['location'])
        self.assertEqual(out['headers']['status'],'201')

        Session = self.Session()
        theQry = Session.query(models.Deployment).filter_by(name="New").first()
        self.assertEqual(theQry,theDeployment)
        
        #And then we need to delete the item from the database
        theQry = Session.query(models.Deployment).filter_by(name="New")
        theQry.delete()
        Session.flush()
        Session.commit()
        pass


    def testDelete(self):
        #It does get a little confusing here, as we need a second Session to make sure everything has been done correctly
        #Let use the Global Session object
        session = self.Session()

        theCount = session.query(models.Deployment).count()

        #Add a new Item to remove
        newDeployment = models.Deployment(name="Temp_Delete")
        session.add(newDeployment)
        session.flush()
        session.commit()
        
        newCount = session.query(models.Deployment).count()

        #Check the item is in the DB 
        self.assertGreater(newCount,theCount)

        deleteString = "deployment/{0}".format(newDeployment.id)
        session.close()
        
        #And Remove it
        out = self.rest.request_delete(deleteString)
        #theBody = json.loads(out['body'])
        #self.assertEqual(theBody,[])

        self.assertEqual(out['headers']['status'],'204')

        #Start a new session and do the counting again

        session = self.Session()
        finalCount = session.query(models.Deployment).count()
        self.assertEqual(theCount,finalCount)


    #And as the Reading has a few corner cases attahed to it
    def testReading(self):
        """ Can we upload readings etc"""

        now = datetime.datetime.now()
        theReading = models.Reading(time=now,
                                    nodeId=1,
                                    typeId=1,
                                    locationId=1,
                                    value=42.0)

        #Can we Upload a Reading
        jsonBody = json.dumps(theReading.toDict())
        out = self.rest.request_post("reading/",body=jsonBody)
        #We should return a 201 (created) status header
        self.assertEqual(out['headers']['status'],'201')
        

        theReading = models.Reading(time=now+datetime.timedelta(seconds=60),
                                    nodeId=1,
                                    typeId=2,
                                    locationId=1,
                                    value=42.0)

        #Can we Upload a Reading
        jsonBody = json.dumps(theReading.toDict())
        
        out = self.rest.request_post("reading/",body=jsonBody)
    
        #Fetch all Readings
        theFetch = self.rest.request_get("reading/")
        jsonBody = json.loads(theFetch['body'])

        session = self.Session()
        theQry = session.query(models.Reading)
        self.assertEqual(theQry.count(),len(jsonBody))

        #return
        params = {"nodeId":1,"time":now}
        theQry = self.rest.request_get("reading/",args=params)
        jsonBody = json.loads(theQry['body'])
        self.assertEqual(len(jsonBody),1)

        #And as the typeId parameter is stored as 'type' we should check that works

        params = {"type":2,"time":now+datetime.timedelta(seconds=60)}
        theQry = self.rest.request_get("reading/",args=params)
        jsonBody = json.loads(theQry['body'])
        self.assertEqual(len(jsonBody),1)

    def testBulkReadings(self):
        """
        Can we bulk upload Readings
        """

        now = datetime.datetime.now()
        readingList = []

        for x in range(10):
            theReading = models.Reading(time=now+datetime.timedelta(seconds=x),
                                        nodeId=1,
                                        typeId=1,
                                        locationId=1,
                                        value=x)

            readingList.append(theReading)

        jsonBody = json.dumps([x.toDict() for x in readingList])
        #print jsonBody

        out = self.rest.request_post("bulk/",body=jsonBody)

        #print out

        session = self.Session()
        theQry = session.query(models.Reading)
        theQry = theQry.filter(models.Reading.time >= now)
        theQry = theQry.filter(models.Reading.time <= now+datetime.timedelta(seconds=10))
        self.assertEqual(theQry.count(),10)

        self.assertEqual(out['headers']['status'],'201')
