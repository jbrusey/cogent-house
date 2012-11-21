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
THEDB = "mysql://chuser:foobar@127.0.0.1/transferStore"


def initDB():
    log.debug("Connecting to database")

    engine = sqlalchemy.create_engine(THEDB)
    meta.Session.configure(bind=engine)
    meta.Base.metadata.bind = engine
    meta.Base.metadata.create_all(engine)


    #popData.init_data()

