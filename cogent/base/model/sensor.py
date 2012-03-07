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

class Sensor(Base,meta.InnoDBMix):
    """ Class to deal with Sensor Objects

    :var Integer id: Id of Sensor
    :var Integer sensorTypeId: *fk* to :class:`cogentviewer.models.sensortype.SensorType`
    :var Integer nodeId: *fk* to :class:`cogentviewer.models.node.Node`
    :var Float calibrationSlope: Calibration slope of this Sensor
    :var Float calibrationOffset: Calibration offset of this Sensor
    """
    __tablename__ = "Sensor"

    id = Column(Integer,primary_key=True)
    sensorTypeId = Column(Integer, ForeignKey('SensorType.id'))
    nodeId = Column(Integer, ForeignKey('Node.id'))
    calibrationSlope = Column(Float)   
    calibrationOffset = Column(Float)   


    def asJSON(self,parentId):
        theDict = {"id": "S_{0}".format(self.id),
                   "label": "Sensor {0} ({1})".format(self.id,self.sensorType.name),
                   "name":  "Sensor {0} ({1})".format(self.id,self.sensorType.name),
                   "type":"sensor",
                   "location": self.node.locationId,
                   "parent":"N_{0}".format(parentId),
                   "children":False,
                   }

        return theDict

        # return {"id":self.id,
        #         "type":"sensor",
        #         "sensorTypeId":self.sensorTypeId,
	# 	"nodeId":self.nodeId,
        #         }

    def update(self,**kwargs):
        for key,value in kwargs.iteritems():
            setattr(self,key,value)

    def flatten(self):
        outDict = self.asJSON()
    
        #children = [x.flatten() for x in self.nodes]
        #children = []
        #outDict["children"] = children
        return outDict


    def asList(self,parentId=""):
        outDict = [self.asJSON(parentId)]
        outDict[0]["children"] = False
        return outDict


    def __str__(self):
        return "Sensor ({0} type {1} m {2} c {3})".format(self.id,self.sensorTypeId,self.calibrationSlope,self.calibrationOffset)


    def flatNav(self):
        """Flatten the object into a JSON hashable array,
        
        This is intended to be used to generate the site navigation
        
        :return:  the object in the form {"name","id","chldren":[]}
        """
        
        outDict = {"name":self.id,
                   "id":self.id}

        return outDict
                   
