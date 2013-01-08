"""Script to help clean up datasets betfore transfer"""

import logging
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(name)-10s %(levelname)-8s %(message)s",
                    datefmt = "%m-%d-%Y %H:%M")


import sqlalchemy
#import remoteModels

import cogent

import cogent.base.model as models

import cogent.base.model.meta as meta


class Cleaner(object):
    def __init__(self,localURL):
        log = logging.getLogger("Cleaner")
        engine = sqlalchemy.create_engine(localURL)
        models.initialise_sql(engine)
        localSession = sqlalchemy.orm.sessionmaker(bind=engine)
        self.localSession = localSession
        log.info("Database Connection to {0} OK".format(localURL))
        self.log = log

    def cleanAll(self):
        pass

    def cleanDeployment(self):
        """Remove Deployments without any houses attached"""
        session = self.localSession()
        log = self.log
        theQry = session.query(models.Deployment)
        removeItems = []
        for item in theQry:
            hasHouses = item.houses
            if not hasHouses:
                log.debug("--> No Houses attached to deployment {0}".format(item))
                removeItems.append(item)

        log.info("Deployments without Houses")
        for item in removeItems:
            log.info("--> {0}".format(item))


    def cleanLocation(self):
        """Look for Locations without any Readings"""
        session = self.localSession()
        log = self.log

        theQry = session.query(models.Location)
        badLocs = []
        for item in theQry:
            firstReading = item.filtReadings.first()
            #firstReading = item.readings.first()
            #log.debug("Location {0} total Readings {1}".format(item,firstReading))
            if firstReading is None:
                log.debug("--> Location without any readings {0}".format(item))
                badLocs.append(item)
                session.delete(item)
        
        session.commit()
        print "Locations without any Readings:"
        #for item in badLocs:
        #    print item
        locIds = [x.id for x in badLocs]
        print "SELECT * FROM Location WHERE id IN {0}".format(locIds)
        
                

    def cleanRooms(self):
        """Clean up Rooms and RoomTypes without any links"""
        session = self.localSession()
        log = self.log
        
        log.info("----- Checking room types-----")
        theQry = session.query(models.RoomType)
        dupTypes = {}
        for item in theQry:
            itemList = dupTypes.get(item.name,[])
            itemList.append(item)
            dupTypes[item.name] = itemList
            if item.rooms is None:
                log.debug("--> Room type without any Rooms {0}".format(item))

        for key,value in dupTypes.iteritems():
            if len(value) > 1:
                log.debug("--> Duplicate Room Type {0} {1}".format(key,value))

        
        log.info("----- Checking roosms-----")         
        theQry = session.query(models.Room)
        dupTypes = {}
        for item in theQry:
            itemList = dupTypes.get(item.name,[])
            itemList.append(item)
            dupTypes[item.name] = itemList

            if item.location is None:
                log.debug("--> Room without Location {0}".format(item))

        log.debug("===== CHECKING FOR DUPLICATE ROOM TYPES ====")
        badLocs = []
        for key,value in dupTypes.iteritems():
            if len(value) > 1:
                log.debug("--> Duplicate Room Type {0} {1}".format(key,value))
                for item in value:
                    log.debug("--> Room {0}".format(item))
                    badCount = 0
                    for loc in item.location:
                        log.debug("--> --> Location {0}".format(loc))
                        #Then check for readings
                        rdg = loc.filtReadings.first()
                        log.debug("--> --> --> First Reading {0}".format(rdg))
                        if rdg is None:
                            badLocs.append(loc.id)
                            badCount += 1
                    if badCount == len(item.location):
                        log.debug("--> --> Room Has No Valid Locations {0}".format(item))
                        session.delete(item)
                        session.commit()
                    else:
                       log.debug("--> Refactoring so readings have the same Location")
                       #firstLoc = value[0]
                       #remLocs = value[1:]
                       #log.debug("First Location {0}".format(firstLoc))
                       #log.debug("Remaining Locations {0}".format(remLocs))
        print badLocs
                    



    def uploadFakeReadings(self):
        import datetime
        now = datetime.datetime.now()
        session = self.localSession()
        for x in range(100000):
            thisTime = now + datetime.timedelta(seconds = x)
            theSample = models.Reading(time=thisTime,
                                       nodeId = 837,
                                       locationId = 1,
                                       typeId = 0,
                                       value = x)
            session.add(theSample)
        session.flush()
        session.commit()

if __name__ == "__main__":
    #cleaner = Cleaner("mysql://root:Ex3lS4ga@127.0.0.1/transferTest")
    cleaner = Cleaner("mysql://root:Ex3lS4ga@127.0.0.1/mainStore")
    cleaner.cleanLocation()
    cleaner.cleanRooms()
    # cleaner.uploadFakeReadings()
