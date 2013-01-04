"""
Classes and Modules that represent house related objects

.. codeauthor::  Ross Wiklins 
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>
"""

import sqlalchemy
import logging
log = logging.getLogger(__name__)

import meta
Base = meta.Base

from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime,Float
from sqlalchemy.orm import relationship, backref

class House(Base, meta.InnoDBMix):
    """
    Class to represent Houses

    :var Integer id: Id of House

    :var Integer deploymentId: Id of parent
        :class:`cogentviewer.models.depoyment.Deployment`

    :var String address: Address of property
    :var DateTime startDate: start of deployment in this House
    :var endDate endDate: end of depoyment in this House

    :var meta: *backref*
        :class:`cogentviewer.models.housemetadata.HouseMetadata` objects
        belonging to this House

    :var occupiers: *backref*
        :class:`cogentviewer.models.occupier.Occupier` objects belonging
        to this house

    """
    __tablename__ = "House"

    id = Column(Integer, primary_key=True)
    deploymentId = Column(Integer, ForeignKey('Deployment.id'))
    address = Column(String(255))
    startDate = Column(DateTime)
    endDate = Column(DateTime)

    #Backrefs
    meta = relationship("HouseMetadata",
                        order_by="HouseMetadata.id",
                        backref="house")
    occupiers = relationship("Occupier", backref="house")
    locations = relationship("Location", backref="house")

    def __eq__(self,other):
        return self.id == other.id and self.deploymentId == other.deploymentId and self.address == other.address

    def getRooms(self):
        """Function to get the Rooms this house has, This returns the
        rooms that are linked via the
        :class:`cogentviewer.models.location.Location` table.  Meaning
        we can get the rooms in a simple standardised way

        :return: List of :class:`cogentviewer.models.room.Room` objects
        """
        
        return [x.room for x in self.locations]
        


    def asJSON(self, parentId=""):
        theItem = {"id":"H_{0}".format(self.id),
                "name":self.address,
                "label":self.address,
                "type":"house",
                "parent": "D_{0}".format(self.deploymentId),
                "children":[]
                }

        if not self.deploymentId:
            theItem["parent"] = "noDep"

        return theItem


    def flatten(self):
        outDict = [self.asJSON()]

        #if self.locations:
        #    rooms = self.getRooms()
            #children = [x.flatten() for x in rooms]
            #outDict["children"] = children
        #children = [x.flatten() for x in self.nodes]           
        #outDict["children"] = children
        return outDict

    def asTree(self):
        thisItem = self.asJSON()
        thisItem["children"] = [x.asTree() for x in self.locations]
        return thisItem

    def asList(self, parentId = ""):

        outDict = [self.asJSON(parentId)]

        if self.locations:
            outDict[0]["children"] = True
            for item in self.locations:
                outDict.extend(item.asList(self.id))

        return outDict

    def __str__(self):
        outStr = "House {0}  {1}  {2}-{3}".format(self.id,
                                                  self.address,
                                                  self.startDate,
                                                  self.endDate)
        return outStr

