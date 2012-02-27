"""Metaclass to initiate all objects and start the database.

This really just makes sure all database code is in the same place
meaing the DB is consistently intiataed in all test cases.
"""


"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

engine = sqlalchemy.create_engine("sqlite:///:memory:",echo=False)
Base.metadata.create_all(engine)
Session = sqlalchemy.orm.sessionmaker(bind=engine)

    
#Create our Test Objects
session = Session()

"""

#CONFIG
DB_URL = 'sqlite:///:memory:'

#sqlalchemy Imports
import sqlalchemy


try:
    import cogent
except ImportError:
    #Assume we are running from the test directory
    #print "Unable to Import Cogent Module Appending Path"
    import sys
    sys.path.append("../")

#Import our Base Metadata etc
#from cogent.base.model import *
#Base = cogent.models.
#from cogent.base.model.meta import Session, Base
from cogent.base.model.meta import Base

engine = sqlalchemy.create_engine(DB_URL)#,echo=True)
Base.metadata.create_all(engine)

Session = sqlalchemy.orm.sessionmaker(bind=engine)
#print engine
