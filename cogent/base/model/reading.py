"""
.. codeauthor::  Ross Wiklins 
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>
"""


import sqlalchemy
import logging
log = logging.getLogger(__name__)
import meta
Base = meta.Base


# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

import time

#To allow Calibration
import sensor 
import dateutil

class Reading(Base,meta.InnoDBMix):
    """Table to hold detils of readings,

    Reading has a composite primary key consisiting of time,nodeId,typeId

    :var DateTime time: Time reading was taken
    :var Integer nodeId: Id of :class:`cogentviewer.models.node.Node` that took this sample
    :var Integer typeId: Id of :class:`cogentviwer.models.sensortype.SensorType` that this reading came from
    :var Integer locationId: Id of :class:`cogentviewer.models.location.Location` that this reading came from

    :var float value: The sensor reading itself
    """
    __tablename__ = "Reading"


    time = Column(DateTime,
                  primary_key=True,
                  nullable=False,
                  autoincrement=False)
    nodeId = Column(Integer,
                    ForeignKey('Node.id'),
                    primary_key=True,
                    nullable=False,
                    autoincrement=False)

    typeId = Column('type', 
                    Integer, 
                    ForeignKey('SensorType.id'),
                    primary_key=True,
                    nullable=False,
                    autoincrement=False)

    locationId = Column(Integer,
                        ForeignKey('Location.id'),
                        autoincrement=False)

    value = Column(Float)    

    def __repr__(self):
        return "Reading(" + str(self.time) + "," + str(self.nodeId) + "," + str(self.typeId) + "," + str(self.value) + ")"
        
    
    #def __eq__(self,other):
    #    return self.value == other.value
    
    def __cmp__(self,other):
        #log.debug("Self {0}".format(self))
        #log.debug("Other {0}".format(other))
                  
        diffs = (self.time - other.time).seconds
        diffs += (self.nodeId - other.nodeId)
        diffs += (self.typeId - other.typeId)
        diffs += (self.locationId - other.locationId)
        diffs += (self.value - other.value)
        return 0
        
    def asJSON(self,slope=1,offset=0):
        """Return this reading as a JSON relevant tuple
        
        This should format the sample so it is parseable by JSON / Javascript
        That will allow it to be graphed using either DOJO or Highcharts

        The format is (time,value) where time is Unixtime in miliseconds
        
        .. warning::
        
            The original timestamp is multipled by 1000, to shift from seconds to miliseconds.
            As per the JSON / Javascript Standard.

        """

        return (time.mktime(self.time.timetuple()) * 1000,(self.value*slope)+offset)
        

    def getRawValues(self):
        """
        Return the Reading as a Tuple of (time,value)
        
        Unlike other methods this does no data processing, returning the Raw (rather than calibrated)
        sensor reading.

        :return DateTime time: Time that this reading was taken
        :return Float value: Value of the reading at this Time

        """

        return (self.time,self.value)

    def getCalibValues(self):
        """
        Return the Reading as a tuple of (time,calibratedValue)
        
        This returns the same as GetRawValues but will calibrate the data against stored values
        
        .. warning:
        
            This will issue an SQL statement for each reading we call the function on,
            Therefore it is only useful as a shortcut when dealing with a limited amount of readings
            
        
        
        :return DateTime time: Time that this reading was taken
        :return Float value: Value of the reading at this Time Calibrated against the sensor values
        """
        #pass
        #Find the Sensor
        session = meta.Session()
        theSensor = session.query(sensor.Sensor).filter_by(sensorTypeId = self.typeId,
                                                           nodeId = self.nodeId).first()
        #print theSensor
        
        value = (self.value * theSensor.calibrationSlope) + theSensor.calibrationOffset

        return (self.time,value)

    def toDict(self):
        """
        Helper Method to convert an object to a dictionary.

        This will return a dictionary object, representing this object.  As the
        Reading table does some trickery with reading.typeId remapping it to
        (type) then we need to take account of that.

        .. note::  As this is intended to simplify conversion to and from JSON,
                   datetimes are converted using .isoformat()

        :return:: A dictionary of {__table__:<tablename> .. (key,value)* pairs}
        """

        #Appending a table to the dictionary could help us be a little cleverer
        #when unpacking objects
        out = {"__table__": self.__tablename__}

        #Iterate through each column in our table
        for col in self.__table__.columns:
            try:
                if col.name == "type":
                    value = getattr(self,"typeId")
                else:
                    value = getattr(self, col.name)
            except AttributeError, e:
                log.warning(e)

            #Conversion code for datetime
            if isinstance(col.type, sqlalchemy.DateTime) and value:
                value = value.isoformat()
            #Append to the dictionary
            out[col.name] = value

        return out

    def fromJSON(self, jsonDict):
        """Update the object using a JSON string

        :var jsonDict:: Either a JSON string (from json.dumps) or dictionary
        containing key,value pairs (from asDict())
        """

        #Check if we have a string or dictonary
        if type(jsonDict) == str:
            jsonDict = json.loads(jsonDict)

        #For each column in the table
        for col in self.__table__.columns:
            #Check to see if the item exists in our dictionary
            newValue = jsonDict.get(col.name, None)

            #Fix missing values
            if newValue is None:
                pass
            else:
                #Convert if it is a datetime object
                if isinstance(col.type, sqlalchemy.DateTime) and newValue:
                    newValue = dateutil.parser.parse(newValue)

                #And set our variable

                #And Deal with the corner case above
                if col.name == "type":
                    setattr(self, "typeId", newValue)
                else:
                    setattr(self, col.name, newValue)



def calibrateReadings(theQuery):
    """Generator object to calibate all readings,
    hopefully this gathers all calibration based readings into one 
    area

    :param theQuery: SQLA query object containing Reading values"""

    #Dictionary to hold all sensor paramters
    session = meta.Session()
    sensorParams = {}

    for reading in theQuery:

        theSensor = sensorParams.get((reading.nodeId,reading.typeId),None)
        log.debug("Original Reading {0} Sensor is {1}".format(reading,theSensor))
        if not theSensor:
            theSensor = session.query(sensor.Sensor).filter_by(nodeId = reading.nodeId,sensorTypeId = reading.typeId).first()
            if theSensor is None:
                theSensor = sensor.Sensor(calibrationSlope = 1.0,calibrationOffset = 0.0)
            sensorParams[(reading.nodeId,reading.typeId)] = theSensor


        #Then add the offset etc
        cReading = Reading(time=reading.time,
                           nodeId = reading.nodeId,
                           typeId = reading.typeId,
                           locationId = reading.locationId,
                           value = theSensor.calibrationOffset + (theSensor.calibrationSlope * reading.value),
                           )
    
        yield cReading
                                  
def calibJSON(theQuery):
    """Generator object to calibate all readings,
    hopefully this gathers all calibration based readings into one 
    area

    :param theQuery: SQLA query object containing Reading values"""

    #Dictionary to hold all sensor paramters
    session = meta.Session()
    sensorParams = {}

    for reading in theQuery:

        theSensor = sensorParams.get((reading.nodeId,reading.typeId),None)
        #log.debug("Original Reading {0} Sensor is {1}".format(reading,theSensor))
        if not theSensor:
            #theSensor = "FOO"
            theSensor = session.query(sensor.Sensor).filter_by(nodeId = reading.nodeId,sensorTypeId = reading.typeId).first()
            if theSensor is None:
                theSensor = sensor.Sensor(calibrationSlope = 1.0,calibrationOffset = 0.0)
            sensorParams[(reading.nodeId,reading.typeId)] = theSensor


        #Then add the offset etc
        cReading = {"time":reading.time.isoformat(),
                    "nodeId" : reading.nodeId,
                    "typeId" : reading.typeId,
                    "locationId" : reading.locationId,
                    "value" : theSensor.calibrationOffset + (theSensor.calibrationSlope * reading.value),
                    }
    
        yield cReading
    

def calibratePairs(theQuery):
    """Generator object to calibrate readings and return in JSON 
    friendly format
    
    :param theQuery: SQLA query object containing readings
    """

    #Dictionary to hold all sensor paramters
    session = meta.Session()
    sensorParams = {}

    for reading in theQuery:

        theSensor = sensorParams.get((reading.nodeId,reading.typeId),None)
        log.debug("Original Reading {0} Sensor is {1}".format(reading,theSensor))
        if not theSensor:
            theSensor = session.query(sensor.Sensor).filter_by(nodeId = reading.nodeId,sensorTypeId = reading.typeId).first()
            if theSensor is None:
                theSensor = sensor.Sensor(calibrationSlope = 1.0,calibrationOffset = 0.0)
            sensorParams[(reading.nodeId,reading.typeId)] = theSensor

        theTime = time.mktime(reading.time.timetuple())*1000.0
        #theTime = reading.time.isoformat()
        theValue = theSensor.calibrationOffset + (theSensor.calibrationSlope * reading.value)
        #theValue = reading.value
    
    
        yield (theTime,theValue)
