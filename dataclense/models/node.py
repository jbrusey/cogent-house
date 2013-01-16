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

from sqlalchemy import Table, Column, Integer, ForeignKey,String,DateTime,Boolean
from sqlalchemy.orm import relationship, backref

import sqlalchemy.types as types
#from Bitset import Bitset


class Node(Base,meta.InnoDBMix): 
    """
    Class to hold detals of the nodes themselves

    :var Integer id: Node Id
    :var Integer locationId: :class:`cogentviewer.models.location.Location` this node is in
    :var Integer nodeTypeId: :class:`cogentviewer.models.nodetype.NodeType` this node is.

    :var stateHistory: *Backref* to :class:`cogentviewer.models.nodestate.NodeState`
    :var nodeHistory: *Backref* to :class:`cogentviewer.models.nodehistory.NodeHistory`
    :var readings: *Backref* to :class:`cogentviewer.models.reading.Reading`
    :var sensors: *Backref* to :class:`cogentviewer.models.sensor.Sensor`
    """
 
    __tablename__ = "Node"

    id = Column(Integer, primary_key=True)
    locationId = Column(Integer,
                        ForeignKey('Location.id'),
                        nullable=True)     
    nodeTypeId = Column(Integer, ForeignKey('NodeType.id'),
                        nullable=True)  
  
    stateHistory = relationship("NodeState", order_by="NodeState.id",backref="node")
    nodeHistory = relationship("NodeHistory",backref="node")
    readings = relationship("Reading",backref="node")
    sensors = relationship("Sensor", backref=("node"))

    #Add a backref to association Table
    #locations = relationship("Location",secondary="location_node",backref="Nodes")
    locations = relationship("Location",secondary="NodeLocation",backref="OldNodes")   

    def update(self,**kwargs):
        for key,value in kwargs.iteritems():
            setattr(self,key,value)

    def __str__(self):
        return "Node {0} Loc {1}".format(self.id,self.locationId)

    def __eq__(self,other):
        return self.id == other.id and self.locationId == other.locationId and self.nodeTypeId == other.nodeTypeId

    def asJSON(self,parentId=""):
        """Adds a Location Parameter to make sure we can link back to location when we come to get the data"""
        theDict = {"id": "N_{0}".format(self.id),
                   "name": "Node {0}".format(self.id),
                   "type":"node",
                   "parent":"L_{0}".format(parentId),
                   "location": self.locationId,
                   "children":False,
                   }

        return theDict


    def flatten(self):
        outDict = self.asJSON()

        children = [x.flatten() for x in self.sensors]
        outDict["children"] = children
        return outDict


    def asList(self,parentId=""):
        outDict = [self.asJSON(parentId)]
        if self.sensors:
            outDict[0]["children"] = True
            for item in self.sensors:
                outDict.extend(item.asList(self.id))

        return outDict



    def getSamples(self,limit=None):
        """
        Testing Function,
        Can we fetch samples from this Node with some stripping out of data.
        """
        theseReadings = self.readings
        if limit:
            theseReadings = theseReadings[:limit]
        return [x.asJSON() for x in theseReadings]

    
    
    def fromJSON(self,jsonDict):
        super(Node,self).fromJSON(jsonDict)
        log.debug("DEALING WITH NODE")

        if type(jsonDict) == str:
            jsonDict = json.loads(jsonDict)
        if type(jsonDict) == list:
            log.warning("WARNING LIST SUPPLIED {0}".format(jsonDict))
            jsonDict = jsonDict[0]

        locId = jsonDict.get("locationId",None)
        #Lets Try Cheating here.

        log.debug("Current Location {0}, New Id {1}  Associated Locations, {2}".format(self.location,
                                                                                       locId,
                                                                                       self.locations))

        if self.location is None:
            #Force an Update
            log.debug("Forcing Location Update to {0}".format(locId))
            self.locationId = locId
            log.debug("New Loc {} {}".format(self.locationId,self.location))

        elif self.location.id == locId:
            log.debug("Location has been updated correctly")
            if self.location in self.locations:
                log.debug("We Know about this location")
            else:
                log.debug("No such Location in the List")
                self.locations.append(self.location)
        else:
            log.warning("WTF Location Id {0} != locId {1}".format(self.location.id,locId))
            sys.exit(0)
