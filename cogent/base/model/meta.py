"""
This metaclass stops the need for the Base function being initiated by all
models, That saves the poor things getting confused with scope.
"""

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

    def dict(self):
        """place holder before we move across to the RestALCHEMY version
        """
        return self.toDict()

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

        #LOG.warning("toDict Depricated, please use dict() function instead")
        #Appending a table to the dictionary could help us when unpacking objects
        
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


#    def fromDict(self,theDict):
#        """Update the object given a dictionary of <key>,<value> pairs
#        """

    def from_dict(self,jsonList):
        return self.fromJSON(jsonList)

    def from_json(self,jsonList):
        return self.fromJSON(jsonList)

    def fromJSON(self,jsonDict):
        """Update the object using a JSON string

        :var jsonDict:: Either a JSON string (from json.dumps) or dictionary
        containing key,value pairs (from asDict())
        """

        #Check if we have a string or dictonary
        #LOG.warning("fromJSON depricated in 0.2.0,  use from_json() instead")
        #LOG.debug("de-serialising {0}".format(jsonDict))

        if type(jsonDict) == str:
            jsonDict = json.loads(jsonDict)
        if type(jsonDict) == list:
            jsonDict = jsonDict[0]
        #For each column in the table
        for col in self.__table__.columns:
            #Check to see if the item exists in our dictionary
            newValue = jsonDict.get(col.name, None)
            
            #Fix missing values
            #if col.name == "locationId":
            #    setattr(self,col.name,newValue)
            if newValue is None:
                pass
            else:
                #Convert if it is a datetime object
                if isinstance(col.type, sqlalchemy.DateTime) and newValue:
                    LOG.debug("{0} CASTING DATE {0}".format("-="*15))
                    newValue = dateutil.parser.parse(newValue,ignoretz=True)
                    LOG.debug("New Time {0}".format(newValue))
                #And set our variable
            setattr(self, col.name, newValue)


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
                LOG.warning("Conversion Error {0}".format(e))

            #Conversion code for datetime
            if isinstance(col.type, sqlalchemy.DateTime) and value:
                value = value.isoformat()
            #Append to the dictionary
            out[col.name] = value

        return out

#    def fromDict(self,theDict):
#        """Update the object given a dictionary of <key>,<value> pairs
#        """

    def from_dict(self,jsonList):
        return self.fromJSON(jsonList)

    def from_json(self,jsonList):
        return self.fromJSON(jsonList)


    def fromJSON(self,jsonDict):
        """Update the object using a JSON string

        :var jsonDict:: Either a JSON string (from json.dumps) or dictionary
        containing key,value pairs (from asDict())

        .. note::

            This Is a candidate for moving to a class or staticmethod,
            But inheritance makes it a little bit of a pain
        """

        #Check if we have a string or dictonary
        
        #LOG.debug("FROMJSON Demung {0}".format(jsonDict))

        if type(jsonDict) == str:
            jsonDict = json.loads(jsonDict)
        if type(jsonDict) == list:
            LOG.warning("WARNING LIST SUPPLIED {0}".format(jsonDict))
            jsonDict = jsonDict[0]
        #For each column in the table
        for col in self.__table__.columns:
            #Check to see if the item exists in our dictionary
            newValue = jsonDict.get(col.name, None)
            
            #Fix missing values
            if col.name == "locationId":
                setattr(self,col.name,newValue)
            elif newValue is None:
                pass
            else:
                #Convert if it is a datetime object
                if isinstance(col.type, sqlalchemy.DateTime) and newValue:
                    LOG.debug("{0} CASTING DATE {0}".format("-="*15))
                    newValue = dateutil.parser.parse(newValue,ignoretz=True)
                    LOG.debug("New Time {0}".format(newValue))
                #And set our variable
                setattr(self, col.name, newValue)

import user


# class RootFactory(object):
#     """New Root Factory Object to assign permissions
#     And control the ACL
#     """

#     __acl__ = [(Allow,Everyone,"logout"),
#                (Allow,"group:user","view"),
#                (Allow,"group:root","view")]
    
#     def __init__(self,request):
#         pass

# def groupfinder(userid,request):
#     LOG.debug("-----> Group Finder Called {0}".format(userid))
#     session = Session()
#     theUser = session.query(user.User).filter_by(id=userid).first()
#     if theUser is None:
#         return ["group:none"]

#     if theUser.level == "root":
#         return["group:root"]
#     elif theUser.level == "user":
#         return ["group:user"]

#     return ["group:none"]
