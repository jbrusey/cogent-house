from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base

class LastReport(Base):
    __tablename__ = "LastReport"

    name = Column(String(40), primary_key=True)
    value = Column(String(4096))
