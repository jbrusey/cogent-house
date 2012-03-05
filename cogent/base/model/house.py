from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base

class House(Base):
    __tablename__ = "House"

    id = Column(Integer, primary_key=True)
    deploymentId = Column(Integer, ForeignKey('Deployment.id'))
    deployment = relationship("Deployment", backref=("houses"))
    address = Column(String(255))
    startDate = Column(DateTime)
    endDate = Column(DateTime)
