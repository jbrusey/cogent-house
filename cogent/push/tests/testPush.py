"""
Testing Code for the Push Script

Testing this gets a little complex as it relies on external modules.
So there is a little bit of legwork requried to get everything up and running

Database Setup
---------------

This expects two databases to be available.

1) Clean version of the database "pushSink" installed as per the webinterface
2) Version of the database "pushSource" installed and populated using the populate data script

Webserver Setup
----------------

* Create an instance of the webserver that is connected to the pushSink database. (test.ini)

Push Script Setup
------------------

* Make sure the config file points towards the test Server
* Remove any test_map.conf files

"""

#Python Library Imports
import unittest
from datetime import datetime, timedelta

import logging
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(name)-10s %(levelname)-8s %(message)s",
                    datefmt = "%m-%d-%Y %H:%M",
                    )


import sqlalchemy

import cogent
import cogent.base.model as models
import cogent.base.model.meta as meta
import cogent.base.model.populateData as populateData
import cogent.push.RestPusher as RestPusher

BASE = meta.Base

#ENGINE URLS
SINKURL = "mysql://chuser@localhost/pushSink"
SOURCEURL = "mysql://chuser@localhost/pushSource"
#SINKURL = "sqlite:///sink_test.db"
#SOURCEURL = "sqlite:///source_test.db"


class TestPush(unittest.TestCase):
   
    @classmethod
    def setUpClass(self):
        """Check the setup works and that everything is how we expect it to be"""

        log = logging.getLogger("Test Push")
        """Create some database engines for testing"""
        logging.debug("Creating Engines")

        #Create our engines
        logging.debug("-> Sink Engine")

        sinkengine = sqlalchemy.create_engine(SINKURL)
        sinksession = sqlalchemy.orm.sessionmaker(bind=sinkengine)
        models.init_model(sinkengine)
        #Create Tables
        logging.debug("--> Creating Tables")
        BASE.metadata.create_all(sinkengine)
        logging.debug("--> Initialising Data")
        session = sinksession()
        populateData.init_data(session)
        session.commit()

        logging.debug("-> Source Engine")
        sourceengine = sqlalchemy.create_engine(SOURCEURL)
        sourcesession = sqlalchemy.orm.sessionmaker(bind=sourceengine)
        models.init_model(sourceengine)
        #Create Tables
        logging.debug("--> Creating Tables")
        BASE.metadata.create_all(sourceengine)
        logging.debug("--> Initialising Data")
        session = sourcesession()
        populateData.init_data(session)
        session.commit()

        logging.debug("Engines Created")
    
        self.log = log
        self.sourcesession = sourcesession
        self.sinksession = sinksession

        #Create a Push Server
        theServer = RestPusher.PushServer(SOURCEURL)
        log.info("Test Server is {0}".format(theServer))

        #Hack to get the Pusher Object
        thePusher = theServer.syncList[0]
        log.info("Test Pusher is {0}".format(thePusher))
        self.thePusher = thePusher


    @unittest.skip
    def test_sensortypes(self):
        """Test Sync Of Sensor Types"""
        source = self.sourcesession()
        sink = self.sinksession()
        log = self.log

        #Check the sensor types match at the start
        localSensor = models.SensorType(id=1000,name="TEST")

        source_data = source.query(models.SensorType).order_by(models.SensorType.id).all()
        sink_data = sink.query(models.SensorType).order_by(models.SensorType.id).all()
        self.assertEqual(source_data,sink_data)
        
        #What we want to to is test the syncList
        out = self.thePusher.syncSensorTypes()
        log.info("-- OUT {0}".format(out))

        self.assertTrue(out)

        #Nothing should have changed
        source_data = source.query(models.SensorType).order_by(models.SensorType.id).all()
        sink_data = sink.query(models.SensorType).order_by(models.SensorType.id).all()
        self.assertEqual(source_data,sink_data)

        # ----------------------------------------------------------

        #Now Add a new Sensor to the Local DB
        localSensor = models.SensorType(id=1000,name="TEST")
        source.add(localSensor)
        source.flush()
        source.commit()

        source = self.sourcesession()
        theQry = source.query(models.SensorType).filter_by(id=1000).first()
        log.debug("=== QRY {0}".format(theQry))

        #What we want to to is test the syncList
        log.debug("---> Synchronising Data")
        out = self.thePusher.syncSensorTypes()
        log.info("-- OUT {0}".format(out))

        #And Also fetch that particular sensor
        sink = self.sinksession()
        sinkSensor = sink.query(models.SensorType).filter_by(id = 1000).first()
        log.debug("Sink Sensor {0}".format(sinkSensor))
        self.assertEqual(sinkSensor,localSensor)

        #------------------------- AND SYNC REMOTE SIDE --------------------------

        #Now Add a new Sensor to the Local DB
        localSensor = models.SensorType(id=1001,name="TEST_TWO")
        sink.add(localSensor)
        sink.flush()
        sink.commit()

        #What we want to to is test the syncList
        out = self.thePusher.syncSensorTypes()
        #print "-- OUT {0}".format(out)

        source = self.sourcesession()
        sink = self.sinksession()
        source_data = source.query(models.SensorType).order_by(models.SensorType.id).all()
        sink_data = sink.query(models.SensorType).order_by(models.SensorType.id).all()
        self.assertEqual(source_data,sink_data)        

        log.debug("--> Cleaning Up")
        source_data = source.query(models.SensorType).filter(models.SensorType.id>=1000).delete()
        sink_data = sink.query(models.SensorType).filter(models.SensorType.id>=1000).delete()

        #Final Flush and commit
        source.flush()
        source.commit()
        
        sink.flush()
        sink.commit()
        
    @unittest.skip
    def testRoomTypes(self):
        """And Syncing room types"""
        source = self.sourcesession()
        sink = self.sinksession()

        #Check the sensor types match at the start
        source_data = source.query(models.RoomType).all()
        sink_data = sink.query(models.RoomType).all()

        self.assertEqual(source_data, sink_data)
        out = self.thePusher.syncRoomTypes()        
       
        #Now Add a new Sensor to the Local DB
        localItem = models.RoomType(id=1000,name="TEST")
        source.add(localItem)
        source.flush()
        source.commit()

        out = self.thePusher.syncRoomTypes()

        source = self.sourcesession()
        sink = self.sinksession()
        
        #Check this is in the sink
        theQry = sink.query(models.RoomType).filter_by(name="TEST").first()
        self.assertEqual(theQry,localItem)

        #Now Add a new Sensor to the Remote DB
        remoteItem = models.RoomType(id=1001,name="TEST_TWO")
        sink.add(remoteItem)
        sink.flush()
        sink.commit()

        out = self.thePusher.syncRoomTypes()

        source = self.sourcesession()
        sink = self.sinksession()

        theQry = source.query(models.RoomType).filter_by(name="TEST_TWO").first()
        self.assertEqual(theQry,remoteItem)

        self.log.debug("--> Cleaning up")
        source_data = source.query(models.RoomType).filter(models.RoomType.id>=5).delete()
        sink_data = sink.query(models.RoomType).filter(models.RoomType.id>=5).delete()

        #Final Flush and commit
        source.flush()
        source.commit()
        sink.flush()
        sink.commit()


    #@unittest.skip
    def testRoom(self):
        """And Syncing room types"""
        
        #We need to sync room types so the Ids work properly
        self.thePusher.syncRoomTypes()    

        source = self.sourcesession()
        sink = self.sinksession()


        source_data = source.query(models.Room).filter(models.Room.id>=13).delete()
        sink_data = sink.query(models.Room).filter(models.Room.id>=13).delete()

        #Final Flush and commit
        source.flush()
        source.commit()
        sink.flush()
        sink.commit()

        source = self.sourcesession()
        sink = self.sinksession()

        #Check the sensor types match at the start
        source_data = source.query(models.Room).all()
        sink_data = sink.query(models.Room).all()

        self.assertEqual(source_data, sink_data)

        out = self.thePusher.syncRooms()        
        
        #Now Add a new Sensor to the Local DB
        localItem = models.Room(id=1000, roomTypeId = 1, name="TEST")
        source.add(localItem)
        source.flush()
        source.commit()

        self.log.debug("== Local Item is {0}".format(localItem))
        out = self.thePusher.syncRooms()

        source = self.sourcesession()
        sink = self.sinksession()
        
        #Check this is in the sink
        theQry = sink.query(models.Room).filter_by(name="TEST").first()
        self.log.debug("-- Local, {0} Remote {1}".format(localItem,theQry))
        self.assertEqual(theQry,localItem)

        #Now Add a new Sensor to the Remote DB
        remoteItem = models.Room(id=1001, name="TEST_TWO", roomTypeId=2)
        sink.add(remoteItem)
        sink.flush()
        sink.commit()

        out = self.thePusher.syncRooms()

        source = self.sourcesession()
        sink = self.sinksession()

        theQry = source.query(models.Room).filter_by(name="TEST_TWO").first()
        self.assertEqual(theQry,remoteItem)

        self.log.debug("--> Cleaning up")
        source_data = source.query(models.RoomType).filter(models.RoomType.id>=13).delete()
        sink_data = sink.query(models.RoomType).filter(models.RoomType.id>=13).delete()

        #Final Flush and commit
        source.flush()
        source.commit()
        sink.flush()
        sink.commit()

#     @unittest.skip
#     def testSyncRooms(self):
#         #Sync Rooms
#         out = self.thePusher.syncRoomTypes()

#         source = sourcesession()
#         sink = sinksession()
        
#         source_data = source.query(models.Room).filter(models.Room.id>13).delete()
#         sink_data = sink.query(models.Room).filter(models.Room.id>13).delete()

#         source_data = source.query(models.Room).order_by(models.Room.id).all()
#         sink_data = sink.query(models.Room).order_by(models.Room.id).all()
#         self.assertEqual(source_data,sink_data)

#         #Add a new room to the Remote DB
#         newRoom = models.Room(id=15,name="TEST ROOM",roomTypeId=1)
#         source.add(newRoom)
#         source.flush()
#         source.commit()
#         sink.flush()
#         sink.commit()
#         out = self.thePusher.syncRooms()

#         source_data = source.query(models.Room.name).order_by(models.Room.name).all()
#         sink_data = sink.query(models.Room.name).order_by(models.Room.name).all()
#         self.assertEqual(source_data,sink_data)

#         newRoom = models.Room(id=15,name="TEST TWO",roomTypeId=2)
#         sink.add(newRoom)
#         source.flush()
#         source.commit()
#         sink.flush()
#         sink.commit()
#         out = self.thePusher.syncRooms()

#         source_data = source.query(models.Room.name).order_by(models.Room.name).all()
#         sink_data = sink.query(models.Room.name).order_by(models.Room.name).all()
#         self.assertEqual(source_data,sink_data)

#         raw_input("Press Any Key to remove added items")
#         source_data = source.query(models.Room).filter(models.Room.id>13).delete()
#         sink_data = sink.query(models.Room).filter(models.Room.id>13).delete()
#         source.flush()
#         source.commit()
#         sink.flush()
#         sink.commit()


#     def testSyncDeployments(self):
#         """Syncronise Deployments"""

#         #We need to do the original sync
#         out = self.thePusher.syncDeployments()

#         source = sourcesession()
#         sink = sinksession()

#         source_data = source.query(models.Deployment).filter(models.Deployment.id>1).delete()
#         sink_data = sink.query(models.Deployment).filter(models.Deployment.id>1).delete()
#         source.flush()
#         sink.flush()


#         #Add a new deployment to the Source
#         newDep = models.Deployment(id=2,name="TEST")
#         source.add(newDep)
#         source.flush()
        
#         source.commit()
#         sink.commit()

#         out = self.thePusher.syncDeployments()

#         #Check it exists
#         source_data = source.query(models.Deployment.name).order_by(models.Deployment.name).all()
#         sink_data = sink.query(models.Deployment.name).order_by(models.Deployment.name).all()
        
#         self.assertEqual(source_data,sink_data)
        

#         #And do the same the other way
#         newDep = models.Deployment(id=5,name="TEST2")
#         sink.add(newDep)
#         sink.flush()

#         source.commit()
#         sink.commit()

#         out = self.thePusher.syncDeployments()

#         #Check it exists
#         source_data = source.query(models.Deployment.name).order_by(models.Deployment.name).all()
#         sink_data = sink.query(models.Deployment.name).order_by(models.Deployment.name).all()
        
#         self.assertEqual(source_data,sink_data)

#         #And a two way Sync
#         newDep = models.Deployment(name="TEST3")
#         source.add(newDep)
#         newDep = models.Deployment(name="TEST4")
#         sink.add(newDep)

#         source.flush()
#         sink.flush()
#         source.commit()
#         sink.commit()

#         out = self.thePusher.syncDeployments()

#         #Check it exists
#         source_data = source.query(models.Deployment.name).order_by(models.Deployment.name).all()
#         sink_data = sink.query(models.Deployment.name).order_by(models.Deployment.name).all()
        
#         self.assertEqual(source_data,sink_data)


#         raw_input("Press abny key to reset")
#         source_data = source.query(models.Deployment).filter(models.Deployment.id>1).delete()
#         sink_data = sink.query(models.Deployment).filter(models.Deployment.id>1).delete()
#         source.flush()
#         sink.flush()
#         source.commit()
#         sink.commit()
