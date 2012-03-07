"""
Classes used by the pushing object to reflect database Tables

:author: Dan Goldsmith <djgoldsmith@googlemail.com>
:date: March 2012
"""

import sqlalchemy

from sqlalchemy.orm import mapper

class RemoteDeployment(object):
    pass

class RemoteHouse(object):
    pass

class RemoteNode(object):
    def __init__(self,id=None,nodeTypeId=None,locationId=None):
        self.id = id
        self.nodeTypeId = nodeTypeId
        self.locationId = locationId
        
class RemoteRoomType(object):
    pass

class RemoteRoom(object):
    pass

class RemoteLocation(object):
    pass

def reflectTables(engine,RemoteMetadata):
    print "Reflecting Tables"
    deployment = sqlalchemy.Table('Deployment',
                                  RemoteMetadata,
                                  autoload=True,
                                  autoload_with=engine)

    mapper(RemoteDeployment,deployment)

    house = sqlalchemy.Table('House',
                             RemoteMetadata,
                             autoload=True,
                             autoload_with=engine)
    mapper(RemoteHouse,house)

    node = sqlalchemy.Table('Node',
                            RemoteMetadata,
                            autoload=True,
                            autoload_with=engine)
    mapper (RemoteNode,node)

    roomType = sqlalchemy.Table('RoomType',
                                RemoteMetadata,
                                autoload=True,
                                autoload_with=engine)
    mapper(RemoteRoomType,roomType)
        
    room = sqlalchemy.Table('Room',
                            RemoteMetadata,
                            autoload=True,
                            autoload_with=engine)
    mapper(RemoteRoom,room)

    location = sqlalchemy.Table('Location',
                            RemoteMetadata,
                            autoload=True,
                            autoload_with=engine)
    mapper(RemoteLocation,location)
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


        
