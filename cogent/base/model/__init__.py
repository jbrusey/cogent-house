"""
Classes to initialise the SQL and populate with default Sensors

:version: 0.4
:author: Dan Goldsmith
:date: Feb 2012

:since 0.4:  Models updated to use Mixin Class, This should ensure all new tables are created using INNODB
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

import populateData

#Setup Logging
log = logging.getLogger(__name__)

Session = sqlalchemy.orm.sessionmaker()

def initialise_sql(engine,dropTables=False,session=False):
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
    Session.configure(bind=engine)
    Base.metadata.bind=engine

    if dropTables:
        Base.metadata.drop_all(engine)

    Base.metadata.create_all(engine)  

def populate_data(session=None):
    """Populate the database with some initial data

    :param session: Session to use to populate database"""
    if not session:
        session = meta.Session()

    populateData.init_data(session)

    
    
def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine)
