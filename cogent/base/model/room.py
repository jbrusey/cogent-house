from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base
    
class Room(Base):
    """ e.g. bedroom 1, bedroom 2 """
    __tablename__ = "Room"

    id = Column(Integer, primary_key=True)
    roomTypeId = Column(Integer, ForeignKey('RoomType.id'))
    roomType = relationship("RoomType", backref=("rooms"))
    name = Column(String(20))
