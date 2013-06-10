"""
Classes to initialise the SQL and populate with default Sensors

..version::    0.4
..codeauthor:: Dan Goldsmith
..date::       Feb 2012

..since 0.4:: 
    Models updated to use Mixin Class, This should ensure all
    new tables are created using INNODB
"""

import logging
log = logging.getLogger(__name__)
#log.setLevel(logging.WARNING)

import csv
import os

from sqlalchemy.exc import IntegrityError

from meta import *

#Namespace Mangling
from deployment import *
from deploymentmetadata import *
from host import *
from house import *
from housemetadata import *
from lastreport import *
from location import *
from node import *
from nodehistory import *
from nodestate import *
from nodetype import *
from occupier import *
from rawmessage import *
from reading import *
from room import *
from roomtype import *
from sensor import *
from sensortype import *
from weather import *
from uploadurl import *
from timings import *

import populateData

import json

#Setup Logging
log = logging.getLogger(__name__)


def initialise_sql(engine, dropTables=False):
    """Initialise the database

    :param engine: Engine to use for the database
    :param dropTables: Do we want to clean the database out or not
    :param session: Use a session other than the global DB session

    .. warning:: 
    
        Previously this function called the populateData function. I
        have removed this functionality Any function that calls
        initialise_sql will have to call the init_data method if
        required

    """
    log.info("Initialising Database")
    meta.Session.configure(bind = engine)
    Base.metadata.bind = engine

    if dropTables:
        Base.metadata.drop_all(engine)

    Base.metadata.create_all(engine)  

def populate_data(session=None):
    """Populate the database with some initial data

    :param session: Session to use to populate database"""
    log.info("Populating Data")

    #Create a brand new session, not linked to any sort of transaction managers
    if not session:
        tMaker = sqlalchemy.orm.sessionmaker()
        session = tMaker()
    

    populateData.init_data(session)

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine)


def clsFromJSON(theList):
    """Generator object to convert JSON strings from a rest object
    into database objects"""
    #Convert from JSON encoded string
    if type(theList) == str:
        theList = json.loads(theList)
    
    #Make the list object iterable
    if not type(theList) == list:
        theList = [theList]


    typeMap = {"deployment":Deployment,
               "house":House,
               "reading":Reading,
               "node":Node,
               "sensor":Sensor,
               "nodestate":NodeState,
               "roomtype":RoomType,
               "sensortype":SensorType,
               "room":Room,
               "location":Location,
               }

        
    for item in theList:
        #print "--> {0}".format(item)
        #Convert to the correct type of object
        theType = item["__table__"]
        theModel = typeMap[theType.lower()]()
        #print theModel
        
        theModel.fromJSON(item)
        yield theModel
            
    
