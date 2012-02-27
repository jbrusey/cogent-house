"""Metaclass to initiate all objects and start the database.

This really just makes sure all database code is in the same place
meaing the DB is consistently intiataed in all test cases.
"""


"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

engine = sqlalchemy.create_engine("sqlite:///:memory:",echo=False)
Base.metadata.create_all(engine)
Session = sqlalchemy.orm.sessionmaker(bind=engine)

    
#Create our Test Objects
session = Session()

"""

#CONFIG
DB_URL = 'sqlite:///:memory:'

#sqlalchemy Imports
import sqlalchemy


try:
    import cogent
except ImportError:
    #Assume we are running from the test directory
    #print "Unable to Import Cogent Module Appending Path"
    import sys
    sys.path.append("../")

#Import our Base Metadata etc
#from cogent.base.model import *
#Base = cogent.models.
#from cogent.base.model.meta import Session, Base
from cogent.base.model.meta import Base

engine = sqlalchemy.create_engine(DB_URL)#,echo=True)
Base.metadata.create_all(engine)

Session = sqlalchemy.orm.sessionmaker(bind=engine)
#print engine

import datetime
try:
    import cogent
except ImportError:
    #Assume we are running from the test directory
    print "Unable to Import Cogent Module Appending Path"
    import sys
    sys.path.append("../")

import cogent.base.model as models

def createTestDB():
    """Function to populate a testing DB"""
    #session = meta.Session()    
    session = Session()
    #transaction.begin()
    #First Create a Deployment

    now = datetime.datetime.now()

    #See if we need to add these items
    theQry = session.query(models.Deployment).filter_by(name="test").first()
    if theQry is not None:
        return True
    

    theDeployment = models.Deployment(name="test",
                                      description="testing",
                                      startDate = now,
                                      endDate = now + datetime.timedelta(days=2),
                                      )

    session.add(theDeployment)
    session.flush()
    #I Also want to add a couple of houses
    house1 = models.House(deploymentId = theDeployment.id,
                          address = "add1",
                          startDate = now,
                          endDate = now+datetime.timedelta(days=1),
                          )

    house2 = models.House(deploymentId = theDeployment.id,
                          address = "add2",
                          startDate = now+datetime.timedelta(days=1),
                          endDate = now+datetime.timedelta(days=2),
                          )

    session.add(house1)
    session.add(house2)
    session.flush()

    #Lets Say that each room has a bedroom and a bathroom...

    # create types
    bedType = models.RoomType(name="bedroom")
    bathType = models.RoomType(name="bathroom")
    
    #Rooms themselves
    bed1 = models.Room(name="Bedroom_H1")
    bed2 = models.Room(name="Bedroom_H2")
    bed1.roomtype = bedType
    bed2.roomtype = bedType
    
    session.add(bed1)
    session.add(bed2)

    bath1 = models.Room(name="bathroom",roomType = bathType)
    bath2 = models.Room(name="bathroom",roomType = bathType)
    session.add(bath1)
    session.add(bath2)

    session.flush()
    #Finally tie these rooms to a location

    locBed1 = models.Location(houseId = house1.id,
                              roomId = bed1.id)
    locBath1 = models.Location(houseId = house1.id,
                               roomId = bath1.id)
    locBed2 = models.Location(houseId = house2.id,
                              roomId = bed2.id)
    locBath2 = models.Location(houseId = house2.id,
                               roomId = bath2.id)
    session.add(locBed1)
    session.add(locBed2)
    session.add(locBath1)
    session.add(locBath2)
    
    session.flush()

    
    #We want some sensor types 
    tempSensor = models.SensorType(id=101,name="temp") 
    humSensor = models.SensorType(id=102,name="hum")
    vocSensor = models.SensorType(id=103,name="voc")
    session.add(tempSensor)
    session.add(humSensor)
    session.add(vocSensor)

    #Node Types
    stdNode = models.NodeType(id=101,
                              name="stdNode")
    vocNode = models.NodeType(id=102,
                             name="vocNode")
    session.add(stdNode)
    session.add(vocNode)
    session.flush()
                             
    #And Some Nodes
    nodeBed1 = models.Node(id=111,
                           locationId=locBed1.id,
                           nodeTypeId=stdNode.id)
    nodeBath1 = models.Node(id=121,
                            locationId=locBath1.id,
                            nodeTypeId=stdNode.id)

    bed1.nodes.append(nodeBed1)
    bath1.nodes.append(nodeBath1)
    session.add(nodeBed1)
    session.add(nodeBath1)

    #Make it a bit trickier as we have two nodes in this bedroom
    nodeBed21 = models.Node(id=211,
                            locationId = locBed2.id,
                            nodeTypeId = stdNode.id)
    nodeBed22 = models.Node(id=212,
                            locationId = locBed2.id,
                            nodeTypeId = vocNode.id)

    bed2.nodes.append(nodeBed21)
    bed2.nodes.append(nodeBed22)
    session.add(nodeBed21)
    session.add(nodeBed22)
    #We also Reuse the Node that was in Bath1, and move it into Bath2
    # nodeBath2 = models.Node(id=221,
    #                        locationId = locBath2.id,
    #                        nodeTypeId = stdNode.id)
    
    bath2.nodes.append(nodeBath1)
    nodeBath1.locationId = locBath2.id
    session.flush()

    #And Some Sensors 
    #Node Bed1( Std Sensor)
    session.add(models.Sensor(sensorTypeId = tempSensor.id,
                              nodeId = nodeBed1.id,
                              calibrationSlope = 1.0,
                              calibrationOffset = 0.0))
    session.add(models.Sensor(sensorTypeId = humSensor.id,
                              nodeId = nodeBed1.id,
                              calibrationSlope = 1.0,
                              calibrationOffset = 0.0))
    #Node Bath 2 (std)
    session.add(models.Sensor(sensorTypeId = tempSensor.id,
                              nodeId = nodeBath1.id,
                              calibrationSlope = 1.0,
                              calibrationOffset = 1.0))
    session.add(models.Sensor(sensorTypeId = humSensor.id,
                              nodeId = nodeBath1.id,
                              calibrationSlope = 1.0,
                              calibrationOffset = 0.0))
    #Node Bed21 (std)
    session.add(models.Sensor(sensorTypeId = tempSensor.id,
                              nodeId = nodeBed21.id,
                              calibrationSlope = 1.0,
                              calibrationOffset = 0.0))
    session.add(models.Sensor(sensorTypeId = humSensor.id,
                              nodeId = nodeBed21.id,
                              calibrationSlope = 1.0,
                              calibrationOffset = 0.0))

    #Node Bed22 (voc)
    session.add(models.Sensor(sensorTypeId = tempSensor.id,
                              nodeId = nodeBed22.id,
                              calibrationSlope = 1.0,
                              calibrationOffset = 0.0))
    session.add(models.Sensor(sensorTypeId = humSensor.id,
                              nodeId = nodeBed22.id,
                              calibrationSlope = 1.0,
                              calibrationOffset = 0.0))
    session.add(models.Sensor(sensorTypeId = vocSensor.id,
                              nodeId = nodeBed22.id,
                              calibrationSlope = 1.0,
                              calibrationOffset = 0.0))

    session.flush()
    #Finally we want some readings to keep It simple we will just focus temperature sensors
    
    #For all Nodes
    #Type Id = 101
    #Location (Derive from NodeID)


    #Reading is, time,nodeid,typeid,locationid,value

    #Deal with the first House
    for x in range(10):
        #Bedroom [House1 (0-1week) Bed 1.1 (Nodeid = 111) (LocBed1)]
        theReading = models.Reading(time=now+datetime.timedelta(seconds=x*60),
                                    nodeId=111,
                                    typeId=tempSensor.id,
                                    locationId=locBed1.id,
                                    value=1.0)
        session.add(theReading)

        #And the bathroom [121]
        theReading = models.Reading(time=now+datetime.timedelta(seconds=x*60),
                                    nodeId=121,
                                    typeId=tempSensor.id,
                                    locationId=locBath1.id,
                                    value=1.0)
        session.add(theReading)
                                    

    session.flush()

    #And the Second House
    secondTime = now+datetime.timedelta(days=1)
    for x in range(10):
        #Bed 2.2 (1-2week) Bed 2.2 (Nodeid = 211)  
        theReading = models.Reading(time=secondTime+datetime.timedelta(seconds=x*60),
                                    nodeId=211,
                                    typeId=tempSensor.id,
                                    locationId=locBed2.id,
                                    value=1.0)
        session.add(theReading)

        theReading = models.Reading(time=secondTime+datetime.timedelta(seconds=x*60),
                                    nodeId=212,
                                    typeId=tempSensor.id,
                                    locationId=locBed2.id,
                                    value=2.0)
        session.add(theReading)

        #And the bathroom [121]
        theReading = models.Reading(time=secondTime+datetime.timedelta(seconds=x*60),
                                    nodeId=121,
                                    typeId=tempSensor.id,
                                    locationId=locBath2.id,
                                    value=2.0)
        session.add(theReading)
                                    

    session.flush()

#    import pprint
#    pprint.pprint(theDeployment.flatten())    

    session.commit()
    #transaction.commit()


    
    
