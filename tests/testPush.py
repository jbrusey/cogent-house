"""
Testing for the Deployment Module

:author: Dan Goldsmith <djgoldsmith@googlemail.com>
"""

"""

"""

#Python Library Imports
import unittest
import datetime

#Python Module Imports
from sqlalchemy import create_engine
import sqlalchemy.exc

import testmeta

models = testmeta.models

#from cogent.push import remoteModels as remoteModels
import cogent.push.Pusher as Pusher

REMOTE_URL = "sqlite:///remote.db"
LOCAL_URL = "sqlite:///test.db"

class TestPush(testmeta.BaseTestCase):
    """Test the Push Functionality.

    For the moment I think we need to overload the standard setup, teardown methods
    Otherwise we will not be able to make any changes to the database

    """

    @classmethod
    def setUpClass(self):
        """Called the First time this class is called.
        This means that we can Init the testing database once per testsuite
        
        We need to override the standard class here, as we also want to create a Remote
        database connection.
        """

        #This is a little bit hackey, but it works quite nicely at the moment.
        #Basically creates an empty remote database that we can connect to.

        #As well as the Push we want to create a direct connection to the remote database
        #This means we can query to ensure the output from each is the same
        engine = create_engine(REMOTE_URL)
        models.initialise_sql(engine)
        remoteSession = sqlalchemy.orm.sessionmaker(bind=engine)
        self.remoteSession = remoteSession
        self.engine = engine

        self.remoteEngine = sqlalchemy.create_engine(REMOTE_URL)
        self.localEngine =  sqlalchemy.create_engine(LOCAL_URL)


         #push.testRemoteQuery()
         #push.testLocalQuery()
        

        #What is pretty cool is the idea we can also  recreate the database to clean it out each time
        #models.initialise_sql(self.engine,True)

    # def testSetup(self):
    #     print "Testing setup or remote and local database"
    #     #Query from local database
    #     localSession = testmeta.Session()
    #     remoteSession = self.remoteSession()

    #     print "Querying Local"
    #     theQry = localSession.query(models.RoomType)
    #     for item in theQry:
    #         print "--> {0}".format(item)

    #     print "Query Remote"
    #     theQry = remoteSession.query(models.RoomType)
    #     for item in theQry:
    #         print "--> {0}".format(item)
            
    def testRemoteDirect(self):
        """Test to see if making a direct connection to the remote database returns what we expect"""
        push = Pusher.Pusher()

        #Initalise Connections
        push.init_remote(self.remoteEngine)

        #Do we get the same items come back from the database
        #For the Remote
        remotePush = push.testRemoteQuery()
        session = self.remoteSession()
        remoteData = session.query(models.RoomType).all()
        self.assertEqual(remotePush,remoteData)


    def testLocalDirect(self):
        """Test to see if making a direct connection to the local database returns what we expect"""

        push = Pusher.Pusher()

        push.init_local(self.localEngine)
        #Do we get the same items come back from the database
        #For the Remote
        remotePush = push.testLocalQuery()
        session =testmeta.Session()
        remoteData = session.query(models.RoomType).all()
        self.assertEqual(remotePush,remoteData)        


        


        

    def testConnection(self):
        """Can we connect to remote databases with various strings"""
        pass

    def testFullTransfer(self):
        """Can we transfer everything across"""
        pass

    

    


if __name__ == "__main__":
    unittest.main()
