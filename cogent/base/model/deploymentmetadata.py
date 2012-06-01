"""
.. codeauthor::  Ross Wiklins 
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>
"""


#SQL Alchemy Relevant information
from sqlalchemy import Table,Column,Integer,String,DateTime,ForeignKey,Float

#And Backrefs and Relations.
from sqlalchemy.orm import relationship,backref

#Setup Logging
import logging
log = logging.getLogger(__name__)

#Import Pyramid Meta Data
import meta
Base = meta.Base


class DeploymentMetadata(Base, meta.InnoDBMix):
    """
    Table to hold metadata about a deployment

    :var integer id:
    :var integer deploymentId: *Foreign key* to :class:`cogentviewer.models.deployment.Deployment` this metadata belongs to
    :var string name:  Name of metadata
    :var string description: Description of metadata
    :var string units: Units of metadata
    :var float value: Value of metadata
    """
    __tablename__ = "DeploymentMetadata"

    id = Column(Integer, primary_key=True)
    deploymentId = Column(Integer, ForeignKey('Deployment.id'))
    name = Column(String(255))
    description = Column(String(255))
    units = Column(String(255))
    value = Column(Float)

    #I prefer to have the backrefs in the parent class
    #deployment = relationship("Deployment", backref=("metadata"),order_by=id)

    def update(self,**kwargs):
        for key,value in kwargs.iteritems():
            setattr(self,key,value)

    def __str__(self):
        return "Meta {0}: {1}".format(self.id,self.deploymentId)
