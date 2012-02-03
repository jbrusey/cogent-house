from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base

class Reading(Base):
    __tablename__ = "Reading"

    # TODO remove id
    id = Column(Integer, primary_key=True)
    # TODO time, typeId and nodeId should be primary key
    time = Column(DateTime)
    nodeId = Column(Integer, ForeignKey('Node.id'))
    node = relationship("Node", backref=backref('readings'))
    typeId = Column('type', Integer, ForeignKey('SensorType.id'))
    # TODO also include houseId and roomId columns
    typ = relationship("SensorType", backref=backref('readings'))
    value = Column(Float)    

    def __repr__(self):
        return "Reading(" + str(self.id) +"," + str(self.time) + "," + str(self.nodeId) + "," + str(self.typeId) + "," + str(self.value) + ")"
        
        
