"""
.. codeauthor::  Ross Wiklins
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>
"""

import logging
import time

import dateutil

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float
#from sqlalchemy.orm import relationship, backref

import meta
import sensor

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class Reading(meta.Base, meta.InnoDBMix):
    """Table to hold detils of readings,

    Reading has a composite primary key consisiting of time,nodeId,typeId

    :var DateTime time: Time reading was taken
    :var Integer nodeId: Id of `Node` that took this sample
    :var Integer typeId: Id of `SensorType` that this reading came from
    :var Integer locationId: Id of `Location` that this reading came from

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

    def __eq__(self, other):
        #Ignore the location Id as it may be mapped.  (Node + Time + Type)
        #Should be enugh
        return (self.time == other.time and
                self.nodeId == other.nodeId and
                self.typeId == other.typeId and
                self.value == other.value)

    def __ne__(self, other):
        return not (self.time == other.time and
                    self.nodeId == other.nodeId and
                    self.typeId == other.typeId and
                    self.value == other.value)

    def __lt__(self, other):
        """Order by time,node, type, value"""
        if self.time == other.time:
            if self.nodeId == other.nodeId:
                if self.typeId == other.typeId:
                    return self.value < other.value
                return self.typeId < other.typeId
            return self.nodeId < other.nodeId
        return self.time < other.time


    def __str__(self):
        return "Rdg t:{0}\tn:{1}\tt:{2}\tl:{3} = {4}".format(self.time,
                                                             self.nodeId,
                                                             self.typeId,
                                                             self.locationId,
                                                             self.value)

    def __repr__(self):
        return "Reading({0},{1},{2},{3},{4}".format(self.time,
                                                    self.nodeId,
                                                    self.typeId,
                                                    self.locationId,
                                                    self.value)


    def asJSON(self, slope=1, offset=0):
        """Return this reading as a JSON relevant tuple

        This should format the sample so it is parseable by JSON / Javascript
        That will allow it to be graphed using either DOJO or Highcharts

        The format is (time,value) where time is Unixtime in miliseconds

        .. warning::

            The original timestamp is multipled by 1000, to shift from
            seconds to miliseconds.
            As per the JSON / Javascript Standard.

        """
        return (time.mktime(self.time.timetuple()) * 1000,
                (self.value*slope)+offset)

    def getRawValues(self):
        """
        Return the Reading as a Tuple of (time,value)

        Unlike other methods this does no data processing, returning the Raw
        (rather than calibrated) sensor reading.

        :return DateTime time: Time that this reading was taken
        :return Float value: Value of the reading at this Time

        """

        return (self.time, self.value)

    def getCalibValues(self):
        """
        Return the Reading as a tuple of (time,calibratedValue)

        This returns the same as GetRawValues but will calibrate the data
        against stored values

        .. warning:

            This will issue an SQL statement for each reading we call the
            function on, Therefore it is only useful as a shortcut when dealing
            with a limited amount of readings

        :return DateTime time: Time that this reading was taken

        :return Float value: Value of the reading at this Time Calibrated
        against the sensor values
        """
        #pass
        #Find the Sensor
        session = meta.Session()
        theSensor = session.query(sensor.Sensor).filter_by(sensorTypeId = self.typeId,
                                                           nodeId = self.nodeId).first()

        if theSensor is None:
            return self.time, self.value

        #Otherwise Calibrate
        value = (self.value * theSensor.calibrationSlope) + theSensor.calibrationOffset
        return (self.time, value)

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
                LOG.warning(e)

            #Conversion code for datetime
            if isinstance(col.type, DateTime) and value:
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
                if isinstance(col.type, DateTime) and newValue:
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
        LOG.debug("Orig Reading {0} Sensor is {1}".format(reading,theSensor))
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
        #LOG.debug("Original Reading {0} Sensor is {1}".format(reading,theSensor))
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


def calibPandas(theQuery):
    """Generator object to calibate all readings,
    hopefully this gathers all calibration based readings into one 
    area

    :param theQuery: SQLA query object containing Reading values"""

    #Dictionary to hold all sensor paramters
    session = meta.Session()
    sensorParams = {}

    for reading in theQuery:

        theSensor = sensorParams.get((reading.nodeId,reading.typeId),None)
        #LOG.debug("Original Reading {0} Sensor is {1}".format(reading,theSensor))
        if not theSensor:
            #theSensor = "FOO"
            theSensor = session.query(sensor.Sensor).filter_by(nodeId = reading.nodeId,sensorTypeId = reading.typeId).first()
            if theSensor is None:
                theSensor = sensor.Sensor(calibrationSlope = 1.0,calibrationOffset = 0.0)
            sensorParams[(reading.nodeId,reading.typeId)] = theSensor


        #Then add the offset etc
        cReading = {"time":reading.time,
                    "nodeId" : reading.nodeId,
                    "typeId" : reading.typeId,
                    "locationId" : reading.locationId,
                    "locationStr": reading.location.room.name,
                    "value" : theSensor.calibrationOffset + (theSensor.calibrationSlope * reading.value),
                    "location" : "Node {0}: {1} {2}".format(reading.nodeId,reading.location.room.name,reading.sensorType.name),
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
        LOG.debug("Original Reading {0} Sensor is {1}".format(reading,
                                                              theSensor))
        if not theSensor:
            theSensor = session.query(sensor.Sensor).filter_by(nodeId = reading.nodeId,
                                                               sensorTypeId = reading.typeId).first()
            if theSensor is None:
                theSensor = sensor.Sensor(calibrationSlope = 1.0,
                                          calibrationOffset = 0.0)
            sensorParams[(reading.nodeId,reading.typeId)] = theSensor

        theTime = time.mktime(reading.time.timetuple())*1000.0
        #theTime = reading.time.isoformat()
        theValue = theSensor.calibrationOffset + (theSensor.calibrationSlope * reading.value)
        #theValue = reading.value

        yield (theTime,theValue)
