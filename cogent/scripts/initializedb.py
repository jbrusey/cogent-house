"""
Populate an intial version of the database.

Modified from original webinterface version of the code to remove pyramid
dependencies
"""

import os
import sys
import transaction

# from sqlalchemy import engine_from_config

# from pyramid.paster import (
#     get_appsettings,
#     setup_logging,
#     )

DBFILE = "mysql://chuser@localhost/ch"
import sqlalchemy

from cogent.base.model import meta as meta
#from ..models import meta as meta

Base = meta.Base
#DBSession = meta.Session()


from alembic.config import Config
from alembic import command



from cogent.base.model import populateData as populateData
import cogent.base.model as models

from ..base.model import (
    deployment,
    deploymentmetadata,
    host,
    house,
    housemetadata,
    lastreport,
    location,
    node,
    nodeboot,
    nodehistory,
    nodestate,
    nodetype,
    occupier,
    rawmessage,
    reading,
    room,
    roomtype,
    sensor,
    sensortype,
    weather,
    event,
    timings,
    user,
    )

import getpass
import transaction

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)

def populateUser():
    """Helper method to populate the User table with our initial root user"""
    session = meta.Session()
    
    hasUser = session.query(user.User).first()
    if hasUser is None:
        print "Warning:  No users setup on the system"
        print "  Creating Root User"
        newUser = raw_input("Login Name: ")
        userEmail = raw_input("User Email: ")
        passOne = "FOO"
        passTwo = "BAR"
        while passOne != passTwo:
            passOne = getpass.getpass()
            passTwo = getpass.getpass("Repeat Password: ")
            if passOne != passTwo:
                print "Passwords do not match"
        
        #Setup a new User
        thisUser = user.User(username=newUser,
                             email=userEmail,
                             password=meta.pwdContext.encrypt(passOne),
                             level="root"
                             )
        session.add(thisUser)
        session.flush()
        transaction.commit()



def main(argv=sys.argv):
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # if len(argv) != 2:
    #     usage(argv)
    # config_uri = argv[1]
    # setup_logging(config_uri)
    # settings = get_appsettings(config_uri)
    # engine = engine_from_config(settings, 'sqlalchemy.')
    logging.debug("Initialise Engine")
    engine = sqlalchemy.create_engine(DBFILE, echo=False)
    
    meta.Session.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    


    DBSession = meta.Session()
    #DBSession.configure(bind=engine)
    logging.debug("Populating Data")
    populateData.init_data(DBSession)
    #populateUser()
    logging.debug("Populated")
    DBSession.flush()
    #DBSession.commit()


    #We also want any alembic scripts to be executed (or not if we build the DB
    #properly)
    alembic_cfg = Config("cogent/alembic.ini") #TODO: WARNING RELATIVE PATH
    command.stamp(alembic_cfg,"head")

    DBSession.close()
    
                  
