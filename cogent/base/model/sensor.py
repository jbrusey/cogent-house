from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base

class Sensor(Base):
    __tablename__ = "Sensor"

    id = Column(Integer,primary_key=True)
    sensorTypeId = Column(Integer, ForeignKey('SensorType.id'))
    sensorType = relationship("SensorType", backref=("sensors"))
    nodeId = Column(Integer, ForeignKey('Node.id'))
    node = relationship("Node", backref=("sensors"))
    
    calibrationSlope = Column(Float)   
    calibrationOffset = Column(Float)   

