"""
Testing Code for the Push Script


This expects two databases to be available.

1) Clean version of the database "pushSink" installed as per the webinterface
2) Version of the database "pushSource" installed and populated using the populate data script

"""

#Python Library Imports
import unittest
from datetime import datetime, timedelta

import sqlalchemy
import cogent
import cogent.base.model as models
import cogent.base.model.meta as meta

import RestPusher

#ENGINE URLS
#SINKURL = "mysql://chuser@localhost/pushSink"
#SOURCEURL = "mysql://chuser@localhost/pushSource"
SINKURL = "sqlite://"
SOURCEURL = "sqlite://"

#Create our engines
sinkengine = sqlalchemy.create_engine(SINKURL)
sinksession = sqlalchemy.orm.sessionmaker(bind=sinkengine)

sourceengine = sqlalchemy.create_engine(SOURCEURL)
sourcesession = sqlalchemy.orm.sessionmaker(bind=sourceengine)


import logging
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(name)-10s %(levelname)-8s %(message)s",
                    datefmt = "%m-%d-%Y %H:%M",
                    )



class TestPush(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        """Check the setup works and that everything is how we expect it to be"""

        #Create a Push Server

        theServer = RestPusher.PushServer()
        print theServer

        #Hack to get the Pusher Object
        thePusher = theServer.syncList[0]
        print thePusher
        self.thePusher = thePusher
        
#     @unittest.skip
#     def test_sensortypes(self):
#         source = sourcesession()
#         sink = sinksession()

#         # #And remove from both

#         #Check the sensor types match at the start

#         source_data = source.query(models.SensorType).order_by(models.SensorType.id).all()
#         sink_data = sink.query(models.SensorType).order_by(models.SensorType.id).all()
#         self.assertEqual(source_data,sink_data)
        
#         #What we want to to is test the syncList
#         out = self.thePusher.syncSensorTypes()
#         #print "-- OUT {0}".format(out)

#         #Now Add a new Sensor to the Local DB
#         localSensor = models.SensorType(id=1000,name="TEST")
#         source.add(localSensor)
#         source.flush()
#         source.commit()

#         #What we want to to is test the syncList
#         out = self.thePusher.syncSensorTypes()
#         #print "-- OUT {0}".format(out)

#         source = sourcesession()
#         sink = sinksession()
#         source_data = source.query(models.SensorType).order_by(models.SensorType.id).all()
#         sink_data = sink.query(models.SensorType).order_by(models.SensorType.id).all()
#         self.assertEqual(source_data,sink_data)

#         #------------------------- AND SYNC REMOTE SIDE --------------------------

#         #Now Add a new Sensor to the Local DB
#         localSensor = models.SensorType(id=1001,name="TEST_TWO")
#         sink.add(localSensor)
#         sink.flush()
#         sink.commit()

#         #What we want to to is test the syncList
#         out = self.thePusher.syncSensorTypes()
#         #print "-- OUT {0}".format(out)

#         source = sourcesession()
#         sink = sinksession()
#         source_data = source.query(models.SensorType).order_by(models.SensorType.id).all()
#         sink_data = sink.query(models.SensorType).order_by(models.SensorType.id).all()
#         self.assertEqual(source_data,sink_data)        

        

#         #And remove from both
#         print "Cleaning Up"
#         raw_input("Press Any Key to remove added items")
#         source_data = source.query(models.SensorType).filter(models.SensorType.id>=1000).delete()
#         sink_data = sink.query(models.SensorType).filter(models.SensorType.id>=1000).delete()

#         #Final Flush and commit
#         source.flush()
#         source.commit()
        
#         sink.flush()
#         sink.commit()
        
#     @unittest.skip
#     def testRoomTypes(self):
#         """And Syncing room types"""
#         source = sourcesession()
#         sink = sinksession()

#         # #And remove from both
#         source_data = source.query(models.RoomType).filter(models.RoomType.id>=6).delete()
#         sink_data = sink.query(models.RoomType).filter(models.RoomType.id>=6).delete()

#         #Final Flush and commit
#         source.flush()
#         source.commit()
        
#         sink.flush()
#         sink.commit()
#         #Check the sensor types match at the start

#         source_data = source.query(models.RoomType).order_by(models.RoomType.id).all()
#         sink_data = sink.query(models.RoomType).order_by(models.RoomType.id).all()
#         self.assertEqual(source_data,sink_data)
        
#         out = self.thePusher.syncRoomTypes()        

#         #return
#         #Now Add a new Sensor to the Local DB
#         localSensor = models.RoomType(id=1000,name="TEST")
#         source.add(localSensor)
#         source.flush()
#         source.commit()

#         out = self.thePusher.syncRoomTypes()
#         #print "-- OUT {0}".format(out)

#         source = sourcesession()
#         sink = sinksession()
#         source_data = source.query(models.RoomType.name).order_by(models.RoomType.id).all()
#         sink_data = sink.query(models.RoomType.name).order_by(models.RoomType.id).all()
        
#         self.assertEqual(source_data,sink_data)        

#         #Now Add a new Sensor to the Remote DB
#         localSensor = models.RoomType(id=1001,name="TEST_TWO")
#         sink.add(localSensor)
#         sink.flush()
#         sink.commit()

#         out = self.thePusher.syncRoomTypes()
#         #print "-- OUT {0}".format(out)

#         source = sourcesession()
#         sink = sinksession()
#         source_data = source.query(models.RoomType.name).order_by(models.RoomType.id).all()
#         sink_data = sink.query(models.RoomType.name).order_by(models.RoomType.id).all()
#         self.assertEqual(source_data,sink_data)        

#         print "Cleaning Up"
#         raw_input("Press Any Key to remove added items")
#         source_data = source.query(models.RoomType).filter(models.RoomType.id>=6).delete()
#         sink_data = sink.query(models.RoomType).filter(models.RoomType.id>=6).delete()

#         #Final Flush and commit
#         source.flush()
#         source.commit()
        
#         sink.flush()
#         sink.commit()

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
