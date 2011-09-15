from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base

class Deployment(Base):
    __tablename__ = "Deployment"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    description = Column(String(255))
    startDate = Column(DateTime)
    endDate = Column(DateTime)
