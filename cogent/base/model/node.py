from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base

class Node(Base):
    __tablename__ = "Node"

    id = Column(Integer, primary_key=True)
    # TODO change to location
    houseId = Column(Integer, ForeignKey('House.id'))
    house = relationship("House", backref=("node"))
    roomId = Column(Integer, ForeignKey('Room.id'))
    room = relationship("Room", backref=("node"))
    
    nodeTypeId = Column(Integer, ForeignKey('NodeType.id'))
    nodeType = relationship("NodeType", backref=("node"))
    
