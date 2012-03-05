from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base

class HouseMetadata(Base):
    __tablename__ = "HouseMetadata"

    id = Column(Integer, primary_key=True)
    houseId = Column(Integer, ForeignKey('House.id'))
    house = relationship("House", backref=("metas"))
    name = Column(String(255))
    description = Column(String(255))
    units = Column(String(20))
    value = Column(Float)
