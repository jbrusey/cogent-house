"""
This metaclass stops the need for the Base function being initiated by all
models, That saves the poor things getting confused with scope.
"""

import warnings

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

import logging
LOG = logging.getLogger(__name__)


#Functions provided by from meta import *
__all__ = ['Base', 'Session']


#PYRAMID IMPORTS (COMMENT THESE FOR NON PYRAMID OPERATION)
# try:
#     from zope.sqlalchemy import ZopeTransactionExtension
#     Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
# except ImportError:
#     #STANDARD IMPORTS
#     # SQLAlchemy session manager. Updated by model.init_model()
#     Session = scoped_session(sessionmaker())

# SQLAlchemy session manager. Updated by model.init_model()
Session = scoped_session(sessionmaker())

import sqlalchemy

import dateutil.parser

import json

# The declarative Base
Base = declarative_base()

import warnings
  
class SerialiseMixin(object):

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


    def dict(self):
        """
        Method to convert a row from an SQLAlchemy table to a dictionary.

        This will return a dictionary repreentation of the row, 
        To aid with identifing which table the serialised object has come from, the table name is appended 
        to the dictionay under the "__table__" key.

        .. note::  As this is intended to simplify conversion to and from JSON,
                   datetimes are converted using .isoformat()

        :return:: A dictionary of {__table__:<tablename> .. (key,value)* pairs}
        """
        
        out = {"__table__": self.__tablename__}

        #Iterate through each column in our table
        for col in self.__table__.columns:
            #Get the value from the namespace (warning, may not work if there is
            #any trickery with column names and names in the python object)

            try:
                value = getattr(self, col.name)
            except AttributeError, e:
                LOG.warning("Conversion Error {0}".format(e))

            #Conversion code for datetime
            if isinstance(col.type, sqlalchemy.DateTime) and value:
                value = value.isoformat()
            #Append to the dictionary
            out[col.name] = value

        return out

    def json(self):
        return json.dumps(self.dict())

    def toDict(self):
        """
        Method to convert a row from an SQLAlchemy table to a dictionary.

        This will return a dictionary repreentation of the row, 
        To aid with identifing which table the serialised object has come from, the table name is appended 
        to the dictionay under the "__table__" key.

        .. note::  As this is intended to simplify conversion to and from JSON,
                   datetimes are converted using .isoformat()

        :return:: A dictionary of {__table__:<tablename> .. (key,value)* pairs}

        .. deprecated:: 0.2.0
             toDict() will be removed in favor of the dict() method, (prepare for transistion to restAlchmey)
        """

        LOG.warning("toDict Depricated, please use dict() function instead")
        #Appending a table to the dictionary could help us when unpacking objects
        warnings.warn("meta.toDict() method has been depricated, please use meta.dict() instead",
                      DeprecationWarning)

        return self.dict()

#    def fromDict(self,theDict):
#        """Update the object given a dictionary of <key>,<value> pairs
#        """

    def from_dict(self,jsonList):
        """Update the object using a dictionary

        :var jsonDict:: A dictionary containing key,value pairs (from asDict())

        :return:  A copy of the original object
        """
        
        return self.from_json(jsonList)

    def from_json(self, jsonobj):
        """Update the object using a JSON string

        :var jsonobj:: Either a JSON string (from json.dumps) or dictionary
        containing key,value pairs (from asDict())

        :return:  A copy of the original object
        """

        if type(jsonobj) == str:
            jsonobj = json.loads(jsonobj)
        if type(jsonobj) == list:
            jsonobj = jsonobj[0]
        #For each column in the table
        for col in self.__table__.columns:
            #Check to see if the item exists in our dictionary
            value = jsonobj.get(col.name, None)
            
            #Fix missing values
            #if col.name == "locationId":
            #    setattr(self,col.name,newValue)
            if value is None:
                pass
            else:
                #Convert if it is a datetime object
                if isinstance(col.type, sqlalchemy.DateTime) and value:
                    value = dateutil.parser.parse(value, ignoretz=True)
                #And set our variable
            setattr(self, col.name, value)

    def fromJSON(self,jsonDict):
        """Update the object using a JSON string

        :var jsonDict:: Either a JSON string (from json.dumps) or dictionary
        containing key,value pairs (from asDict())

        :return:  A copy of the original object
        """

        warnings.warn("meta.fromJSON() method has been depricated, please use meta.from_json() instead",
                      DeprecationWarning)

        return self.from_json(jsonDict)

class InnoDBMix(SerialiseMixin):
    """
    Mixin Base class for all models used in the viewer.

    Primarily this makes sure that all new database tables are created
    using the InnoDB engine.

    Addtionally this class defines standard functionality that should
    be included in all modules.
    """
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mysql_charset':'utf8'}









