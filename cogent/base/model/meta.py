"""
This metaclass stops the need for the Base function being initiated by all
models, That saves the poor things getting confused with scope.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

import logging
log = logging.getLogger(__name__)


#Functions provided by from meta import *
__all__ = ['Base', 'Session']


#PYRAMID IMPORTS (COMMENT THESE FOR NON PYRAMID OPERATION)
try:
    from zope.sqlalchemy import ZopeTransactionExtension
    Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
except ImportError:
    #STANDARD IMPORTS
    # SQLAlchemy session manager. Updated by model.init_model()
    Session = scoped_session(sessionmaker())

# SQLAlchemy session manager. Updated by model.init_model()
#Session = scoped_session(sessionmaker())

import sqlalchemy

import dateutil.parser

import json

# The declarative Base
Base = declarative_base()



class InnoDBMix(object):
    """
    Mixin Base class for all models used in the viewer.

    Primarily this makes sure that all new database tables are created
    using the InnoDB engine.

    Addtionally this class defines standard functionality that should
    be included in all modules.
    """
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mysql_charset':'utf8'}


    def update(self, **kwargs):
        """
        Update an object using keyword arguments

        :param kwargs: List of keyword arguments to add to this object

        .. note::

            Unlike the keyword based __init__ function provided by Base. This
            has no sanity checking.  Items that have no database column can be
            added to the database, however they will not be saved when the data
            is committed.
        """

        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def toDict(self):
        """
        Helper Method to convert an object to a dictionary.

        This will return a dictionary object, representing this object.

        .. note::  As this is intended to simplify conversion to and from JSON,
                   datetimes are converted using .isoformat()

        :return:: A dictionary of {__table__:<tablename> .. (key,value)* pairs}
        """

        #Appending a table to the dictionary could help us be a little cleverer
        #when unpacking objects
        out = {"__table__": self.__tablename__}

        #Iterate through each column in our table
        for col in self.__table__.columns:
            #Get the value from the namespace (warning, may not work if there is
            #any trickery with column names and names in the python object) Such
            #as in the case of reading.type (typeId) what feckin ejit did that.
            #For the moment we will use a try / except hack To get around it.
            #print col.name

            try:
                value = getattr(self, col.name)
            except AttributeError, e:
                log.warning("Conversion Error {0}".format(e))

            #Conversion code for datetime
            if isinstance(col.type, sqlalchemy.DateTime) and value:
                value = value.isoformat()
            #Append to the dictionary
            out[col.name] = value

        return out

    def fromJSON(self,jsonDict):
        """Update the object using a JSON string

        :var jsonDict:: Either a JSON string (from json.dumps) or dictionary
        containing key,value pairs (from asDict())

        .. note::

            This Is a candidate for moving to a class or staticmethod,
            But inheritance makes it a little bit of a pain
        """

        #Check if we have a string or dictonary
        if type(jsonDict) == str:
            jsonDict = json.loads(jsonDict)

        #For each column in the table
        for col in self.__table__.columns:
            #Check to see if the item exists in our dictionary
            newValue = jsonDict.get(col.name, None)

            #Fix missing values
            if newValue is None:
                pass
            else:
                #Convert if it is a datetime object
                if isinstance(col.type, sqlalchemy.DateTime) and newValue:
                    newValue = dateutil.parser.parse(newValue)

                #And set our variable
                setattr(self, col.name, newValue)
