"""
Classes used by the pushing object to reflect database Tables

..moduleauthor:: Dan Goldsmith <djgoldsmith@googlemail.com>
..date:: March 2012
"""

import sqlalchemy

from sqlalchemy.orm import mapper
import sqlalchemy.orm

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class RemoteBase(object):
    """Base Class for Remote Model Objects"""
    def __init__(self,**kwargs):
        """
        Create an object using keyword arguments
        """
        for key,value in kwargs.iteritems():
           setattr(self,key,value)

class Node(RemoteBase):
    """Node class to map to"""
    pass

class Sensor(RemoteBase):
    """Sensor class to map to"""
    pass

class Room(RemoteBase):
    """Room Class to map to"""
    def __str__(self):
       return "Room ({0}) {1}".format(self.id, self.name)
   
class House(RemoteBase):
    """House Class to map to"""
    def __str__(self):
       outStr = "House {0}  {1}  {2}-{3}".format(self.id,
                                                 self.address,
                                                 self.startDate,
                                                 self.endDate)
       return outStr

class Location(RemoteBase):
    """Location Class to map to"""
    def __str__(self):
        return "RLocation {0} {1} {2}".format(self.id,
                                              self.houseId,
                                              self.roomId)

class Reading(RemoteBase):
    """Reading Class to map to"""
    def __str__(self):
       return "Value: {0} Time: {1}".format(self.value,
                                            self.time)

class RoomType(RemoteBase):
    """Room Typ class to map to"""
    pass

class Deployment(RemoteBase):
    """ Deployment class to map to"""
    def __str__(self):
       return "Deploy {0} {1}".format(self.id,self.name)

    def __eq__(self,other):
       return self.name == other.name
   

class NodeState(RemoteBase):
    """Node State Class to Map To"""
    pass
        

def reflectTables(engine,RemoteMetadata):
    """Reflect all the tables in the remote database.

    This function, connects to the remote database, 
    reflects all relevant tables then sets up mappings to these classes.

    Having mappings setup means that we can call 
   
    .. code-block:: python
   
        >>>foo = remoteModels.Deployment
        >>>Id = foo.id

    Rather than
   
    .. code-block:: python

        >>>foo = remoteModels.meta.tables['deployment']
        >>>id = foo['id']
   
    """

    #Check if we have these tables mapped already.
   
    try:
        mapped = sqlalchemy.orm.class_mapper(Deployment)
        log.debug("Remote Classes already mapped")
        log.debug("> {0} <".format(mapped))
        return
    except sqlalchemy.orm.exc.UnmappedClassError: 
       log.debug("Must Map Remote Classes")

    #Reflect Deployment Table
    deployment = sqlalchemy.Table('Deployment',
                                  RemoteMetadata,
                                  autoload=True,
                                  autoload_with=engine)
    #Setup Mapper
    mapper(Deployment,deployment)
   
    node = sqlalchemy.Table('Node',
                            RemoteMetadata,
                            autoload=True,
                            autoload_with=engine)
    mapper (Node,node)
   
    sensor = sqlalchemy.Table("Sensor",
                              RemoteMetadata,
                              autoload=True,
                              autoload_with=engine)
   
    mapper(Sensor,sensor)
   
    room = sqlalchemy.Table('Room',
                            RemoteMetadata,
                            autoload=True,
                            autoload_with=engine)
    mapper(Room,room)
   
    house = sqlalchemy.Table('House',
                             RemoteMetadata,
                             autoload=True,
                             autoload_with=engine)
    mapper(House,house)
   
    location = sqlalchemy.Table('Location',
                                RemoteMetadata,
                                autoload=True,
                                autoload_with=engine)
    mapper(Location,location)
    
    roomType = sqlalchemy.Table('RoomType',
                                RemoteMetadata,
                                autoload=True,
                                autoload_with=engine)
    mapper(RoomType,roomType)
    
    reading = sqlalchemy.Table("Reading",
                               RemoteMetadata,
                               autoload=True,
                               autoload_with=engine)
    mapper(Reading,reading)
   
    nodeState = sqlalchemy.Table("NodeState",
                                 RemoteMetadata,
                                 autoload=True,
                                 autoload_with=engine)
   
    mapper(NodeState,nodeState)

        
