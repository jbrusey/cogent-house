#! /bin/python

import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import meta as meta
import cogentviewer.utils.security as security

Base = meta.Base
#DBSession = meta.Session()

from alembic.config import Config
from alembic import command

from ..models import populateData as populateData
import cogentviewer.models as models
from ..models import (
    deployment,
    deploymentmetadata,
    host,
    house,
    housemetadata,
    lastreport,
    location,
    node,
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
    pushstatus,
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
                             password=security.pwdContext.encrypt(passOne),
                             level="root"
                             )
        session.add(thisUser)
        session.flush()
        transaction.commit()



def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    meta.Session.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)

    #We also want any alembic scripts to be executed
    alembic_cfg = Config(config_uri) #TODO: WARNING RELATIVE PATH
    command.stamp(alembic_cfg,"head")

    DBSession = meta.Session()
    #DBSession.configure(bind=engine)
    
    populateData.init_data(DBSession)
    populateUser()
