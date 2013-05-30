"""Metaclass to bring everything together in a simulation of a Pyramid environment

This really just makes sure all database code is in the same place
meaing the DB is consistently intiataed in all test cases.
"""

import os
import unittest

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

import json

from pyramid.config import Configurator
from paste.deploy.loadwsgi import appconfig
from pyramid import testing
from pyramid import testing

from sqlalchemy.orm import sessionmaker
from sqlalchemy import engine_from_config

import cogentviewer.models.meta as meta
import cogentviewer.models as models

#Setup the Testing to load pyramid settings from the test.ini file
ROOT_PATH = os.path.dirname(__file__)
SETTINGS_PATH = os.path.join(ROOT_PATH,"../../","test.ini")

#settings = appconfig('config:' + SETTINGS_PATH)

#log.debug("Loading Test Cases Name is {0} {1}".format(__name__,type(__name__)))

#log.debug("META IS")
#log.debug(meta)
#log.debug("BIND IS: {0}".format(meta.Base.metadata.bind))

def initDatabase():
    """Method to initialise the database"""

    log.debug("------- INITIALISE TESTING DATABASE ---------")
    settings = appconfig('config:' + SETTINGS_PATH)
    engine = engine_from_config(settings,prefix="sqlalchemy.")

    log.debug("Database Engine Started: {0}".format(engine))

    #Setup the configurator
    config = Configurator(settings = settings)

    #And populate the initial data
    #from cogentviewer.models import initialise_sql
    #from cogentviewer.models import populate_data

    #log.debug("Initialising SQL")
    #initialise_sql(engine)
    #meta.Base.metadata.bind = engine

    #log.debug("Populating Data")
    #populate_data()
    log.debug("----------------------------------------------")

#Check to see if we have a database allready initilised (Avoids bug where the test overrides everything)
if meta.Base.metadata.bind is None:
    log.info("No Database Initiated")
    initDatabase()


class BaseTestCase(unittest.TestCase):
    """Base class for testing"""

    @classmethod
    def setUpClass(cls):
        """Class method, called each time this is initialised"""
        #cls.config = testing.setUp()
        log.debug("Initialising Test Class Database for {0}".format(cls.__name__))
        settings = appconfig('config:' + SETTINGS_PATH)
        cls.engine = engine_from_config(settings,prefix='sqlalchemy.')
        cls.Session = sessionmaker()

    # def setUp(self):
    #     super(BaseTestCase, self).setUp()
    #     from cogentviewer import main
    #     #settings = { 'sqlalchemy.url': 'sqlite://'}
    #     app = main({}, **settings)

    #     from webtest import TestApp
    #     self.testapp = TestApp(app)

    def setUp(self):
        """Called each time a test case is called,
        He we wrap the test case in TransactionMagic(TM) 
        Meaning we can roll the testcase back, returning the database to normal
        """
        connection = self.engine.connect()
        
        #Begin the Transaction 
        self.transaction = connection.begin()
        
        #And bind the session
        self.session = self.Session(bind=connection)

    def tearDown(self):
        """
        Close the transaction and rollback after each test case is called
        """
        testing.tearDown()
        self.transaction.rollback()
        self.session.close()

class FunctionalTest(BaseTestCase):
    """ Add Functinal Testing (for the web pages themselves) functionalty"""
    
    @classmethod
    def setUpClass(cls):
        """
        New Setup Function, creates an app 
        """

        #not sure on classmehtod inheritance
        settings = appconfig('config:' + SETTINGS_PATH)
        cls.engine = engine_from_config(settings,prefix='sqlalchemy.')
        cls.Session = sessionmaker()

        #super(BaseTestCase, cls).setUp()
        from cogentviewer import main
        app = main({}, **settings)

        from webtest import TestApp
        cls.testapp = TestApp(app)
        

class ModelTestCase(BaseTestCase):
    """Subclass to test models"""

    def testEq(self):
        self.fail("You need to implement the Equality Test for this Model")
    
    def testCmp(self):
        self.fail("You need to implement the CMP test for this Model")

    def assertReallyEqual(self, a, b):
        # assertEqual first, because it will have a good message if the
        # assertion fails.
        self.assertEqual(a, b)
        self.assertEqual(b, a)
        self.assertTrue(a == b)
        self.assertTrue(b == a)
        self.assertFalse(a != b)
        self.assertFalse(b != a)
        self.assertEqual(0, cmp(a, b))
        self.assertEqual(0, cmp(b, a))

    def assertReallyNotEqual(self, a, b):
        # assertNotEqual first, because it will have a good message if the
        # assertion fails.
        self.assertNotEqual(a, b)
        self.assertNotEqual(b, a)
        self.assertFalse(a == b)
        self.assertFalse(b == a)
        self.assertTrue(a != b)
        self.assertTrue(b != a)
        self.assertNotEqual(0, cmp(a, b))
        self.assertNotEqual(0, cmp(b, a))
        
    def _serialobj(self):
        """Helper method, return an object to serialise"""
        self.fail("You need to implement a serialObj method for this class")
        pass

    def _dictobj(self):
        """Helper method, retrun a dictionary represnetaion of the _serialobj object"""
        self.fail("You need to implement a serialObj method for this class")
        pass

    def testSerialise(self):
        theObj = self._serialobj()

        #convert to dictionary
        #theDict = theObj.toDict()
        theDict = theObj.dict()
        #print "DICT ",theDict
        #Convert Back
        newObj = models.newClsFromJSON(theDict)
        #print "NEW: ",newObj
        self.assertEqual(theObj,newObj)

    def testDict(self):
        """Test Convertsion to a dictionary"""
        theItem = self._serialobj()
        theDict = self._dictobj()
        # now = datetime.datetime.now()

        # theItem = models.Deployment(id=1,
        #                             name="Test",
        #                             description="A Testing Deployment",
        #                             startDate = now,
        #                             endDate = now)

        # #See if we get the dictionaty we expect
        # #Should be the parameters + __table__ == "name"
        
        # theDict = {"__table__":"Deployment",
        #            "id":1,
        #            "name":"Test",
        #            "description":"A Testing Deployment",
        #            "startDate": now.isoformat(),
        #            "endDate": now.isoformat()}

        objDict = theItem.dict()
        self.assertIsInstance(objDict,dict)
        self.assertEqual(objDict,theDict)


    #  THIS METHOD GIVES A FEW PROBLEMS,  IE Dictionary has no garentees on how it will serialise,
    #  Therefore its a tad tricky to compare two strings from a serialised dictionarty
    #  It is sovered by the serialise testist though.
    # def testJson(self):
    #     """Test Conversion to a JSON Object"""
    #     theItem = self._serialobj()
    #     theDict = self._dictobj()

    #     #And the same with the json method
    #     objJson = theItem.json()
    #     self.assertIsInstance(objJson,str)
    #     self.assertEqual(objJson,json.dumps(theDict))




# #Build a complete testing database
# def createTestDB(session=False,now=False):
#     """Create a complete Testing Database
#     :param session: Session to use if not the global DB session
#     :param now: Time to use to setup the database
#     """

#     log.debug("Add Testing Data")
#     if not session:
#         session = Session()

        
#     if not now:
#         now = datetime.now()
#     deploymentEnd = now + timedelta(days=2)
#     house2Start = now + timedelta(days=1)
    
    
#     #See if we need to add these items
#     theDeployment = session.query(models.Deployment).filter_by(name="test").first()
#     #print theDeployment
#     #if theQry is not None:
#     #    return True

#     if theDeployment is None:
#         theDeployment = models.Deployment(name="test",
#                                           description="testing",
#                                           startDate = now,
#                                           endDate = deploymentEnd,
#                                           )

#         session.add(theDeployment)
#         session.flush()
#     else:
#         theDeployment.update(startDate=now,
#                              endDate=deploymentEnd)
#     log.debug("Houses")
#     #I Also want to add a couple of houses
#     #The First House runs for One day
#     house1 = session.query(models.House).filter_by(address="add1").first()
#     if house1 is None:
#         house1 = models.House(deploymentId = theDeployment.id,
#                               address = "add1",
#                               startDate = now,
#                               endDate = deploymentEnd,
#                               )
#         session.add(house1)
#     else:
#         house1.update(startDate = now,
#                       endDate = deploymentEnd)

#     house2 = session.query(models.House).filter_by(address="add2").first()
#     if house2 is None:
#         house2 = models.House(deploymentId = theDeployment.id,
#                               address = "add2",
#                               startDate = house2Start,
#                               endDate = deploymentEnd,
#                               )
#         session.add(house2)
#     else:
#         house2.update(startDate = house2Start,
#                       endDate = deploymentEnd)

#     session.flush()
    
#     #Lets Add Some Rooms (Using Bruseys new Room Paradigm)
#     log.debug("Rooms")
#     #Get the Relevant Room Types
#     bedroomType = session.query(models.RoomType).filter_by(name="Bedroom").first()
#     if bedroomType is None:
#         bedroomType = models.RoomType(name="Bedroom")
#         session.add(bedroomType)

#     livingType = session.query(models.RoomType).filter_by(name="Living Room").first()
#     if livingType is None:
#         livingType = models.RoomType(name="Living Room")
#         session.add(livingType)

#     session.flush()
    
#     #And the Specific Rooms themselves
#     masterBed = session.query(models.Room).filter_by(name="Master Bedroom").first()
#     if masterBed is None:
#         #(Note) We can either add room type by Id
#         masterBed = models.Room(name="Master Bedroom",roomTypeId=bedroomType.id)
#         session.add(masterBed)

#     secondBed = session.query(models.Room).filter_by(name="Second Bedroom").first()
#     if secondBed is None:
#         #Or We can do it the easier way
#         secondBed = models.Room(name="Second Bedroom")
#         secondBed.roomType = bedroomType
#         session.add(secondBed)
    
#     #Add a Living Room too
#     livingRoom = session.query(models.Room).filter_by(name="Living Room").first()
#     if livingRoom is None:
#         livingRoom = models.Room(name="Living Room")
#         livingRoom.roomType = livingType
#         session.add(livingRoom)
        
#     session.flush()

#     log.debug("Locations")
#     #Each House Should have a Master Bed room
#     loc1_Master = session.query(models.Location).filter_by(houseId=house1.id,roomId = masterBed.id).first()
#     if loc1_Master is None:
#         loc1_Master = models.Location(houseId = house1.id,
#                                     roomId = masterBed.id)
#         session.add(loc1_Master)

#     loc2_Master = session.query(models.Location).filter_by(houseId=house2.id,roomId = masterBed.id).first()
#     if loc2_Master is None:
#         loc2_Master = models.Location(houseId = house2.id,
#                                     roomId = masterBed.id)
#         session.add(loc2_Master)

#     #Each House Should Also have a Living Rooms
#     loc1_Living = session.query(models.Location).filter_by(houseId=house1.id,roomId=livingRoom.id).first()
#     if loc1_Living is None:
#         loc1_Living = models.Location(houseId = house1.id,
#                                       roomId = livingRoom.id)
#         session.add(loc1_Living)

#     loc2_Living = session.query(models.Location).filter_by(houseId=house2.id,roomId=livingRoom.id).first()
#     if loc2_Living is None:
#         loc2_Living = models.Location(houseId = house2.id,
#                                       roomId = livingRoom.id)
#         session.add(loc2_Living)

#     #And Lets be Generous and Give the First House a Second Bedroom
#     loc1_Second = session.query(models.Location).filter_by(houseId = house1.id,
#                                                            roomId = secondBed.id).first()
#     if loc1_Second is None:
#         loc1_Second = models.Location(houseId = house1.id,
#                                       roomId = secondBed.id)
#         session.add(loc1_Second)



#     session.flush()

#     #Create Nodes and Sensors
#     log.debug("Nodes")
#     node37 = session.query(models.Node).filter_by(id=37).first()
#     if node37 is None:
#         node37 = models.Node(id=37)
#         session.add(node37)

#     node38 = session.query(models.Node).filter_by(id=38).first()
#     if node38 is None:
#         node38 = models.Node(id=38)
#         session.add(node38)

#     node39 = session.query(models.Node).filter_by(id=39).first()
#     if node39 is None:
#         node39 = models.Node(id=39)
#         session.add(node39)

#     node40 = session.query(models.Node).filter_by(id=40).first()
#     if node40 is None:
#         node40 = models.Node(id=40)
#         session.add(node40)

#     node69 = session.query(models.Node).filter_by(id=69).first()
#     if node69 is None:
#         node69 = models.Node(id=69)
#         session.add(node69)

#     node70 = session.query(models.Node).filter_by(id=70).first()
#     if node70 is None:
#         node70 = models.Node(id=70)
#         session.add(node70)

#     node50 = session.query(models.Node).filter_by(id=50).first()
#     if node50 is None:
#         node50 = models.Node(id=50)
#         session.add(node50)
        
#     session.flush()
#     session.commit()
#     log.debug("Sensors")
#     #We want to work only with temperature database
#     tempType = session.query(models.SensorType).filter_by(name="Temperature").first()   
#     if tempType is None:
#         tempType = models.SensorType(name="Temperature")
#         session.add(tempType)
#     session.flush()
#     #session.commit()

#     #To make iterating through locations a little easier when adding samples
#     locs = [node37,node38,node39,node40,node69,node70]


#     #While Technically it would be a good idea to have sensor's 
#     #We may be able to get away with just having sensor types
#     #However they are needed for the Visualiser so we can add them here.
#     for item in locs:
#         theSensor = session.query(models.Sensor).filter_by(sensorTypeId =tempType.id,
#                                                            nodeId=item.id).first()
#         if theSensor is None:
#             theSensor = models.Sensor(sensorTypeId=tempType.id,
#                                       nodeId=item.id,
#                                       calibrationSlope=1,
#                                       calibrationOffset=0)
#             session.add(theSensor)
        
#     session.flush()

#     #Zap all old data
#     for item in locs:
#         theQry = session.query(models.Reading).filter_by(nodeId=item.id,
#                                                          typeId=tempType.id)
#         theQry.delete()

#     #And state history
#     theQry = session.query(models.NodeState).delete()
#     session.flush()
    

#     #Next Add some data for each node

#     #Deployment 1 Lasts for 2 Days, Pretend we have a sampling rate of 1 samples per hour
#     #Match Nodes and Locations (1 Node for Each Bedroom + 2 in the Living Room)
#     node37.location = loc1_Master
#     node38.location = loc1_Second
#     node39.location = loc1_Living

#     session.flush()

#     #Add some node state information
#     #To start a true star network
#     for item in [37,38,39]:
#         theState = models.NodeState(time=now,
#                                     nodeId = item,
#                                     parent=40974,
#                                     localtime = 0)
#         session.add(theState)

#     session.flush()
    
#     #Lets also fake a rejig of the nodestate about a day into the depoyment
#     #With a tree along the lines of <base> -> [node37,node38 -> [node39,node40]]
#     for item in [39,40]:
#         theState = models.NodeState(time=now+timedelta(hours=24),
#                                     nodeId = item,
#                                     parent = 38,
#                                     localtime = 48)

#         session.add(theState)
#         session.flush()
#     session.flush()
    
#     #Add Data (Deal with node 40 seperately as this is a corner case
#     log.debug("Readings1 ")
#     locs = [node37,node38,node39]
#     for x in range(2*24):
#     #for x in range(3):
#         insertDate = now+timedelta(hours = x)
#         for item in locs:
#             #Composite Key not working in Reading
#             session.add(models.Reading(time=insertDate,
#                                        nodeId=item.id,
#                                        typeId=tempType.id,
#                                        locationId=item.location.id,
#                                        value=item.id + x))
#     session.flush()

#     log.debug("Readings2")
#     #But we also get overZealous with Node 40
#     #For the first week it is in the Living Room
#     node40.location = loc1_Living
#     for x in range(1*24):
#         insertDate = now+timedelta(hours = x)
#         session.add(models.Reading(time =insertDate,
#                                    nodeId=node40.id,
#                                    typeId=tempType.id,
#                                    locationId=node40.location.id,
#                                    value=node40.id+x))

#     session.flush()
#     #But we then move it to the Master Bedroom
#     node40.location = loc1_Master
#     for x in range(1*24):
#         insertDate = house2Start+timedelta(hours = x)
#         session.add(models.Reading(time =insertDate,
#                                    nodeId=node40.id,
#                                    typeId=tempType.id,
#                                    locationId=node40.location.id,
#                                    value=node40.id+(24+x)))

#     #TODO: Our Data for the Living room node 40 disapears in the visualiser
#     session.flush()



#     #We then Go to Deployment 2 it lasts for 1 day
#     #Match nodes and Locations 1 Node in Bed and Living Room
#     node69.location = loc2_Master
#     node70.location = loc2_Living
    
#     #Add some node state information here too
#     # Chain base2( 40975) -> node69 -> node70
#     session.add(models.NodeState(time=house2Start,
#                                  nodeId = 69,
#                                  parent = 40975,
#                                  localtime = 0))
#     session.add(models.NodeState(time=house2Start,
#                                  nodeId = 70,
#                                  parent = 69,
#                                  localtime = 0))
#     session.flush()
                
#     log.debug("Readings 3")
#     locs = [node69,node70]
#     for x in range(1*24):
#     #for x in range(3):
#         insertDate = house2Start+timedelta(hours = x)
#         for item in locs:
#             #Composite Key not working in Reading
#             session.add(models.Reading(time=insertDate,
#                                        nodeId=item.id,
#                                        typeId=tempType.id,
#                                        locationId=item.location.id,
#                                        value=item.id + x))

#     log.debug("All items added. Committing")
#     session.flush()
#     session.commit()
#     session.close()
#     log.debug("Testing Data added")



# # log.debug("Configuring Test")
# # #Fetch the database URL from the configuration file
# # confFile = open("test.ini")
# # config = ConfigParser.ConfigParser()
# # #Read the config file
# # config.readfp(confFile)

# # dburl = config.get("app:main","sqlalchemy.url")
# # log.debug("DB URL is {0}".format(dburl))



# # #dburl = "mysql://root:Ex3lS4ga@127.0.0.1/testStore"

# # #And Create all the Database Stuff
# # engine = create_engine(dburl)
# # models.initialise_sql(engine)
# # log.debug("Setup Testing Class with engine {0}".format(engine))
# # populateData.init_data()
# # Session = sessionmaker(bind=engine)
# # print "Creating Testing DB"
# # createTestDB()
# # print "Done"
# # #engine.shutdown()
