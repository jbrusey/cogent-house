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


class RoomType(Base,meta.InnoDBMix):
    """The Type of Room  e.g. bedroom or kitchen

    :var Integer id: Id
    :var String name: Name of the Room
    :var rooms: What :class:`cogentviewer.models.room.Room` objects are of this type
    
    """
    __tablename__ = "RoomType"


    id = Column(Integer,primary_key=True)
    name = Column(String(20))
    rooms = relationship("Room",order_by="Room.id",backref="roomType")

    def __cmp__(self,other):
        """Check if two room type items are equal"""
        if self.name == other.name:
            return self.id - other.id
        else:
            return False


    def __str__(self):
        return "RoomType {0} : {1}".format(self.id,self.name)

