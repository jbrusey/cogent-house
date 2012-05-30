"""
This metaclass stops the need for the Base function being initiated by all models,
That saves the poor things getting confused with scope.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

import logging
log = logging.getLogger(__name__)


#Functions provided by from meta import *
__all__ = ['Base', 'Session']

#It would be rather nice to be able to do a context sensitive import here,
#But I cant think of a way to do it.
#Therefore, we need to do some manual commenting in / out to get the system to work with
#Both Pyramid and non Pyramid ways of working

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


    def update(self,**kwargs):
        """
        Update an object using keyword arguments

        :param kwargs: List of keyword arguments to add to this object
        
        .. code-block:: python

	    >>>foo = Template() # Create a blank object
            >>>foo 
            Template(id=None,value=None)
            >>>foo.update(id=5,value=10) # Set id and value to 5,10 respectively
            Template(id=5,value=10)
            

        .. note:: 
        
            Unlike the keyword based __init__ function provided by Base. This has no
            sanity checking.  Items that have no database column can be added to the database, 
            however they will not be saved when the data is committed.
        """
        for key,value in kwargs.iteritems():
            setattr(self,key,value)

    def toDict(self):
        """
        Helper Method to convert an object to a dictionary

        :return:: A dictionary of {__table__:<tablename> .. (key,value)* pairs}
        """

        #Appending a table to the dictionary could help us be a little cleverer when unpacking objects
        out = {"__table__":self.__tablename__}

        #Iterate through each column in our table
        for col in self.__table__.columns:
            #Get the value from the namespace (warning, may not work if there is any trickery with column names and names in the python object)
            #Such as in the case of reading.type (typeId) what feckin ejit did that.  For the moment we will use a try / except hack 
            #To get around it.
            #print col.name

            try:
                value = getattr(self,col.name)
            except AttributeError, e:
                #log.warning(e)
                if self.__tablename__ == "Reading" and col.name == "type":
                    value = getattr(self,"typeId")

            #Conversion code for datetime
            if isinstance(col.type,sqlalchemy.DateTime) and value:
                value = value.isoformat()
            #Append to the dictionary
            out[col.name] = value

        return out

    def fromJSON(self,jsonDict):
        """Convert to a table object from a JSON encoded String / dictonary

        .. param jsonDict:: Either a JSON string (from json.dumps) or dictionary containing key,value pairs

        """

        #Check if we have a string or dictonary
        if type(jsonDict) == str:
            jsonDict = json.loads(jsonDict)

        #For each column in the table
        for col in self.__table__.columns:
            #Check to see if the item exists in our dictionary
            newValue = jsonDict.get(col.name,None)
            #Convert if it is a datetime object
            if isinstance(col.type,sqlalchemy.DateTime) and newValue:
                newValue = dateutil.parser.parse(newValue)

            #And set our variable
            
            #And Deal with the corner case above
            if self.__tablename__ == "Reading" and col.name == "type":
                setattr(self,"typeId",newValue)
            else:
                setattr(self,col.name,newValue)
