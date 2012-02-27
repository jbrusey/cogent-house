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

from sqlalchemy import Table, Column, Integer, ForeignKey,String,DateTime,Boolean
from sqlalchemy.orm import relationship, backref

import sqlalchemy.types as types
from Bitset import Bitset


class Node(Base): 
    """
    Class to hold detals of the nodes themselves

    :var Integer id: Node Id
    :var Integer locationId: :class:`cogentviewer.models.location.Location` this node is in
    :var Integer nodeTypeId: :class:`cogentviewer.models.nodetype.NodeType` this node is.

    :var stateHistory: *Backref* to :class:`cogentviewer.models.nodestate.NodeState`
    :var nodeHistory: *Backref* to :class:`cogentviewer.models.nodehistory.NodeHistory`
    :var readings: *Backref* to :class:`cogentviewer.models.reading.Reading`
    :var sensors: *Backref* to :class:`cogentviewer.models.sensor.Sensor`
    """
 
    __tablename__ = "Node"

    id = Column(Integer, primary_key=True)
    locationId = Column(Integer,
                        ForeignKey('Location.id'))     
    nodeTypeId = Column(Integer, ForeignKey('NodeType.id'))  
  
    stateHistory = relationship("NodeState", order_by="NodeState.id",backref="node")
    nodeHistory = relationship("NodeHistory",backref="node")
    readings = relationship("Reading",backref="node")
    sensors = relationship("Sensor", backref=("node"))
   
    def update(self,**kwargs):
        for key,value in kwargs.iteritems():
            setattr(self,key,value)


    def asJSON(self,parentId=""):

        theDict = {"id": "N_{0}".format(self.id),
                   "label": "Node {0}".format(self.id),
                   "name": "Node {0}".format(self.id),
                   "type":"node",
                   "parent":"R_{0}".format(parentId),
                   "children":False,
                   }

        return theDict


    def flatten(self):
        outDict = self.asJSON()

        children = [x.flatten() for x in self.sensors]
        outDict["children"] = children
        return outDict


    def asList(self,parentId=""):
        outDict = [self.asJSON(parentId)]
        if self.sensors:
            outDict[0]["children"] = True
            for item in self.sensors:
                outDict.extend(item.asList(self.id))

        return outDict



    def getSamples(self,limit=None):
        """
        Testing Function,
        Can we fetch samples from this Node with some stripping out of data.
        """
        theseReadings = self.readings
        if limit:
            theseReadings = theseReadings[:limit]
        return [x.asJSON() for x in theseReadings]

    
    
