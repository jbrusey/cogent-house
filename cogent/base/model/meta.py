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
    print "STANDARD SCOPED SESSION LOADED"

# SQLAlchemy session manager. Updated by model.init_model()
#Session = scoped_session(sessionmaker())

# The declarative Base
Base = declarative_base()
