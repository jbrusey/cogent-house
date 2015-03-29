"""
.. codeauthor::  Ross Wiklins
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>
"""

import sqlalchemy
from functools import total_ordering

from cogentviewer.models import meta


from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship #, backref

@total_ordering
class Location(meta.Base, meta.InnoDBMix):
    """
    Location provides a link between houses and rooms.  This is needed if the
    node is moved, for example during multiple deployments.

    :var Integer id: Id of Location
    :var Integer houseId: Link to `House` the room is in
    :var Integer roomId: Link to `Room` this location corresponds to
    """

    __tablename__ = "Location"
    __table_args__ = (
        sqlalchemy.UniqueConstraint('houseId', 'roomId'),
        {'mysql_engine': 'InnoDB',
         'mysql_charset':'utf8'},
        )

    id = Column(Integer, primary_key=True)
    houseId = Column(Integer,
                     ForeignKey('House.id'))
    roomId = Column(Integer,
                    ForeignKey('Room.id'))

    nodes = relationship("Node", backref='location')
    readings = relationship("Reading", backref='location')

    #A Lazy loaded version that allows us to generte a query object based
    #On the readings.
    filtReadings = relationship("Reading", lazy='dynamic')

    allnodes = relationship("Node",
                            secondary="NodeLocation",
                            backref="all_locs")

    def __str__(self):
        return "Location {0}: {1} {2}".format(self.id,
                                               self.houseId,
                                               self.roomId)

    def __eq__(self, other):
        return ((self.houseId, self.roomId) ==
                (other.houseId, other.roomId))

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return ((self.houseId, self.roomId) <
                (other.houseId, other.roomId))


NodeLocation = sqlalchemy.Table("NodeLocation", meta.Base.metadata,
                                sqlalchemy.Column("LocationId",
                                                  Integer,
                                                  ForeignKey("Location.id")),
                                sqlalchemy.Column("nodeId",
                                                  Integer,
                                                  ForeignKey("Node.id"))
                                )
