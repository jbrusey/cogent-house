"""
Classes and Modules that represent sensor related objects

.. codeauthor::  Ross Wiklins 
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>
"""


import sqlalchemy
import logging
log = logging.getLogger(__name__)

import meta
Base = meta.Base

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

class SensorType(Base,meta.InnoDBMix):
    """ Represent Sensor Types

    .. note ::
    
        This table is a candiate for "insert on create" as sensor types should be static
        
    :var Integer id:
    :var String name:
    :var String code:
    :var String units:
    :var Float c0:
    :var Float c1:
    :var Float c2:
    :var Float c3:

    :var readings: *backref* to :class:`cogentviewer.models.reading.Reading`
    :var sensors: *backref* to :class:`cogentviewer.models.sensor.Sensor`
    """
    __tablename__ = "SensorType"

    id = Column(Integer,primary_key=True,autoincrement=False)
    name = Column(String(255))
    code = Column(String(50))
    units = Column(String(20))
    c0 = Column(Float)
    c1 = Column(Float)
    c2 = Column(Float)
    c3 = Column(Float)
    
    readings = relationship("Reading",backref="sensorType")
    sensors = relationship("Sensor",backref="sensorType")

    def asJSON(self):
        return {"id":self.id,
                "label":self.name,
                "name":self.name,
                "type":"sensorType",
                "code":self.code,
                "units":self.units}

    def __str__(self):
        return "{0}: {1} {2} {3}".format(self.id,self.name,self.code,self.units)
