from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, BigInteger, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base

class NodeState(Base):
    __tablename__ = "NodeState"

    id = Column(Integer, primary_key=True)
    time = Column(DateTime)
    nodeId = Column(Integer, ForeignKey('Node.id'))
    node = relationship("Node", backref=("stateHistory"))
    parent = Column(Integer)
    localtime = Column(BigInteger)

    def __repr__(self):
        return ("NodeState(" +
                str(self.id) + "," +
                str(self.time) + "," +
                str(self.nodeId) + "," +
                str(self.parent) + "," +
                str(self.localtime) + ")")

