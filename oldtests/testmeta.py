"""Metaclass to bring everything together in a simulation of a Pyramid environment

This really just makes sure all database code is in the same place
meaing the DB is consistently intiataed in all test cases.
"""

#sqlalchemy Imports
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import sys
import os
import unittest

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
viewer = False

import ConfigParser

import cogent
import cogent.base.model as models
import cogent.base.model.meta as meta   
import cogent.base.model.populateData as populateData


from datetime import datetime, timedelta


class BaseTestCase(unittest.TestCase):
    """
    Deal with tables in the house module
    """
    @classmethod
    def setUpClass(self):
        """Called the First time this class is called.
        This means that we can Init the testing database once per testsuite
        """
        
        #Parse the Config File
        try:
            confFile = open("setup.conf")
        except IOError:
            try:
                confFile = open("tests/setup.conf")
            except IOError:
                confFile = open("cogentviewer/tests/setup.conf")


        config = ConfigParser.ConfigParser()
        #Read the File
        config.readfp(confFile)
        
        #And pull out the DB Url
        dburl = config.get("TestDB","dbString")
        log.debug("DB URL is {0}".format(dburl))

        engine = create_engine(dburl)
        self.engine = engine
        models.initialise_sql(engine)
        log.debug("Setup Testing Class with engine {0}".format(engine))
        self.engine = engine
        populateData.init_data()
        self.Session = sqlalchemy.orm.sessionmaker(bind=engine)
        #createTestDB(self.Session())

    def setUp(self):
        """Called each time a test case is called, I wrap each
        testcase in a transaction, this means that nothing is saved to
        the database between testcases, while still allowing "fake" commits
        in the individual testcases.

        This means there should be no unexpected items in the DB."""
        #Pyramid Version
        try:
            self.config = testing.setUp()
        except:
            pass
        connection = self.engine.connect()
        self.transaction = connection.begin()
        self.session = self.Session()
        self.session.bind=connection

    def tearDown(self):
        """
        Called after each testcase,
        Uncommits any changes that test case made
        """
        
        #Pyramid
        try:
            self.transaction.abort()
            testing.tearDown()
        except:
            self.transaction.rollback()
            self.session.close()


#Build a complete testing database
def createTestDB(session=False,now=False):
    """Create a complete Testing Database
    :param session: Session to use if not the global DB session
    :param now: Time to use to setup the database
    """

    log.debug("Add Testing Data")
    if not session:
        session = Session()

        
    if not now:
        now = datetime.now()
    deploymentEnd = now + timedelta(days=2)
    house2Start = now + timedelta(days=1)
    
    
    #See if we need to add these items
    theDeployment = session.query(models.Deployment).filter_by(name="test").first()
    #if theQry is not None:
    #    return True
    if theDeployment is None:
        theDeployment = models.Deployment(name="test",
                                          description="testing",
                                          startDate = now,
                                          endDate = deploymentEnd,
                                          )

        session.add(theDeployment)
        session.flush()
    else:
        theDeployment.update(startDate=now,
                             endDate=deploymentEnd)
    
    #I Also want to add a couple of houses
    #The First House runs for One day
    house1 = session.query(models.House).filter_by(address="add1").first()
    if house1 is None:
        house1 = models.House(deploymentId = theDeployment.id,
                              address = "add1",
                              startDate = now,
                              endDate = deploymentEnd,
                              )
        session.add(house1)
    else:
        house1.update(startDate = now,
                      endDate = deploymentEnd)

    house2 = session.query(models.House).filter_by(address="add2").first()
    if house2 is None:
        house2 = models.House(deploymentId = theDeployment.id,
                              address = "add2",
                              startDate = house2Start,
                              endDate = deploymentEnd,
                              )
        session.add(house2)
    else:
        house2.update(startDate = house2Start,
                      endDate = deploymentEnd)

    session.flush()
    
    #Lets Add Some Rooms (Using Bruseys new Room Paradigm)

    #Get the Relevant Room Types
    bedroomType = session.query(models.RoomType).filter_by(name="Bedroom").first()
    if bedroomType is None:
        bedroomType = models.RoomType(name="Bedroom")
        session.add(bedroomType)

    livingType = session.query(models.RoomType).filter_by(name="Living Room").first()
    if livingType is None:
        livingType = models.RoomType(name="Living Room")
        session.add(livingType)

    session.flush()

    #And the Specific Rooms themselves
    masterBed = session.query(models.Room).filter_by(name="Master Bedroom").first()
    if masterBed is None:
        #(Note) We can either add room type by Id
        masterBed = models.Room(name="Master Bedroom",roomTypeId=bedroomType.id)
        session.add(masterBed)

    secondBed = session.query(models.Room).filter_by(name="Second Bedroom").first()
    if secondBed is None:
        #Or We can do it the easier way
        secondBed = models.Room(name="Second Bedroom")
        secondBed.roomType = bedroomType
        session.add(secondBed)
    
    #Add a Living Room too
    livingRoom = session.query(models.Room).filter_by(name="Living Room").first()
    if livingRoom is None:
        livingRoom = models.Room(name="Living Room")
        livingRoom.roomType = livingType
        session.add(livingRoom)
        
    session.flush()

    #Each House Should have a Master Bed room
    loc1_Master = session.query(models.Location).filter_by(houseId=house1.id,roomId = masterBed.id).first()
    if loc1_Master is None:
        loc1_Master = models.Location(houseId = house1.id,
                                    roomId = masterBed.id)
        session.add(loc1_Master)

    loc2_Master = session.query(models.Location).filter_by(houseId=house2.id,roomId = masterBed.id).first()
    if loc2_Master is None:
        loc2_Master = models.Location(houseId = house2.id,
                                    roomId = masterBed.id)
        session.add(loc2_Master)

    #Each House Should Also have a Living Rooms
    loc1_Living = session.query(models.Location).filter_by(houseId=house1.id,roomId=livingRoom.id).first()
    if loc1_Living is None:
        loc1_Living = models.Location(houseId = house1.id,
                                      roomId = livingRoom.id)
        session.add(loc1_Living)

    loc2_Living = session.query(models.Location).filter_by(houseId=house2.id,roomId=livingRoom.id).first()
    if loc2_Living is None:
        loc2_Living = models.Location(houseId = house2.id,
                                      roomId = livingRoom.id)
        session.add(loc2_Living)

    #And Lets be Generous and Give the First House a Second Bedroom
    loc1_Second = session.query(models.Location).filter_by(houseId = house1.id,
                                                           roomId = secondBed.id).first()
    if loc1_Second is None:
        loc1_Second = models.Location(houseId = house1.id,
                                      roomId = secondBed.id)
        session.add(loc1_Second)



    session.flush()

    #Create Nodes and Sensors
    
    node37 = session.query(models.Node).filter_by(id=37).first()
    if node37 is None:
        node37 = models.Node(id=37)
        session.add(node37)

    node38 = session.query(models.Node).filter_by(id=38).first()
    if node38 is None:
        node38 = models.Node(id=38)
        session.add(node38)

    node39 = session.query(models.Node).filter_by(id=39).first()
    if node39 is None:
        node39 = models.Node(id=39)
        session.add(node39)

    node40 = session.query(models.Node).filter_by(id=40).first()
    if node40 is None:
        node40 = models.Node(id=40)
        session.add(node40)

    node69 = session.query(models.Node).filter_by(id=69).first()
    if node69 is None:
        node69 = models.Node(id=69)
        session.add(node69)

    node70 = session.query(models.Node).filter_by(id=70).first()
    if node70 is None:
        node70 = models.Node(id=70)
        session.add(node70)

    node50 = session.query(models.Node).filter_by(id=50).first()
    if node50 is None:
        node50 = models.Node(id=50)
        session.add(node50)
        

    #We want to work only with temperature database
    tempType = session.query(models.SensorType).filter_by(name="Temperature").first()   
    if tempType is None:
        tempType = models.SensorType(id=0,name="Temperature")
        session.add(tempType)
    session.flush()
    session.commit()

    #To make iterating through locations a little easier when adding samples
    locs = [node37,node38,node39,node40,node69,node70]


    #While Technically it would be a good idea to have sensor's 
    #We may be able to get away with just having sensor types
    #However they are needed for the Visualiser so we can add them here.
    for item in locs:
        theSensor = session.query(models.Sensor).filter_by(sensorTypeId =tempType.id,
                                                           nodeId=item.id).first()
        if theSensor is None:
            theSensor = models.Sensor(sensorTypeId=tempType.id,
                                      nodeId=item.id,
                                      calibrationSlope=1,
                                      calibrationOffset=0)
            session.add(theSensor)
        
    session.flush()

    #Zap all old data
    for item in locs:
        theQry = session.query(models.Reading).filter_by(nodeId=item.id,
                                                         typeId=tempType.id)
        theQry.delete()

    #And state history
    theQry = session.query(models.NodeState).delete()
    session.flush()
    

    #Next Add some data for each node

    #Deployment 1 Lasts for 2 Days, Pretend we have a sampling rate of 1 samples per hour
    #Match Nodes and Locations (1 Node for Each Bedroom + 2 in the Living Room)
    node37.location = loc1_Master
    node38.location = loc1_Second
    node39.location = loc1_Living

    session.flush()

    #Add some node state information
    #To start a true star network
    for item in [37,38,39]:
        theState = models.NodeState(time=now,
                                    nodeId = item,
                                    parent=40974,
                                    localtime = 0)
        session.add(theState)

    session.flush()
    
    #Lets also fake a rejig of the nodestate about a day into the depoyment
    #With a tree along the lines of <base> -> [node37,node38 -> [node39,node40]]
    for item in [39,40]:
        theState = models.NodeState(time=now+timedelta(hours=24),
                                    nodeId = item,
                                    parent = 38,
                                    localtime = 48)

        session.add(theState)
        session.flush()
    session.flush()
    
    #Add Data (Deal with node 40 seperately as this is a corner case

    locs = [node37,node38,node39]
    for x in range(2*24):
    #for x in range(3):
        insertDate = now+timedelta(hours = x)
        for item in locs:
            #Composite Key not working in Reading
            session.add(models.Reading(time=insertDate,
                                       nodeId=item.id,
                                       typeId=tempType.id,
                                       locationId=item.location.id,
                                       value=item.id + x))
    session.flush()

    #But we also get overZealous with Node 40
    #For the first week it is in the Living Room
    node40.location = loc1_Living
    for x in range(1*24):
        insertDate = now+timedelta(hours = x)
        session.add(models.Reading(time =insertDate,
                                   nodeId=node40.id,
                                   typeId=tempType.id,
                                   locationId=node40.location.id,
                                   value=node40.id+x))

    session.flush()
    #But we then move it to the Master Bedroom
    node40.location = loc1_Master
    for x in range(1*24):
        insertDate = house2Start+timedelta(hours = x)
        session.add(models.Reading(time =insertDate,
                                   nodeId=node40.id,
                                   typeId=tempType.id,
                                   locationId=node40.location.id,
                                   value=node40.id+(24+x)))

    #TODO: Our Data for the Living room node 40 disapears in the visualiser
    session.flush()

    #We then Go to Deployment 2 it lasts for 1 day
    #Match nodes and Locations 1 Node in Bed and Living Room
    node69.location = loc2_Master
    node70.location = loc2_Living
    
    #Add some node state information here too
    # Chain base2( 40975) -> node69 -> node70
    session.add(models.NodeState(time=house2Start,
                                 nodeId = 69,
                                 parent = 40975,
                                 localtime = 0))
    session.add(models.NodeState(time=house2Start,
                                 nodeId = 70,
                                 parent = 69,
                                 localtime = 0))
    session.flush()
                

    locs = [node69,node70]
    for x in range(1*24):
    #for x in range(3):
        insertDate = house2Start+timedelta(hours = x)
        for item in locs:
            #Composite Key not working in Reading
            session.add(models.Reading(time=insertDate,
                                       nodeId=item.id,
                                       typeId=tempType.id,
                                       locationId=item.location.id,
                                       value=item.id + x))
    session.flush()
    session.commit()
    session.close()
    log.debug("Testing Data added")
