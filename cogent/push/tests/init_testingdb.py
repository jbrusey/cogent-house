#! /bin/python

import os
import sys
import transaction
import math
import datetime

import sqlalchemy
import transaction
#from sqlalchemy import engine_from_config

#from pyramid.paster import (
#    get_appsettings,
#    setup_logging,
#    )

from cogent.base.model import meta as meta

Base = meta.Base
#DBSession = meta.Session()

from alembic.config import Config
from alembic import command

from cogent.base.model import populateData as populateData
import cogent.base.model as models

#import getpass
#import transaction

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)

def populateUser():
    """Helper method to populate the User table with our initial root user"""
    session = meta.Session()
    
    
    newuser = user.User(username="test",
                        email="test",
                        password=meta.pwdContext.encrypt("test"),
                        level="root")

    session.merge(newuser)
    session.flush()
    transaction.commit()

    # hasUser = session.query(user.User).first()
    # if hasUser is None:
    #     print "Warning:  No users setup on the system"
    #     print "  Creating Root User"
    #     newUser = raw_input("Login Name: ")
    #     userEmail = raw_input("User Email: ")
    #     passOne = "FOO"
    #     passTwo = "BAR"
    #     while passOne != passTwo:
    #         passOne = getpass.getpass()
    #         passTwo = getpass.getpass("Repeat Password: ")
    #         if passOne != passTwo:
    #             print "Passwords do not match"
        
    #     #Setup a new User
    #     thisUser = user.User(username=newUser,
    #                          email=userEmail,
    #                          password=meta.pwdContext.encrypt(passOne),
    #                          level="root"
    #                          )
    #     session.add(thisUser)
    #     session.flush()
    #     transaction.commit()



def populatedata(session = None):
    """Populate our testing database with an example deployment etc"""

    #The Deployment
    if not session:
        print "Creating a new Session"
        session = meta.Session()

    #Remove Existing nodes as they just confuse things
    qry = session.query(models.Node)
    qry.delete()
    session.flush()
    session.commit()
    transaction.commit()

    #now = datetime.datetime.now()
    now = datetime.datetime(2013,01,01,00,00,00)

    thedeployment = models.Deployment(id=1,
                                      name="testing",
                                      description="a testing deployment",
                                      startDate = now)

    session.merge(thedeployment)
    session.flush()

    #We also add a testing house
    thehouse = models.House(id=1,
                            address="testing house",
                            deploymentId = thedeployment.id,
                            startDate = now)

    session.merge(thehouse)
    session.flush()

    #Lets add two locations
    thebedroom = models.Location(id=1,
                                 houseId = thehouse.id,
                                 roomId = 1)

    thebathroom = models.Location(id=2,
                                  houseId = thehouse.id,
                                  roomId = 6)

    session.merge(thebedroom)
    session.merge(thebathroom)
    session.flush()
    session.commit()

    #update the nodes so they have the correct locations
    thenode = session.query(models.Node).filter_by(id=837).first()
    if thenode is None:
        print "Create Node 837"
        thenode = models.Node(id=837,
                              locationId=1)
        session.add(thenode)

    thenode = session.query(models.Node).filter_by(id=838).first()
    if thenode is None:
        thenode = models.Node(id=838,
                              locationId=2)
        print "Create Node 838"
        session.add(thenode)
    
    session.flush()
    transaction.commit()
    session.commit()

    #transaction.commit()

    #To test the Yields I also want an incomplte database
    thehouse = models.House(id=2,
                            address="Poor House",
                            deploymentId = thedeployment.id,
                            startDate = now)
    session.merge(thehouse)

    #Add a couple of locations
   #Lets add two locations
    thebedroom = models.Location(id=3,
                                 houseId = thehouse.id,
                                 roomId = 1)
    session.merge(thebedroom)

    thebathroom = models.Location(id=4,
                                  houseId = thehouse.id,
                                  roomId = 6)

    session.merge(thebathroom)
    session.flush()
    session.commit()
    transaction.commit()


    thenode = session.query(models.Node).filter_by(id=1061).first()
    if thenode is None:
        thenode = models.Node(id=1061,
                              locationId=3)
        print "Create Node 1061"
        session.add(thenode)
    thenode.locationId = 3

    thenode = session.query(models.Node).filter_by(id=1063).first()
    if thenode is None:
        thenode = models.Node(id=1063,
                              locationId=4)
        print "Create Node 1063"
        session.add(thenode)

    session.flush()
    session.commit()

def populate_readings(session = None):

    #The Deployment
    if not session:
        print "Creating a new Session"
        session = meta.Session()

    now = datetime.datetime(2013,01,01,00,00,00)

    #Now we want to add a load of readings / Nodestates
    thetime = now# - datetime.timedelta(days = 10)
    endtime = now + datetime.timedelta(days=10)
    #print "START TIME {0}".format(starttime)

    thecount = 0.0
    seqnum = -1
    while thetime < endtime:
        #Increment and roll over the sequence number
        seqnum += 1
        if seqnum > 255:
            seqnum = seqnum - 255
            
        for nid in [837, 838, 1061, 1063]:

            locationid = 1
            if nid == 838:
                locationid = 2
            elif nid == 1061:
                locationid = 3
                #Sample very 10 minutes (50% Yield)
                if thetime.minute % 10 == 0:
                    continue
            elif nid == 1063:
                locationid = 4
                #And remove every 3rd sample
                if thetime.minute % 15 == 0:
                    continue

            ns = models.NodeState(nodeId = nid,
                                  parent = 1,
                                  time = thetime,
                                  seq_num = seqnum)

            session.add(ns)

        
            reading = models.Reading(nodeId = nid,
                                     typeId = 0,
                                     time = thetime,
                                     locationId = locationid,
                                     value = 18.0+(2.0*math.sin(thecount)),
                                     )
            session.add(reading)




        #Increment the time
        thetime = thetime + datetime.timedelta(minutes=5)
        thecount = thecount + (3.14 / 144)

    session.commit()
    transaction.commit()
    session.commit()
    session.close()



def main(dburl="sqlite:///pushtest.db"):
    # if len(argv) != 2:
    #     usage(argv)
    # config_uri = argv[1]
    # setup_logging(config_uri)
    # settings = get_appsettings(config_uri)
    # engine = engine_from_config(settings, 'sqlalchemy.')
    # meta.Session.configure(bind=engine)
    # Base.metadata.bind = engine

    # #As its a testing database
    # #Base.metadata.drop_all()
    # try:
    #     transaction.commit()
    # except sqlalchemy.exc.OperationalError:
    #     print "No database exists"



    # Base.metadata.create_all(engine)

    # #We also want any alembic scripts to be executed
    # alembic_cfg = Config("alembic.ini") #TODO: WARNING RELATIVE PATH
    # command.stamp(alembic_cfg,"head")

    # DBSession = meta.Session()
    # #DBSession.configure(bind=engine)
    
    import time

    print "Creating Database for {0}".format(dburl)
    t1 = time.time()

    engine = sqlalchemy.create_engine(dburl)
    connection = engine.connect()
    print "--> Time to create Engine {0}".format(time.time() - t1)

    #try:
    #    connection.execute("delete from nodestate")
    #    connection.execute("delete from reading")
    #except:
    #    print "Error deleting existing tables"


    #transaction.commit()
    print "Initialising SQL"

    #Create a connection to the database
    Base.metadata.bind = engine

    Base.metadata.drop_all(engine)
    print "--> Time to Drop {0}".format(time.time() - t1)
    Base.metadata.create_all(engine)  
    print "--> Time Create {0}".format(time.time() - t1)
    # #Start the transaction 
    # #trans = connection.begin()
    populateData.init_data()
    print "--> Time to Init {0}".format(time.time() - t1)   
    populatedata()
    print "--> Time to Populate {0}".format(time.time() - t1)
    populate_readings()

if __name__ == "__main__":
    main()
