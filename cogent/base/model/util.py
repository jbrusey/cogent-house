"""
util.py - move utility functions out of __init__

@author D. Goldsmith
@author J. Brusey
"""

from sqlalchemy.orm import mapperlib

from . import meta

#Namespace Mangling
from .deployment import Deployment
from .house import House
from .location import Location
from .node import Node
from .nodestate import NodeState
from .nodetype import NodeType
from .nodeboot import NodeBoot
from .reading import Reading
from .room import Room
from .roomtype import RoomType
from .sensor import Sensor
from .sensortype import SensorType

import json

#Setup Logging
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)

TABLEMAP = {}

def init_model(engine):
    """Call me before using any of the tables or classes in the model

    DO NOT REMOVE ON MERGE
    """
    meta.Session.configure(bind=engine)
   

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
    meta.Base.metadata.bind = engine

    if dropTables:
        meta.Base.metadata.drop_all(engine)

    meta.Base.metadata.create_all(engine)

def findClass(tableName):
    """Helper method that attempts to find a SQLA class given a tablename
    :var tablename: Name of table to find
    """

    tableName = tableName.lower()
    log.debug(TABLEMAP)
    mappedTable = TABLEMAP.get(tableName,None)
    if mappedTable:
        return mappedTable

    log.debug("Looking for {0}".format(tableName))
    for x in list(mapperlib._mapper_registry.items()):
        #mapped table
        log.debug("--> Checking against {0}".format(x))
        checkTable = x[0].mapped_table
        theClass = x[0].class_
        log.debug("--> Mapped Table {0}".format(checkTable))
        checkName = checkTable.name.lower()
        TABLEMAP[checkName] = theClass
        if checkName == tableName:
            log.debug("--> Match {0}".format(checkTable.name))
            log.debug("--> Class is {0}".format(theClass))
            mappedTable = theClass

    log.debug("--> Final Verison {0}".format(mappedTable))
    return mappedTable

def newClsFromJSON(jsonItem):
    """Method to create class from JSON"""
    if type(jsonItem) == str:
        jsonItem = json.loads(jsonItem)

    log.debug("Loading class from JSON")
    log.debug("JSON ITEM IS {0}".format(jsonItem))
    theType = jsonItem["__table__"]
    log.debug("Table from JSON is {0}".format(theType))
    theClass = findClass(theType)
    log.debug("Returned Class {0}".format(theClass))
    #Iterate through to find the class
    #Create a new instace of this models
    theModel = theClass()
    log.debug("New model is {0}".format(theModel))
    #And update using the JSON stuff
    theModel.fromJSON(jsonItem)
    log.debug("Updated Model {0}".format(theModel))
    return theModel

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
               "nodeboot":NodeBoot,
               "roomtype":RoomType,
               "sensortype":SensorType,
               "room":Room,
               "location":Location,
               "nodetype":NodeType,
               }

    for item in theList:
        if type(item) == str or type(item) == str:
            item = json.loads(item)
        #Convert to the correct type of object
        theType = item["__table__"]
        theModel = typeMap[theType.lower()]()
        #print theModel
        
        theModel.fromJSON(item)
        yield theModel