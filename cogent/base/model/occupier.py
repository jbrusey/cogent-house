from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base

class Occupier(Base):
    __tablename__ = "Occupier"

    id = Column(Integer, primary_key=True)
    houseId = Column(Integer, ForeignKey('House.id'))
    house = relationship("House", backref=("occupiers"))
    name = Column(String(255))
    contactNumber = Column(String(20))
    startDate = Column(DateTime)
    endDate = Column(DateTime)
