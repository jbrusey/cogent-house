"""
Classes and Modules that represent sensor related objects

.. codeauthor::  Ross Wiklins
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>
"""

import meta


from sqlalchemy import Column, Integer, ForeignKey, Float


class Sensor(meta.Base, meta.InnoDBMix):
    """ Class to deal with Sensor Objects

    :var Integer id: Id of Sensor
    :var Integer sensorTypeId: *fk* to
        :class:`cogentviewer.models.sensortype.SensorType`
    :var Integer nodeId: *fk* to :class:`cogentviewer.models.node.Node`
    :var Float calibrationSlope: Calibration slope of this Sensor
    :var Float calibrationOffset: Calibration offset of this Sensor
    """
    __tablename__ = "Sensor"

    id = Column(Integer, primary_key=True)
    sensorTypeId = Column(Integer, ForeignKey('SensorType.id'))
    nodeId = Column(Integer, ForeignKey('Node.id'))
    calibrationSlope = Column(Float)
    calibrationOffset = Column(Float)


    def __str__(self):
        return "Sensor({0} type {1} m {2} c {3})".format(self.id,
                                                         self.sensorTypeId,
                                                         self.calibrationSlope,
                                                         self.calibrationOffset)
