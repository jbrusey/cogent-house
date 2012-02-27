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

from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime,Float
from sqlalchemy.orm import relationship, backref

import datetime


class Location(Base):
    """
    Location provides a link between houses and rooms.
    This is needed if the node is moved, for example during multiple deployments.
    
    This table should be an "associatve array" transparrently linking houses and rooms


    :var Integer id: Id of Location
    :var Integer houseId: Link to :class:`cogentviewer.models.house.House` the room is in
    :var Integer roomId: Link to :class:`cogentviewer.models.room.Room` this location corresponds to
    """

    __tablename__ = "Location"
    __table_args__ = (
        sqlalchemy.UniqueConstraint('houseId', 'roomId'),
        )
        
    id = Column(Integer, primary_key=True)
    houseId = Column(Integer,
                     ForeignKey('House.id'))
    roomId = Column(Integer,
                    ForeignKey('Room.id'))

    nodes = relationship("Node",backref=backref('location'))

    def __str__(self):
        return ("Loc ({0}): House {1} , Room {2}".format(self.id,self.houseId,self.roomId))
