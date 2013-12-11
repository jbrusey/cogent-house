"""
Classes and Modules that represent sensor related objects

.. codeauthor::  Ross Wiklins
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>
"""

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

import meta

class SensorType(meta.Base, meta.InnoDBMix):
    """ Represent Sensor Types

    .. note ::
        This table is a candiate for "insert on create" as sensor types
        should be static

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

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(255))
    code = Column(String(50))
    units = Column(String(20))
    c0 = Column(Float)
    c1 = Column(Float)
    c2 = Column(Float)
    c3 = Column(Float)

    readings = relationship("Reading", backref="sensorType")
    sensors = relationship("Sensor", backref="sensorType")


    def __str__(self):
        return "{0}: {1} {2} {3}".format(self.id,
                                         self.name,
                                         self.code,
                                         self.units)

    def __eq__(self, other):
        """Test for equality"""
        return self.id == other.id and \
            self.name == other.name and \
            self.code == other.code and \
            self.units == other.units

    def __ne__(self, other):
        return not(self.id == other.id and \
                       self.name == other.name and \
                       self.code == other.code and \
                       self.units == other.units)

    def __lt__(self, other):
        if self.id == other.id:
            return self.name < other.name
        return self.id < other.id
