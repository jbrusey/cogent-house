"""
.. codeauthor::  Ross Wiklins
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

import meta

class Room(meta.Base, meta.InnoDBMix):
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

    def __str__(self):
        return "Room ({0}) {1} (Type={2})".format(self.id,
                                                  self.name,
                                                  self.roomTypeId)


    def __eq__(self, other):
        return self.name == other.name and self.roomTypeId == other.roomTypeId

    def __ne__(self, other):
        return not(self.name == other.name and
                   self.roomTypeId == other.roomTypeId)

    def __lt__(self, other):
        if self.name == other.name:
            return self.roomTypeId < other.roomTypeId
        return self.name < other.name
