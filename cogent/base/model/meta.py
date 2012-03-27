"""
This metaclass stops the need for the Base function being initiated by all models,
That saves the poor things getting confused with scope.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

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

# The declarative Base
Base = declarative_base()

class InnoDBMix(object):
    """
    Base class for all models used in the viewer.
    
    This class defines standard functionality that should be included in 
    all modules.

    Additionally, table arguments are given, making sure that any new
    tables created use the InnoDB engine
    """
    
    
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mysql_charset':'utf8'}


    def update(self,**kwargs):
        """
        Update an object using keyword arguments::
	    foo = Template() # Create a blank object
	    foo.update(id=5,value=10) # Set id and value to 5,10 respectively
        """
        for key,value in kwargs.iteritems():
            setattr(self,key,value)



