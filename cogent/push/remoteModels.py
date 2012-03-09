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

class Node(object):
    def __init__(self,id=None,nodeTypeId=None,locationId=None):
        self.id = id
        self.nodeTypeId = nodeTypeId
        self.locationId = locationId

class Sensor(RemoteBase):
    pass

    


class RoomType(object):
    pass


# class Room(object):
#     pass


# class Deployment(object):
#     pass

# class House(object):
#     pass

        

# class Location(object):
#     pass

def reflectTables(engine,RemoteMetadata):
    print "Reflecting Tables"
    # deployment = sqlalchemy.Table('Deployment',
    #                               RemoteMetadata,
    #                               autoload=True,
    #                               autoload_with=engine)

    # mapper(Deployment,deployment)

    # house = sqlalchemy.Table('House',
    #                          RemoteMetadata,
    #                          autoload=True,
    #                          autoload_with=engine)
    # mapper(House,house)

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



    roomType = sqlalchemy.Table('RoomType',
                                RemoteMetadata,
                                autoload=True,
                                autoload_with=engine)
    mapper(RoomType,roomType)
        
    # room = sqlalchemy.Table('Room',
    #                         RemoteMetadata,
    #                         autoload=True,
    #                         autoload_with=engine)
    # mapper(Room,room)

    # location = sqlalchemy.Table('Location',
    #                         RemoteMetadata,
    #                         autoload=True,
    #                         autoload_with=engine)
    # mapper(RemoteLocation,location)
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


        
