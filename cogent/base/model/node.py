from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base


class Node(Base):
    __tablename__ = "Node"

    id = Column(Integer, primary_key=True)
    locationId = Column(Integer,
                        ForeignKey('Location.id'))
    location = relationship('Location', backref=backref('nodes'))
    
    nodeTypeId = Column(Integer, ForeignKey('NodeType.id'))
    nodeType = relationship("NodeType", backref=backref("node"))
    
