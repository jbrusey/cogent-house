"""
.. codeauthor::  Ross Wiklins 
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>
"""

import sqlalchemy

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


class Deployment(Base):
    """Table to hold information about deployments.

    I would assume that a deployment is a logical grouping if
    *deployments* (which are otherwise known as houses). Otherwise,
    this is largely superseeded by the :class:`cogentviewer.models.house.House` class
    
    For example:    
    Samson Close *(Deployment)*

    #. House 1 *(House)*
    #. House 2 *(House)*

    :var integer id: deployment id (pk)
    :var string name: deployment name
    :var string description: deployment description
    :var DateTime startDate: deployment start date
    :var DateTime  endDate: deployment end date 

    :var list meta:   *Backref:* all :class:`cogentviewer.models.deploymentmetadata.DeploymentMetadata` about this deployment
    :var list houses:    *Backref:* all :class:`cogentviewer.models.house.House` objects in this deployment

    .. warning::

        **meta** was originally known as **metadata** this has the potential to break old code
        

    """
    __tablename__ = "Deployment"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    description = Column(String(255))
    startDate = Column(DateTime)
    endDate = Column(DateTime)

    #I prefer to have the backrefs in the parent class
    #This makes thing relationship clearer, as we allready have FK's in child classes
    meta = relationship("DeploymentMetadata",order_by="DeploymentMetadata.id",backref="deployment")
    houses = relationship("House",order_by="House.id",backref="deployment")

    def update(self,**kwargs):
        for key,value in kwargs.iteritems():
            setattr(self,key,value)

    def asJSON(self):
        return {"id":"D_{0}".format(self.id),
                "name":self.name,
                "label":self.name,
                "type":"deployment",
                #"end":self.endDate,
                #"start":self.startDate,
                "children":None,
                "parent":"root",}

    def flatten(self):
        
        outDict = self.asJSON()
        if self.houses:
            outDict["children"] = [x.flatten() for x in self.houses]
        return outDict

    def __str__(self):
        return "Deployment: {0} {1} {2} - {3}".format(self.id,
                                                      self.name,
                                                      self.startDate,
                                                      self.endDate)


    def asList(self,parentId = ""):
        outDict = [self.asJSON()]
        if self.houses:
            #log.debug("Has House")
            outDict[0]["children"] = True
            for item in self.houses:
                outDict.extend(item.asList(self.id))
                
        #log.debug("Deployment Out Dict {0}".format(outDict))
        return outDict

