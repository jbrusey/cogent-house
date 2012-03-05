from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base

class DeploymentMetadata(Base):
    __tablename__ = "DeploymentMetadata"

    id = Column(Integer, primary_key=True)
    deploymentId = Column(Integer, ForeignKey('Deployment.id'))
    deployment = relationship("Deployment", backref=("metadata"))
    name = Column(String(255))
    description = Column(String(255))
    units = Column(String(255))
    value = Column(Float)
