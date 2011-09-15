from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base

class RoomType(Base):
    """ e.g. bedroom or kitchen"""
    __tablename__ = "RoomType"

    id = Column(Integer,primary_key=True)
    name = Column(String(20))
