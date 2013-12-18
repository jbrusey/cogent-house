"""
.. codeauthor::  Ross Wiklins 
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>

"""

import logging
LOG = logging.getLogger(__name__)

import meta


from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref

#import sqlalchemy.types as types

import location

class Node(meta.Base, meta.InnoDBMix):
    """
    Class to hold detals of the nodes themselves

    :var Integer id: Node Id
    :var Integer locationId: `Location` this node is in
    :var Integer nodeTypeId: `NodeType` this node is.

    :var stateHistory: *Backref* to `nodestate.NodeState`
    :var nodeHistory: *Backref* to `nodehistory.NodeHistory`
    :var readings: *Backref* to `reading.Reading`
    :var sensors: *Backref* to `sensor.Sensor`
    """

    __tablename__ = "Node"

    id = Column(Integer, primary_key=True, autoincrement=False)
    locationId = Column(Integer,
                        ForeignKey('Location.id'),
                        nullable=True)
    nodeTypeId = Column(Integer, ForeignKey('NodeType.id'),
                        nullable=True)

    stateHistory = relationship("NodeState",
                                order_by="NodeState.id",
                                backref="node")
    nodeHistory = relationship("NodeHistory",
                               backref="node")
    readings = relationship("Reading",
                            backref="node")
    sensors = relationship("Sensor",
                           backref=("node"))

    #Add a backref to association Table

    # locations = relationship("Location",
    #                          secondary="NodeLocation",
    #                          backref="node")


    def __eq__(self, other):
        """Nodes should be equal in Id (and type but it may not exist) Only"""
        return self.id == other.id

    def __ne__(self, other):
        """Ids differ"""
        return not(self.id == other.id)

    def __lt__(self, other):
        return self.id < other.id

    def update(self, **kwargs):
        for key,value in kwargs.iteritems():
            setattr(self,key,value)

    def __str__(self):
        return "Node {0} Loc {1}".format(self.id,self.locationId)

