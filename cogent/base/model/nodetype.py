from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref
import sqlalchemy.types as types

from cogent.base.model.meta import Base

from Bitset import Bitset

class BitsetType(types.TypeDecorator):
    impl = types.String
    
    def process_bind_param(self, value, dialect):
        return str(value)

    def process_result_value(self, value, dialect):
        return Bitset.fromstring(value)

class NodeType(Base):
    __tablename__ = "NodeType"

    id = Column(Integer, primary_key = True, autoincrement = False)
    name = Column(String(20))
    time = Column(DateTime)
    seq = Column(Integer)
    updated_seq = Column(Integer)
    period = Column(Integer)
    blink = Column(Boolean)
    configured = Column(BitsetType(10))

    def __repr__(self):
        return ("NodeType(" +
                str(self.node_type) + "," +
                str(self.node_type_name) + "," + 
                str(self.time) + "," +
                str(self.seq) + "," +
                str(self.period) + "," +
                str(self.blink) + "," +
                repr(self.configured) + ")")

