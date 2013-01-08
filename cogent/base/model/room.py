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

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

   
#Association object linking rooms and nodes. gives a many to many.
#It also means we can work out what Nodes were in What Rooms at a given time

class Room(Base,meta.InnoDBMix):
    """
    A room in a :class:`cogentviewer.models.house.House`
    
    :var Integer id: Id
    :var Integer roomTypeId: The :class:`cogentviewer.models.roomtype.RoomType` of the room
    :var String name: Name of the Room
    :var location: *backref* The :class:`cogentviewer.models.location.Location` of the room
    """

    __tablename__ = "Room"

    id = Column(Integer, primary_key=True)
    roomTypeId = Column(Integer, ForeignKey('RoomType.id'), nullable=True)
    name = Column(String(20))

    location = relationship("Location",backref="room")


    def asJSON(self,parentId=""):
        theItem = {"id":"R_{0}".format(self.id),
                   "label": "{0} ({1})".format(self.name,self.roomType.name),
                   "name": "{0} ({1})".format(self.name,self.roomType.name),
                   "type":"room",
                   "parent": "H_{0}".format(parentId),
                   "children":False
                   }
        return theItem

    def flatten(self):
        jsonDict =  self.asJSON()
        if self.nodes:
            children = [x.flatten() for x in self.nodes]
            jsonDict["children"] = children

        return jsonDict
        
    def asList(self,parentId=""):
        """Turn this object into a list, so the tree functions can display it"""
        log.debug("--> Room As List Called")
        outDict = [self.asJSON(parentId)]
        log.debug("Room Nodes {0}".format(self.nodes))
        if self.nodes:
            outDict[0]["children"] = True
            for item in self.nodes:
                outDict.extend(item.asList(self.id))

        return outDict


    def __str__(self):
        return "Room ({0}) {1}".format(self.id,self.name)

    def __cmp__(self,other):
        #return -1
        typeOff = 0
        if self.name == other.name:
            if self.roomTypeId:
                typeOff =  self.roomTypeId - other.roomTypeId
            return self.id - other.id - typeOff
        
        else:
            return -1
