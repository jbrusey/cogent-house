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
        #return "Reading(" + str(self.time) + "," + str(self.nodeId) + "," + str(self.typeId) + "," + str(self.value) + ")"
        return "Reading {0}, {1}, {2}, {3} = {4}".format(self.time,
                                                         self.nodeId,
                                                         self.typeId,
                                                         self.locationId,
                                                         self.value)
        
        
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
