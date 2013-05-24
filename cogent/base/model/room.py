"""
.. codeauthor::  Ross Wiklins
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

import meta
BASE = meta.Base


class Room(BASE, meta.InnoDBMix):
    """
    A room in a :class:`cogentviewer.models.house.House`

    :var Integer id: Id
    :var Integer roomTypeId: The `RoomType` of the room
    :var String name: Name of the Room
    :var location: *backref* The `Location` of the room
    """

    __tablename__ = "Room"

    id = Column(Integer, primary_key=True)
    roomTypeId = Column(Integer, ForeignKey('RoomType.id'), nullable=True)
    name = Column(String(20))

    location = relationship("Location", backref="room")


    def asJSON(self, parentId=""):
        theItem = {"id":"R_{0}".format(self.id),
                   "label": "{0} ({1})".format(self.name, self.roomType.name),
                   "name": "{0} ({1})".format(self.name, self.roomType.name),
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

    # def asList(self,parentId=""):
  #     """Turn this object into a list, so the tree functions can display it"""
    #     log.debug("--> Room As List Called")
    #     outDict = [self.asJSON(parentId)]
    #     if self.nodes:
    #         outDict[0]["children"] = True
    #         for item in self.nodes:
    #             outDict.extend(item.asList(self.id))

    #     return outDict


    def __str__(self):
        return "Room ({0}) {1} {2}".format(self.id, self.name,self.roomTypeId)


    def __eq__(self, other):
        return self.name == other.name and self.roomTypeId == other.roomTypeId

    def __ne__(self, other):
        return not(self.name == other.name and
                   self.roomTypeId == other.roomTypeId)

    def __lt__(self, other):
        if self.name == other.name:
            return self.roomTypeId < other.roomTypeId
        return self.name < other.name
