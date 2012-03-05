from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base

class SensorType(Base):
    __tablename__ = "SensorType"

    id = Column(Integer,primary_key=True,autoincrement=False)
    name = Column(String(255))
    code = Column(String(50))
    units = Column(String(20))
    c0 = Column(Float)
    c1 = Column(Float)
    c2 = Column(Float)
    c3 = Column(Float)

