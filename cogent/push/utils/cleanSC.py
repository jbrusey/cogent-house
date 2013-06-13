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


    def removeNonSampson(self):
        log = self.log
        session = self.localSession()
        theHouses = session.query(models.House).filter(~models.House.address.like("SC-%"))
        for house in theHouses[:1]:
            log.debug("-- Delete {0} --".format(house))
            #Find locations associated with this House
            
            locIds = [x.id for x in house.locations]
            if locIds:
                log.debug("--> House Locations {0}".format(locIds))
                # for lId in locIds:
                dataQry = session.query(models.Reading).filter(models.Reading.locationId.in_(locIds))
                firstItem = dataQry.first()
                log.debug("--> First Item {0}".format(firstItem))
                if firstItem is None:
                    log.debug("No Items, Skip Deleting data")
                else:
                    numRows = dataQry.delete(False)
                    session.flush()
                    log.debug("{0} Items Deleted".format(numRows))
                    session.commit()

                #Then delete Locations
                theQry = session.query(models.Location).filter(models.Location.id.in_(locIds))
                firstItem = theQry.first()
                log.debug("First Location {0}".format(firstItem))
                if firstItem is not None:
                    log.debug("Deleting Locations")
                    theQry.delete(False)
                    session.flush()
                    session.commit()

            log.debug("Deleting House")
            session.delete(house)
            session.flush()
        session.commit()
        session.close()
            #ipt = raw_input("Delete all data for House {0}>".format(house))
            #if ipt.lower() == "y":
            #    log.debug("--> Delete")
            


if __name__ == "__main__":
    THEDB = "mysql://root:adm3csva@127.0.0.1:3307/SampsonClose"
    cln = Cleaner(THEDB)
    cln.removeNonSampson()
