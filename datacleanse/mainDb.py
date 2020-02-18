import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

#Sqlalchemy for local connection
import sqlalchemy
import sqlalchemy.orm

#Pyramid modules
from sqlalchemy.ext.declarative import declarative_base

import models
import models.meta as meta
import models.populateData as popData

#DB
#THEDB = "mysql://chuser@127.0.0.1/transferTest"
#THEDB = "mysql://root:Ex3lS4ga@127.0.0.1/mainStore"
#THEDB = "mysql://root:Ex3lS4ga@127.0.0.1/transferTest"
THEDB = "mysql://root:adm3csva@127.0.0.1:3307/SampsonClose"

def initDB():
    log.debug("Connecting to database")

    engine = sqlalchemy.create_engine(THEDB)
    meta.Session.configure(bind=engine)
    meta.Base.metadata.bind = engine
    meta.Base.metadata.create_all(engine)


def calculateYield(theAddress):
    session = meta.Session()
    log.debug("Calculating Yield")
    theHouse = session.query(models.House).filter_by(address=theAddress).first()
    log.debug("House is {0}".format(theHouse))
    
    #Locations associated with this house
    theLocations = session.query(models.Location).filter_by(houseId = theHouse.id).all()
    log.debug("Locations for this house:")
    for item in theLocations:
        log.debug("--> {0}".format(item))
    
    #Not most efficent but allows the above to be printed
    locIds = [x.id for x in theLocations]
    log.debug("Location Id's {0}".format(locIds))


if __name__ == "__main__":
    initDB()
    log.debug("Init DAta")
    popData.init_data()
    #calculateYield("1 Avon Road")
