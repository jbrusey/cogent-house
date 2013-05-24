"""
.. codeauthor::  Ross Wiklins 
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>

"""

import logging
LOG = logging.getLogger(__name__)

import meta


from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref

#import sqlalchemy.types as types

import location

class Node(meta.Base, meta.InnoDBMix):
    """
    Class to hold detals of the nodes themselves

    :var Integer id: Node Id
    :var Integer locationId: `Location` this node is in
    :var Integer nodeTypeId: `NodeType` this node is.

    :var stateHistory: *Backref* to `nodestate.NodeState`
    :var nodeHistory: *Backref* to `nodehistory.NodeHistory`
    :var readings: *Backref* to `reading.Reading`
    :var sensors: *Backref* to `sensor.Sensor`
    """

    __tablename__ = "Node"

    id = Column(Integer, primary_key=True)
    locationId = Column(Integer,
                        ForeignKey('Location.id'),
                        nullable=True)
    nodeTypeId = Column(Integer, ForeignKey('NodeType.id'),
                        nullable=True)

    stateHistory = relationship("NodeState",
                                order_by="NodeState.id",
                                backref="node")
    nodeHistory = relationship("NodeHistory",
                               backref="node")
    readings = relationship("Reading",
                            backref="node")
    sensors = relationship("Sensor",
                           backref=("node"))

    #Add a backref to association Table

    # locations = relationship("Location",
    #                          secondary="NodeLocation",
    #                          backref="node")


    def __eq__(self, other):
        """Nodes should be equal in Id (and type but it may not exist) Only"""
        return self.id == other.id

    def __ne__(self, other):
        """Ids differ"""
        return not(self.id == other.id)

    def __lt__(self, other):
        return self.id < other.id

    def update(self, **kwargs):
        for key,value in kwargs.iteritems():
            setattr(self,key,value)

    def __str__(self):
        return "Node {0} Loc {1}".format(self.id,self.locationId)

    def asJSON(self, parentId=""):
        """Adds a Location Parameter to make sure we can
        link back to location when we come to get the data"""
        theDict = {"id": "N_{0}".format(self.id),
                   "name": "Node {0}".format(self.id),
                   "type": "node",
                   "parent": "L_{0}".format(parentId),
                   "location": self.locationId,
                   "children": False,
                   }

        return theDict

    # def flatten(self):
    #     outDict = self.asJSON()

    #     children = [x.flatten() for x in self.sensors]
    #     outDict["children"] = children
    #     return outDict


    # def asList(self, parentId=""):
    #     outDict = [self.asJSON(parentId)]
    #     if self.sensors:
    #         outDict[0]["children"] = True
    #         for item in self.sensors:
    #             outDict.extend(item.asList(self.id))

    #     return outDict

    # def getSamples(self, limit=None):
    #     """
    #     Testing Function,
    #     Can we fetch samples from this Node with some stripping out of data.
    #     """
    #     theseReadings = self.readings
    #     if limit:
    #         theseReadings = theseReadings[:limit]
    #     return [x.asJSON() for x in theseReadings]

    def fromJSON(self, jsondict):
        super(Node,self).fromJSON(jsondict)
        LOG.debug("DEALING WITH NODE")

        if type(jsondict) == str:
            jsondict = json.loads(jsondict)
        if type(jsondict) == list:
            LOG.warning("WARNING LIST SUPPLIED {0}".format(jsondict))
            jsondict = jsondict[0]

        locId = jsondict.get("locationId",None)
        #Lets Try Cheating here.

        if locId is None:
            return

        return
        session = meta.Session()
        newLocation = session.query(location.Location).filter_by(id=locId).first()

        if self.locationId is None:
            #Force an Update
            LOG.debug("Forcing Location Update to {0}".format(locId))
            self.locationId = locId
            self.all_locs.append(newLocation)
            LOG.debug("New Loc {0} {1}".format(self.locationId,self.location))

        elif self.locationId == locId:
            LOG.debug("Location has been updated correctly")
            if self.location in self.all_locs:
                LOG.debug("We Know about this location")
            else:
                LOG.debug("No such Location in the List")
                self.all_locs.append(newLocation)
        else:
            LOG.warning("Location Id {0} != locId {1}".format(self.location.id,
                                                              locId))
