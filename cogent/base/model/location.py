from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base

class Location(Base):
    __tablename__ = "Location"
    __table_args__ = (
        UniqueConstraint('houseId', 'roomId'),
        )
        
    id = Column(Integer, primary_key=True)
    houseId = Column(Integer,
                     ForeignKey('House.id'))
    house = relationship('House', backref=backref('location'))
    roomId = Column(Integer,
                    ForeignKey('Room.id'))
    room = relationship('Room', backref=backref('location'))
    
