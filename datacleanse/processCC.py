"""
Methods to upload the contents of a current cost database to the server

This module provides functionality to transfer data from eiher
databases created by the current cost logging functionality on the
Arch rock server, or the CSV files holding data from the Jodrell
Street deployments.

@author: Dan Goldsmith
@version: 0.1.1
@date: November 2011
"""

#Standard Python Library
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


import time
import csv
import datetime

#Sqlalchemy for local connection
import sqlalchemy
import sqlalchemy.orm

#Pyramid modules
from sqlalchemy.ext.declarative import declarative_base


localBase = declarative_base()

import mainDb
import models

class CCData(localBase):
    """Maps to Data table in current cost DB"""
    __tablename__ = "data"
    DeviceId = sqlalchemy.Column(sqlalchemy.Integer)
    DateTime = sqlalchemy.Column(sqlalchemy.DateTime, primary_key=True)
    Watts = sqlalchemy.Column(sqlalchemy.Float)
    kWh = sqlalchemy.Column(sqlalchemy.Float)

    def __init__(self, **kwargs):
        """Generalised Initialisation function.
        @param kwargs: Keyword arguments to initilise
        """
        self.update(kwargs)

    def update(self, theDict={}, **kwargs):
        """Generalized update function"""
        theDict.update(kwargs)

        for key, value in theDict.iteritems():
            setattr(self, key, value)

    def __repr__(self):
        return "{0}: {1} {2}".format(self.DateTime,
                                     self.Watts,
                                     self.kWh)



class CurrentCostParser():
    """Class to deal with uploading current cost data

    This file will take the data output by the perl / python current cost storage
    """
    def __init__(self,ccDb,houseName):
        """Initialise the Parser

        @param ccDb: Current Cost Database object
        """
        log.debug("Creating CC Parser")

        ccEngine = sqlalchemy.create_engine("sqlite:///{0}".format(ccDb))
        ccMetadata = localBase.metadata
        ccMetadata.create_all(ccEngine)

        self.Session = sqlalchemy.orm.sessionmaker(bind=ccEngine)
        self.houseName = houseName

    def createDeployment(self):
        """
        Create a new deployment and house etc on the Transfer Database
        """

        deploymentName = "archRock"
        houseName = self.houseName
        
        session = models.meta.Session()
        #Check for deployment

        theDep = session.query(models.Deployment).filter_by(name=deploymentName).first()
        log.debug("Checking for existing deployment {0}".format(theDep))
        if theDep is None:
            #Create a new deployment
            theDep = models.Deployment(name=deploymentName)
            session.add(theDep)
            session.flush()
            log.debug("Adding Deployment to database {0}".format(theDep))


        #And check for Houses
        theHouse = session.query(models.House).filter_by(address=houseName).first()
        log.debug("Checking for house {0}".format(theHouse))
        if theHouse is None:
            theHouse = models.House(address=houseName,
                                    deploymentId = theDep.id)
            session.add(theHouse)
            session.flush()
            log.debug("Adding New House {0}".format(theHouse))


        self.theHouse = theHouse
        #Create a location for this particular node
        
        theRoom = session.query(models.Room).filter_by(name="External").first()
        if theRoom is None:
            theRoom = models.Room(name="External",roomTypeId=1)
            session.add(theRoom)
            session.flush()

        log.debug("External Room is {0}".format(theRoom))

        #theLocation = models.Location(houseId = theHouse.id,roomId = theRoom.id)
        theLocation = session.query(models.Location).filter_by(houseId=theHouse.id,
                                                               roomId = theRoom.id).first()
        log.debug("Checking for existing location {0}".format(theLocation))
        if theLocation is None:
            theLocation = models.Location(houseId = theHouse.id,
                                          roomId = theRoom.id)
            session.add(theLocation)
            session.flush()

        self.theLocation = theLocation

        #Node / Node Type
        theNode = session.query(models.Node).filter_by(id=118118).first()
        if theNode is None:
            theNode = models.Node(id=118118)
            session.add(theNode)
            session.flush()
        log.debug("Node is {0}".format(theNode))
        self.theNode = theNode

        sensorType = session.query(models.SensorType).filter_by(name="Power").first()
        self.avgType = sensorType
        log.debug("Sensor is {0}".format(sensorType))
        
        sensorType = session.query(models.SensorType).filter_by(name="Power Min").first()
        self.minType = sensorType

        sensorType = session.query(models.SensorType).filter_by(name="Power Max").first()
        self.maxType = sensorType

        session.commit()

    def getReadings(self):
        session = self.Session()

        mainSession = models.meta.Session()
        theNode = self.theNode
        theLocation = self.theLocation
        avgType = self.avgType
        minType = self.minType
        maxType = self.maxType



        theQry = session.query(CCData).order_by(CCData.DateTime)

        #Check if there are allready readings for this House in the Database
        remoteQry = mainSession.query(models.Reading).filter_by(nodeId=theNode.id,
                                                                typeId = avgType.id,
                                                                locationId = theLocation.id,
                                                                )

        log.debug("Count of Data CC {0}  Remote {1}".format(theQry.count(),
                                                            remoteQry.count()))

        if remoteQry.count() > 100:
            log.warning("***** Looks like we have uploaded {0} *****".format(self.theHouse))
            return


        startTime = None
        readingArray = []
        #outArray = []
        timestamps = {}
        for item in theQry:
            theTime = item.DateTime
            if startTime == None:
                startTime = theTime
            
            timeDelta = theTime - startTime
            #log.debug("item: {0}  Start {1} Delta {2}".format(item,startTime,timeDelta))
            if timeDelta.total_seconds() >= (60*5): #5 Min Interval
                #log.debug("Time Jump")
                avg = sum(readingArray) / len(readingArray)
                minVal = min(readingArray)
                maxVal = max(readingArray)
                #log.debug("Average {0}".format(avg))
                #outArray.append([startTime,avg])
                
                if startTime in timestamps:
                    log.warning("Duplicate sample found for time {0} Avg is {1}/{2}".format(theTime,avg,timestamps[startTime]))
                    pass
                else:
                    hasSample = mainSession.query(models.Reading).filter_by(time=startTime,
                                                                            nodeId = theNode.id,
                                                                            typeId = avgType.id,
                                                                            locationId = theLocation.id).first()
                    if hasSample:
                        log.warning("Existing Sample {0}: {1} {2}".format(hasSample,avg,startTime))
                    else:
                        avgSample = models.Reading(time = startTime,
                                                   nodeId = theNode.id,
                                                   typeId = avgType.id,
                                                   locationId = theLocation.id,
                                                   value = avg)
                        #log.debug(avgSample)
                        mainSession.add(avgSample)
                        timestamps[startTime] = avg

                        minSample = models.Reading(time=startTime,
                                                   nodeId = theNode.id,
                                                   typeId = minType.id,
                                                   locationId = theLocation.id,
                                                   value=minVal)
                        mainSession.add(minSample)

                        maxSample = models.Reading(time=startTime,
                                                   nodeId = theNode.id,
                                                   typeId = maxType.id,
                                                   locationId = theLocation.id,
                                                   value=maxVal)

                        mainSession.add(maxSample)


                        mainSession.flush()
                    
                startTime = theTime
                readingArray = []


            readingArray.append(item.Watts)
        log.debug("Committing")
        mainSession.commit()
        #self.outArray = outArray
            
if __name__ == "__main__":
    #And initialise the other DB
    mainDb.initDB()

    EXCLUDE = ["/home/dang/svn/ArchrockDeployments/Data/CurrentCost/117+119Jodrell.db",]

    
    import glob 
    import os.path
    files = glob.glob("/home/dang/svn/ArchrockDeployments/Data/CurrentCost/*.db")
    #log.debug("Files are {0}".format(files))

    for fd in files:
        if fd in EXCLUDE:
            continue
        else:
            baseName = os.path.basename(fd)
            depName = baseName.split(".")[0]
            log.debug("Path {0} Base {1} House {2}".format(fd,baseName,depName))

            theParser = CurrentCostParser(fd,depName)
            theParser.createDeployment()
            theParser.getReadings()
    #theParser = CurrentCostParser("/home/dang/svn/ArchrockDeployments/Data/CurrentCost/117Jodrell.db","117 Jodrell Street")
    #theParser.createDeployment()
    #theParser.getReadings()

    
