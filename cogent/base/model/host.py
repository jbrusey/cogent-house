from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base

class Host(Base):
    __tablename__ = "Host"

    id = Column(Integer, primary_key=True)
    hostname = Column(String(255))
    lastupdate = Column(DateTime)
        
