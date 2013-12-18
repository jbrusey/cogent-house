"""
Data Generation Functions to test Push Functionality
"""

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

#LOCAL_URL = "sqlite:///local.db"
LOCAL_URL = 'mysql://test_user:test_user@localhost/pushSource'

import cogent
import cogent.base.model as models
import cogent.base.model.meta as meta
import sqlalchemy
import time
from datetime import datetime
from datetime import timedelta

READING_GAP = 10
STATE_SWITCH = 100

class Datagen(object):
    def __init__(self):
        log.debug("Initialising Push Script")
        engine = sqlalchemy.create_engine(LOCAL_URL)
        
        #Intialise the databse
        models.initialise_sql(engine)
        models.populate_data()

        #Get relevant models etc
        session = meta.Session()
        
        #Check if our data exists
        theDeployment = session.query(models.Deployment).filter_by(name="PushTest").first()
        if theDeployment is None:
            log.debug("--> Create New Deployment")
            #Create a new Deployment
            theDeployment = models.Deployment(name="PushTest")
            session.add(theDeployment)
            session.flush()
        log.debug("Deployment is {0}".format(theDeployment))
            
        theHouse = session.query(models.House).filter_by(address="Push Address").first()
        if theHouse is None:
            log.debug("--> Create new House")
            theHouse = models.House(address="Push Address",deploymentId=theDeployment.id)
            session.add(theHouse)
            session.flush()

        log.debug("House is {0}".format(theHouse))
        #Two Rooms
        
        roomType = session.query(models.RoomType).filter_by(name="Bedroom").first()

        masterBed = session.query(models.Room).filter_by(name="Master Bedroom").first()
        if masterBed is None:
            masterBed = models.Room(name="Master Bedroom",roomTypeId=roomType.id)
            session.add(masterBed)
            
        secondBed = session.query(models.Room).filter_by(name="Second Bedroom").first()
        if secondBed is None:
            secondBed = models.Room(name="Second Bedroom",roomTypeId=roomType.id)
            session.add(secondBed)
        session.flush()
            

        #Locations
        masterLoc = session.query(models.Location).filter_by(houseId = theHouse.id,roomId=masterBed.id).first()
        
        if masterLoc is None:
            log.debug("Create New Master Location")
            masterLoc = models.Location(houseId=theHouse.id,
                                        roomId = masterBed.id)
            session.add(masterLoc)
        
        secondLoc = session.query(models.Location).filter_by(houseId=theHouse.id,
                                                             roomId=secondBed.id).first()
        if secondLoc is None:
            log.debug("Create New Second Location")
            secondLoc = models.Location(houseId = theHouse.id,
                                        roomId = secondBed.id)
            session.add(secondLoc)
        
        session.flush()
        log.debug("Master Location {0}".format(masterLoc))
        log.debug("Second Location {0}".format(secondLoc))

        #Add Nodes to each Location
        node37 = session.query(models.Node).filter_by(id=37).first()
        if not node37:
            node37 = models.Node(id=37)
            session.add(node37)

        node38 = session.query(models.Node).filter_by(id=38).first()
        if node38 is None:
            node38 = models.Node(id=38)
            session.add(node38)
                  
        node37.location = masterLoc
        node38.location = secondLoc
        session.flush()

        #All Our Data adding script needs to worry about is the Nodes
        self.node37 = node37
        self.node38 = node38

        #Finally add an Upload URL if required
        theUrl = session.query(models.UploadURL).filter_by(url="dang@127.0.0.1").first()
        if not theUrl:
            theUrl = models.UploadURL(url="dang@127.0.0.1",
                                      dburl="mysql://test_user:test_user@localhost:3307/pushTest")
            session.add(theUrl)
        
        theUrl = session.query(models.UploadURL).filter_by(url="dang@cogentee.coventry.ac.uk").first()
        if not theUrl:
            theUrl = models.UploadURL(url="dang@cogentee.coventry.ac.uk",
                                      dburl="mysql://dang:j4a77aec@localhost:3307/chtest")
            session.add(theUrl)

        session.commit()

    def addMany(self):
        """Add around 1 million records to the database"""
        """Add about 2000 Records to the Database"""
        session = meta.Session()
        localCount = 0
        stateOne = True
        fakeTime = datetime.now()

        node37 = self.node37
        node38 = self.node38

        totalCount = 0
        try:
            #while totalCount < 500000:
            while totalCount < 100000:
                #Add a reading every N seconds
                #log.debug("Adding New Reading {0}".format(fakeTime))

                theReading = models.Reading(time = fakeTime,
                                            nodeId = node37.id,
                                            locationId = node37.locationId,
                                            value = localCount,
                                            typeId = 0)
                session.add(theReading)

                theReading = models.Reading(time = fakeTime,
                                            nodeId = node38.id,
                                            locationId = node38.locationId,
                                            value = 100-localCount,
                                            typeId = 0)            
                session.add(theReading)
                session.flush()
                if localCount == STATE_SWITCH:
                    log.debug("Switching States")
                    localCount = 0

                    #Add a node state
                    if stateOne:
                        theState = models.NodeState(time=fakeTime,
                                                    nodeId=node37.id,
                                                    parent = 1024,
                                                    localtime = 0)
                        session.add(theState)

                        theState = models.NodeState(time=fakeTime,
                                                    nodeId=node38.id,
                                                    parent = 1024,
                                                    localtime = 0)
                        session.add(theState)        
                    else:
                        theState = models.NodeState(time=fakeTime,
                                                    nodeId=node37.id,
                                                    parent = node38.id,
                                                    localtime = 0)
                        session.add(theState)

                        theState = models.NodeState(time=fakeTime,
                                                    nodeId=node38.id,
                                                    parent = 1024,
                                                    localtime = 0)
                        session.add(theState)

                    stateOne = not stateOne
                    session.flush()
                    session.commit
                    log.debug("Commiting Samples {0}".format(totalCount))
                else:
                    localCount += 1

                #time.sleep(READING_GAP)
                totalCount += 1
                fakeTime = fakeTime + timedelta(seconds=10)
                #session.commit()
        except KeyboardInterrupt:
            log.debug("Closing Everything down")
            session.flush()
            session.commit()
       

        session.flush()
        session.commit()

    def run(self):
        session = meta.Session()
        localCount = 0
        stateOne = True

        node37 = self.node37
        node38 = self.node38

        try:
            while True:
                #Add a reading every N seconds
                log.debug("Adding New Reading {0}".format(datetime.now()))

                theReading = models.Reading(time = datetime.now(),
                                            nodeId = node37.id,
                                            locationId = node37.locationId,
                                            value = localCount,
                                            typeId = 0)
                session.add(theReading)

                theReading = models.Reading(time = datetime.now(),
                                            nodeId = node38.id,
                                            locationId = node38.locationId,
                                            value = 100-localCount,
                                            typeId = 0)            
                session.add(theReading)
                session.flush()
                if localCount == STATE_SWITCH:
                    log.debug("Switching States")
                    localCount = 0

                    #Add a node state
                    if stateOne:
                        theState = models.NodeState(time=datetime.now(),
                                                    nodeId=node37.id,
                                                    parent = 1024,
                                                    localtime = 0)
                        session.add(theState)

                        theState = models.NodeState(time=datetime.now(),
                                                    nodeId=node38.id,
                                                    parent = 1024,
                                                    localtime = 0)
                        session.add(theState)        
                    else:
                        theState = models.NodeState(time=datetime.now(),
                                                    nodeId=node37.id,
                                                    parent = node38.id,
                                                    localtime = 0)
                        session.add(theState)

                        theState = models.NodeState(time=datetime.now(),
                                                    nodeId=node38.id,
                                                    parent = 1024,
                                                    localtime = 0)
                        session.add(theState)

                    stateOne = not stateOne
                    session.flush()
                else:
                    localCount += 1

                time.sleep(READING_GAP)
                session.commit()
        except KeyboardInterrupt:
            log.debug("Closing Everything down")
            session.flush()
            session.commit()


if __name__ == "__main__":
    datagen = Datagen()
    #datagen.run()
    datagen.addMany()
