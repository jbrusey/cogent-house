from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base

class Weather(Base):
    __tablename__ = "Weather"

    time = Column(DateTime,primary_key=True)
    outTemp = Column(Float) 
    outHum = Column(Float)     
    dew = Column(Float)   

    gust = Column(Float)
    wSpeed = Column(Float) 
    wDir = Column(Float)
    wChill = Column(Float)
    
    apparentTemp = Column(Float)   
    
    rain = Column(Float)   
    pressure = Column(Float)   
    tempIn = Column(Float)   
    humIn = Column(Float)   
