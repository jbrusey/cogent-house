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

from sqlalchemy import Table, Column, Integer, ForeignKey,String,DateTime,Boolean,BigInteger
from sqlalchemy.orm import relationship, backref

import sqlalchemy.types as types
#from Bitset import Bitset


class NodeState(Base,meta.InnoDBMix):
    """
    It appears that this table holds the state of any nodes.
    
    I assume this will be used for the routing tree display,

    .. todo::
    
        Find out what these are for        
        1. parent
        1. localTime


    :var Integer id: Id of NodeState
    :var DateTime time: Timestamp of state 
    :var Integer nodeId: :class:`cogentviewer.models.node.Node` this state belongs to
    :var Integer parent: Parent node in the routing tree?
    :var BigInteger localtime: Local time of the node (in unix time??)
    """

    __tablename__ = "NodeState"


    id = Column(Integer, primary_key=True)
    time = Column(DateTime)
    nodeId = Column(Integer, ForeignKey('Node.id'))
    parent = Column(Integer)
    localtime = Column(BigInteger)

    def __repr__(self):
        return ("NodeState(" +
                str(self.id) + "," +
                str(self.time) + "," +
                str(self.nodeId) + "," +
                str(self.parent) + "," +
                str(self.localtime) + ")")


    def __cmp__(self,other):
        try:
            val = (self.time - other.time).seconds
            val += self.nodeId - other.nodeId
            val += self.parent - other.parent
            return val
        except TypeError,e:
            log.warning("Unable to Compate {0} {1}".format(self,other))
        