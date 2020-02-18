"""

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

class Location(Base,meta.InnoDBMix):
    """
    Location provides a link between houses and rooms.
    This is needed if the node is moved, for example during multiple deployments.
    
    This table should be an "associatve array" transparrently linking houses and rooms


    :var Integer id: Id of Location
    :var Integer houseId: Link to :class:`cogentviewer.models.house.House` the room is in
    :var Integer roomId: Link to :class:`cogentviewer.models.room.Room` this location corresponds to
    """

    __tablename__ = "Location"
    __table_args__ = (
        sqlalchemy.UniqueConstraint('houseId', 'roomId'),
        {'mysql_engine': 'InnoDB',
         'mysql_charset':'utf8'},
        )
   
    id = Column(Integer, primary_key=True)
    houseId = Column(Integer,
                     ForeignKey('House.id'))
    roomId = Column(Integer,
                    ForeignKey('Room.id'))

    nodes = relationship("Node",backref=backref('location'))
    readings = relationship("Reading",backref=backref('location'))
    filtReadings = relationship("Reading",lazy='dynamic')

    def asJSON(self,parentId=""):
        """
        Differes from the standard asJSON model by returning the
        name of the room as its name
        """
        theItem = {"id":"L_{0}".format(self.id),
                   "name":"{0}".format(self.room.name),
                   "label":"({0}) {1}".format(self.id,self.room.name),
                   "type":"location",
                   "parent": "H_{0}".format(self.houseId),
                   }
       
        try:
            hasRead = self.readings[0]
        except:
            hasRead = False
            #return None
        #log.info(self.readings.count())
        return theItem

    def getReadings(self,typeId=None):
        """Attempt to return only readings of a certain type

        :param typeId: Type If of object to filter by
        """
        if typeId:
            return self.filtReadings.filter_by(typeId = typeId).all()
        else:
            return self.readings

    def asTree(self):
        return self.asJSON()
        
    def asList(self,parentId = ""):
        outDict = [self.asJSON(parentId)]
        if self.nodes:
            outDict[0]["children"] = True
            for item in self.nodes:
                outDict.extend(item.asList(self.id))
        return outDict


    def __str__(self):
        return "Loaction {0}: {1} {2}".format(self.id,self.houseId,self.roomId)

    def __eq__(self,other):
        return self.id == other.id and self.houseId == other.houseId and self.roomId == other.roomId
    #def __str__(self):
	#    return "({0}) {1} : {2}".format(self.id,self.house.address,self.room.name)


NodeLocation = sqlalchemy.Table("NodeLocation",Base.metadata,
                                sqlalchemy.Column("LocationId",Integer,ForeignKey("Location.id")),
                                sqlalchemy.Column("nodeId",Integer,ForeignKey("Node.id"))
                                )
                                                  

