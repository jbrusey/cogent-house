from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base

class Reading(Base):
    __tablename__ = "Reading"

    time = Column(DateTime,
                  primary_key=True,
                  nullable=False,
                  autoincrement=False)
    nodeId = Column(Integer,
                    ForeignKey('Node.id'),
                    primary_key=True,
                    nullable=False,
                    autoincrement=False)
    node = relationship("Node", backref=backref('readings'))
    typeId = Column('type',
                    Integer,
                    ForeignKey('SensorType.id'),
                    primary_key=True,
                    nullable=False,
                    autoincrement=False)
    locationId = Column(Integer,
                        ForeignKey('Location.id'))
    location = relationship('Location', backref=backref('readings'))
    
    typ = relationship("SensorType", backref=backref('readings'))
    value = Column(Float)    

    def __repr__(self):
        return ("Reading(" + 
                ",".join([repr(x) for x in [self.time,
                                            self.nodeId,
                                            self.typeId,
                                            self.locationId,
                                            self.value]
                    ]) + ")")
        
        
