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
SINKURL = "mysql://chuser@localhost/pushSink"
SOURCEURL = "mysql://chuser@localhost/pushSource"

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
        

        

    def test_sensortypes(self):
        source = sourcesession()
        sink = sinksession()

        # #And remove from both

        #Check the sensor types match at the start

        source_data = source.query(models.SensorType).order_by(models.SensorType.id).all()
        sink_data = sink.query(models.SensorType).order_by(models.SensorType.id).all()
        self.assertEqual(source_data,sink_data)
        
        #What we want to to is test the syncList
        out = self.thePusher.syncSensorTypes()
        #print "-- OUT {0}".format(out)

        #Now Add a new Sensor to the Local DB
        localSensor = models.SensorType(id=1000,name="TEST")
        source.add(localSensor)
        source.flush()
        source.commit()

        #What we want to to is test the syncList
        out = self.thePusher.syncSensorTypes()
        #print "-- OUT {0}".format(out)

        source = sourcesession()
        sink = sinksession()
        source_data = source.query(models.SensorType).order_by(models.SensorType.id).all()
        sink_data = sink.query(models.SensorType).order_by(models.SensorType.id).all()
        self.assertEqual(source_data,sink_data)

        #------------------------- AND SYNC REMOTE SIDE --------------------------

        #Now Add a new Sensor to the Local DB
        localSensor = models.SensorType(id=1001,name="TEST_TWO")
        sink.add(localSensor)
        sink.flush()
        sink.commit()

        #What we want to to is test the syncList
        out = self.thePusher.syncSensorTypes()
        #print "-- OUT {0}".format(out)

        source = sourcesession()
        sink = sinksession()
        source_data = source.query(models.SensorType).order_by(models.SensorType.id).all()
        sink_data = sink.query(models.SensorType).order_by(models.SensorType.id).all()
        self.assertEqual(source_data,sink_data)        

        

        #And remove from both
        print "Cleaning Up"
        raw_input("Press Any Key to remove added items")
        source_data = source.query(models.SensorType).filter(models.SensorType.id>=1000).delete()
        sink_data = sink.query(models.SensorType).filter(models.SensorType.id>=1000).delete()

        #Final Flush and commit
        source.flush()
        source.commit()
        
        sink.flush()
        sink.commit()
        

