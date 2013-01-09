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
                #firstType = value[0]
                #log.debug("--> First Room Type {0}".format(firstType))
                #for roomType in value[1:]:
                #    log.debug("--> --> Other Types {0}".format(roomType))

        log.info("----- Checking roosms-----")         
        theQry = session.query(models.Room)
        dupTypes = {}
        for item in theQry:
            itemList = dupTypes.get(item.name,[])
            itemList.append(item)
            dupTypes[item.name] = itemList

            if item.location is None:
                log.debug("--> Room without Location {0}".format(item))

        log.debug("===== CHECKING FOR DUPLICATE ROOMS ====")

        for key,value in dupTypes.iteritems():
            if len(value) > 1:
                log.debug("Duplicate Room {0}".format(key))
                badLocs = []
                firstRoom = value[0]
                print "First Room Is {0}".format(firstRoom)
                for item in value:
                    log.debug("--> Room {0}".format(item))
                    if item.location:
                        log.debug("--> Has Locations")
                        badLocs.extend(item.location)
                    else:
                        log.debug("No Locations")
                        session.delete(item)
                        session.flush()
                session.commit()
                
                print "Locations"
                if len(badLocs) == 0:
                    continue
                print "Bad Locations"
                firstLoc = badLocs[0]
                print "First Location {0}".format(firstLoc)
                for item in set(badLocs[1:]):
                    #print "Loc: ",item
                    #So we Want to fetch the readings
                    rdg = item.filtReadings.first()
                    print "First Reading {0}".format(rdg)
                    theQry = session.query(models.Reading).filter_by(locationId = item.id)
                    #for item in theQry:
                    #    item.locationId = firstLoc.id
                        #print item
                    # #print theQry
                    # print firstLoc.id
                    out = theQry.update({"locationId" : firstLoc.id})
                    print "{0} Samples moved from {1} to {2}".format(out,rdg,firstLoc.id)
                    session.flush()
                    session.commit()
                    session.delete(item)                    
                    session.commit()

                    
                for item in value[1:]:
                    log.debug("--> Room {0}".format(item))
                    log.debug("--> Locs {0}".format(item.location))
                    if not item.location:
                        log.debug("--> Delete")
                        session.delete(item)
                        session.flush()

                if value != firstLoc:
                    log.debug("Delete Duplicate Room")
                    session.delete(item)
                    session.flush()
                
                session.flush()
                session.commit()
                

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
    cleaner = Cleaner("mysql://root:Ex3lS4ga@127.0.0.1/transferTest")
    #cleaner = Cleaner("mysql://root:Ex3lS4ga@127.0.0.1/mainStore")
    cleaner.cleanLocation()
    cleaner.cleanRooms()
    # cleaner.uploadFakeReadings()
