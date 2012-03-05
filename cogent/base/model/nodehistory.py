from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base

class NodeHistory(Base):
    __tablename__ = "NodeHistory"

    nodeId = Column(Integer, ForeignKey('Node.id'), primary_key=True)
    node = relationship("Node", backref="nodeHistory")
    startDate = Column(DateTime, primary_key=True)
    endDate = Column(DateTime)
    houseAddress = Column(String(255))
    roomType = Column(String(255))
    roomName = Column(String(255))
