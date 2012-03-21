"""
Classes used by the pushing object to reflect database Tables

:author: Dan Goldsmith <djgoldsmith@googlemail.com>
:date: March 2012
"""

import sqlalchemy

from sqlalchemy.orm import mapper

class RemoteBase(object):
 def __init__(self,**kwargs):
    """
    Create an object using keyword arguments
    """
    for key,value in kwargs.iteritems():
           setattr(self,key,value)

class Node(RemoteBase):
   
   pass

class Sensor(RemoteBase):
   pass

class Room(RemoteBase):
   pass

class House(RemoteBase):
   pass

class Location(RemoteBase):
   def __str__(self):
      return "RLocation {0} {1} {2}".format(self.id,self.houseId,self.roomId)
   pass

class Reading(RemoteBase):
   def __str__(self):
      return "Value: {0} Time: {1}".format(self.value,self.time)
   pass

class RoomType(RemoteBase):
   pass

class Deployment(RemoteBase):
   pass

class NodeState(RemoteBase):
   pass
        



def reflectTables(engine,RemoteMetadata):
    deployment = sqlalchemy.Table('Deployment',
                                  RemoteMetadata,
                                  autoload=True,
                                  autoload_with=engine)

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

    pass

# def initialise_sql(engine):
#     """Intialise a connection to the database and reflect all Remote Tables

#     :param String engine: Database String of Engine to Connect to
#     """
#     #print "Initalising Engine"
#     RemoteSession.configure(bind=engine)
#     #Metadata.bind = engine
#     #Reflect Tables
#     reflectTables(engine)
#     pass


        
