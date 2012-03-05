from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base

class RawMessage(Base):
    __tablename__ = "RawMessage"

    id = Column(Integer,primary_key=True,autoincrement=False)
    time = Column(DateTime)
    pickedObject = Column(String(400))
    
