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

class BitsetType(types.TypeDecorator):
    impl = types.String
    
    def process_bind_param(self, value, dialect):
        return str(value)

    def process_result_value(self, value, dialect):
        return Bitset.fromstring(value)

class NodeType(Base,meta.InnoDBMix):
    """Type of Node
    
    These values should remain relitively static as we only have a given number of nodetypes

    :var Integer id: Id
    :var String name: Name of type
    :var DateTime time: 
    :var Integer seq:
    :var Integer updated_seq: 
    :var Integer period:
    :var Boolean blink:
    :var configured: :class:`cogentviewer.models.node.BitsetType`
    :var nodes: *backref* to :class:`cogentviewer.models.node.Node`
   

    """
    __tablename__ = "NodeType"

    id = Column(Integer, primary_key = True, autoincrement = False)
    name = Column(String(20))
    time = Column(DateTime)
    seq = Column(Integer)
    updated_seq = Column(Integer)
    period = Column(Integer)
    blink = Column(Boolean)
    configured = Column(BitsetType(10))

    nodes = relationship("Node",order_by="Node.id",backref="nodeType")

    def __repr__(self):
        return ("NodeType(" +
                ",".join([repr(x) for x in [self.id,
                                            self.name,
                                            self.time,
                                            self.seq,
                                            self.updated_seq,
                                            self.period,
                                            self.blink,
                                            self.configured]]) + ")")


    def __cmp__(self,other):
        if self.id - other.id == 0:
            return cmp(self.name, other.name)
        else:
            return self.id - other.id
        #return False
        #print "COMPARE {0} ({1}) to {2} ({3}) == {4}".format(self.id,type(self.id),
        #                                                     other.id,type(other.id),
        #                                                     self.id == other.id)
        #return self.id - other.id
