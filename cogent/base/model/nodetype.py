"""
.. codeauthor::  Ross Wiklins
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>

"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
import sqlalchemy.types as types

import meta
from Bitset import Bitset

class BitsetType(types.TypeDecorator):
    impl = types.String

    def process_bind_param(self, value, dialect):
        return str(value)

    def process_result_value(self, value, dialect):
        return Bitset.fromstring(value)

class NodeType(meta.Base, meta.InnoDBMix):
    """Type of Node

    These values should remain relitively static as we only have
    a given number of nodetypes

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

    nodes = relationship("Node", order_by="Node.id", backref="nodeType")

    def __repr__(self):
        return ("NodeType(" +
                ",".join([repr(x) for x in [self.id,
                                            self.name,
                                            self.time,
                                            self.seq,
                                            self.updated_seq,
                                            self.period,
                                            self.blink,
                                            self.configured,
                                            ]]) + ")")


    def dict(self):
        thedict =  {"__table__":"nodetype",
                    "id":self.id,
                    "name":self.name,
                    "time":None,
                    "seq":self.seq,
                    "updated_seq":self.updated_seq,
                    "period":self.period,
                    "blink":self.blink,
                    "configured": str(self.configured),
                    }
        if self.time:
            thedict["time"] = self.time.isoformat()

        return thedict
                
                
    def __cmp__(self,other):
        if self.id == other.id:
            return cmp(self.name, other.name)
        else:
            return self.id - other.id
        
