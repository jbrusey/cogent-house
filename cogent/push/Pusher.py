import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

import sqlalchemy
import remoteModels

import cogent
import cogent.base.model as models
import cogent.base.model.meta as meta
#RemoteSession = sqlalchemy.orm.sessionmaker()
#RemoteMetadata = sqlalchemy.MetaData()

class Pusher(object):
    """Class to push updates to a remote database"""
    def __init__(self):
        pass

    def init_remote(self,engine):
        """Intialise a connection to the database and reflect all Remote Tables

        :param engine: Engine to use for this connection
        """
        log.debug("Initalising Remote Engine")
        RemoteSession = sqlalchemy.orm.sessionmaker()
        RemoteSession.configure(bind=engine)
        RemoteMetadata = sqlalchemy.MetaData()
        
        
        log.debug("Reflecting Remote Tables")
        remoteModels.reflectTables(engine,RemoteMetadata)
        self.RemoteSession=RemoteSession

    def init_local(self,engine):
        """Initalise a local connection"""
        log.debug("Initialising Local Engine")
        models.initialise_sql(engine)
        LocalSession = sqlalchemy.orm.sessionmaker(bind=engine)
        self.LocalSession = LocalSession


    def testRemoteQuery(self):
        """
        Run a test Query for Room Types on the Remote Database
        """
        session = self.RemoteSession()
        theQry = session.query(remoteModels.RemoteRoomType)
        return theQry.all()

    def testLocalQuery(self):
        """
        Test Query of Local Database
        """
        session = self.LocalSession()
        #log.debug("Query Room Type")
        theQry = session.query(models.RoomType)
        return theQry.all()
        #for item in theQry:
        #    log.debug("--> {0}".format(item))



if __name__ == "__main__":
    logging.debug("Testing Push Classes")
    
    
    remoteEngine = sqlalchemy.create_engine("sqlite:///remote.db")
    localEngine =  sqlalchemy.create_engine("sqlite:///test.db")

    push = Pusher()
    push.init_remote(remoteEngine)
    push.init_local(localEngine)
    push.testRemoteQuery()
    push.testLocalQuery()
    pass
