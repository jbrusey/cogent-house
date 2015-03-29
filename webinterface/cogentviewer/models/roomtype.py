"""
.. codeauthor::  Ross Wiklins
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from functools import total_ordering
import meta

@total_ordering
class RoomType(meta.Base, meta.InnoDBMix):
    """The Type of Room  e.g. bedroom or kitchen

    :var Integer id: Id
    :var String name: Name of the Room
    :var rooms (FK): What Rooms objects are of this type
    """

    __tablename__ = "RoomType"

    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    rooms = relationship("Room", order_by="Room.id", backref="roomType")

    def __str__(self):
        return "RoomType {0} : {1}".format(self.id, self.name)

    def __eq__(self, other):
        """Equality,  again avoid the Id"""
        return self.name == other.name

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return self.name < other.name

    def queryparams(self, body = None):
        """Return a set of query parameters to find this specific item via the rest
        service

        :param body: The Request body or None
        :return: query compatable dictionary
        """
        if body:
            return {"name": body["name"]}
        
        return {"name" : self.name}
