"""
Classes to initialise the SQL and populate with default Sensors

..version::    0.4
..codeauthor:: Dan Goldsmith
..date::       Feb 2012

..since 0.4:: 
    Models updated to use Mixin Class, This should ensure all
    new tables are created using INNODB
"""

import csv
import os

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import mapperlib

from meta import *

#Namespace Manginlg the Proper way, (via all)
#__all__ = ["deployment.*"]

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
from event import *
from timings import *
from user import *

import populateData

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
    Session.configure(bind=engine)
    print "---------------- INIT MODEL CALLED ---------------"
    import pdb; pdb.set_trace()

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
    for x in mapperlib._mapper_registry.items():
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
               "roomtype":RoomType,
               "sensortype":SensorType,
               "room":Room,
               "location":Location,
               "nodetype":NodeType,
               }

    for item in theList:
        #print "--> {0}".format(item)
        #Convert to the correct type of object
        theType = item["__table__"]
        theModel = typeMap[theType.lower()]()
        #print theModel
        
        theModel.fromJSON(item)
        yield theModel
