import unittest
import datetime
from Queue import Queue

import logging
logging.basicConfig(level=logging.DEBUG)

import cogent.base.BaseLogger as BaseLogger
import cogent.base.model.Bitset as Bitset
from cogent.node import StateMsg, StateV1Msg, ConfigMsg, Packets
import cogent.base.model as models

import base

#Note: MoteIF doesn't currently support coming directly off the serial
#interface. So we create a fake BIF
class TestBif(object):
    def __init__(self):
        self.queue = Queue()
		
    def receive(self, msg):
        self.queue.put(msg)

    def sendMsg(self, msg):
        # assumption is that msg is a ConfigMsg
        print "sendMsg",msg

    def finishAll(self):
        pass


def setuptestingDB(session):
    """Setup a testing database"""

    #Remove stuff from Node    session.execute("DELETE FROM Node")
    session.execute("DELETE FROM NodeState")
    session.execute("DELETE FROM Reading")
    session.execute("DELETE FROM SensorType")
    session.flush()
    session.commit()
    #foo = models.Node(id=400)
    #session.insert(foo)
    #session.flush()
    #session.commit()
        
    pass

class test_baselogger(base.BaseTestCase):
    """Test Cases for BaseLogger"""

    #As we dont want to have several Base Loggers knocking around
    @classmethod 
    def setUpClass(cls):
        #Inherit from Base
        super(test_baselogger, cls).setUpClass()

        #Create a baseIF
        print "Creating BaseLogger"
        testbif = TestBif()
        blogger = BaseLogger.BaseLogger(bif=testbif,
                                        dbfile="sqlite:///test.db")

        blogger.create_tables()
        blogger.log.setLevel(logging.DEBUG)
        cls.testbif = testbif
        cls.blogger = blogger

        #One that doesnt get wrapped in a transaction
        #session = cls.Session()
        #setuptestingDB(session)

        #Remove Delta Temperature sensor type for a specific test
        session = cls.Session()
        qry = session.query(models.SensorType).filter_by(id=1)
        qry.delete()
        session.flush()
        session.commit()


    def setUp(self):
        #Clean up the database before each run
        session = self.Session()
        session.execute("DELETE FROM Node")
        session.execute("DELETE FROM NodeState")
        session.execute("DELETE FROM Reading")
        session.flush()
        thenode = models.Node(id=4242)
        session.add(thenode)
        session.commit()

    def tearDown(self):
        """Overload to stop the transaction magic"""
        pass

    #@classmethod
    #def tearDownClass(cls):
    #    print "Tearing Down BIF"
    #    pass

    #@unittest.skip
    def test_nodata(self):
        """Check what happens if we have no data recieved from the bif"""
        output = self.blogger.mainloop()
        self.assertFalse(output)
    
    #@unittest.skip
    def testFailOnSpecial(self):
        """Do We fail gracefully if Special is wrong"""
        bs = Bitset(size=Packets.SC_SIZE)
        #Try to setup a temperature sample
        bs[Packets.SC_TEMPERATURE] = True

        #Then A packet
        packet = StateMsg(addr=4242)        
        packet.set_ctp_parent_id(101) #Parent Node Id
        #packet.set_special(0xc7) #Special Id

        packet.set_packed_state_mask(bs.a)
        packet.set_packed_state([22.5])

        #The First thing is to see if the code passes nicely (ie no fail)
        #When run in the normal way
        self.testbif.receive(packet)
        output = self.blogger.mainloop()
        self.assertIsNone(output) #Only when we store return True

        with self.assertRaises(Exception): 
            self.blogger.store_state(packet)        

    #@unittest.skip
    def testStore(self):
        """Store State without queuing"""
        now = datetime.datetime.now()
        #Create our bitmask
        bs = Bitset(size=Packets.SC_SIZE)
        #Try to setup a temperature sample
        bs[Packets.SC_TEMPERATURE] = True

        #Then A packet
        packet = StateMsg(addr=4242)        
        packet.set_ctp_parent_id(101) #Parent Node Id
        packet.set_special(0xc7) #Special Id

        packet.set_packed_state_mask(bs.a)
        packet.set_packed_state([22.5])

        self.blogger.store_state(packet)

        #Check the reading turns up
        session = self.Session()
        qry = session.query(models.Node).filter_by(id=4242).first()
        self.assertTrue(qry)

        #NodeState
        qry = session.query(models.NodeState).filter_by(nodeId=4242)
        self.assertEqual(qry.count(), 1)
        qry = qry.first()
        self.assertTrue(qry)
        tdiff = qry.time - now
        self.assertLess(tdiff.seconds, 1.0)
        self.assertEqual(qry.parent, 101)
        
        #And Reading
        qry = session.query(models.Reading).filter_by(nodeId=4242)
        #As we just did temperature there should only be one reading
        self.assertEqual(qry.count(), 1)
        qry = qry.first()
        self.assertTrue(qry)
        self.assertEqual(qry.typeId, 0)
        self.assertEqual(qry.value, 22.5)     

    #@unittest.skip
    def testRcv(self):
        """Test a single receive"""
        now = datetime.datetime.now()

        #Create our bitmask
        bs = Bitset(size=Packets.SC_SIZE)
        #Try to setup a temperature sample
        bs[Packets.SC_TEMPERATURE] = True

        #Then A packet
        packet = StateMsg(addr=4242)        
        packet.set_ctp_parent_id(101) #Parent Node Id
        packet.set_special(0xc7) #Special Id

        packet.set_packed_state_mask(bs.a)
        packet.set_packed_state([22.5])

        self.testbif.receive(packet)
        output = self.blogger.mainloop()
        self.assertTrue(output)

        #Check the reading turns up
        session = self.Session()
        qry = session.query(models.Node).filter_by(id=4242).first()
        self.assertTrue(qry)

        #NodeState
        qry = session.query(models.NodeState).filter_by(nodeId=4242)
        self.assertEqual(qry.count(), 1)
        qry = qry.first()
        self.assertTrue(qry)
        tdiff = qry.time - now
        self.assertLess(tdiff.seconds, 1.0)
        self.assertEqual(qry.parent, 101)
        
        #And Reading
        qry = session.query(models.Reading).filter_by(nodeId=4242)
        #As we just did temperature there should only be one reading
        self.assertEqual(qry.count(), 1)
        qry = qry.first()
        self.assertTrue(qry)
        self.assertEqual(qry.typeId, 0)
        self.assertEqual(qry.value, 22.5)        

    #@unittest.skip
    def test_Rcv_Node(self):
        """Does Recieve work when that node is not in the DB"""

        now = datetime.datetime.now()

        #Create our bitmask
        bs = Bitset(size=Packets.SC_SIZE)
        #Try to setup a temperature sample
        bs[Packets.SC_TEMPERATURE] = True

        #Then A packet
        packet = StateMsg(addr=100)        
        packet.set_ctp_parent_id(101) #Parent Node Id
        packet.set_special(0xc7) #Special Id

        packet.set_packed_state_mask(bs.a)
        packet.set_packed_state([22.5])

        self.testbif.receive(packet)
        output = self.blogger.mainloop()
        self.assertTrue(output)

        #Check stuff gets added to the database correctly
        session = self.Session()
        #Has a node been added to the DB
        qry = session.query(models.Node).filter_by(id=100).first()
        self.assertTrue(qry)

        #NodeState
        qry = session.query(models.NodeState).filter_by(nodeId=100)
        self.assertEqual(qry.count(), 1)
        qry = qry.first()
        self.assertTrue(qry)
        tdiff = qry.time - now
        self.assertLess(tdiff.seconds, 1.0)
        self.assertEqual(qry.parent, 101)
        
        #And Reading
        qry = session.query(models.Reading).filter_by(nodeId=100)
        #As we just did temperature there should only be one reading
        self.assertEqual(qry.count(), 1)
        qry = qry.first()
        self.assertTrue(qry)
        self.assertEqual(qry.typeId, 0)
        self.assertEqual(qry.value, 22.5)


    #@unittest.skip
    def test_Rcv_Sensor(self):
        """Does Recieve work when that sensortype is not in the DB"""

        now = datetime.datetime.now()
        #Create our bitmask
        bs = Bitset(size=Packets.SC_SIZE)
        #Try to setup a temperature sample
        bs[Packets.SC_D_TEMPERATURE] = True

        #Then A packet
        packet = StateMsg(addr=4242)        
        packet.set_ctp_parent_id(101) #Parent Node Id
        packet.set_special(0xc7) #Special Id

        packet.set_packed_state_mask(bs.a)
        packet.set_packed_state([22.5])

        self.testbif.receive(packet)
        output = self.blogger.mainloop()
        self.assertTrue(output)

        #Check stuff gets added to the database correctly
        session = self.Session()

        #Does the sensortype exist now (Apparently its not a FK in Reading)
        #qry = session.query(models.SensorType).filter_by(id=1).first()
        #self.assertTrue(qry)
        #Is the name UNKNOWN
        #self.assertEqual(qry.Name, "UNKNOWN")
        

        #NodeState
        qry = session.query(models.NodeState).filter_by(nodeId=4242)
        self.assertEqual(qry.count(), 1)
        qry = qry.first()
        self.assertTrue(qry)
        tdiff = qry.time - now
        self.assertLess(tdiff.seconds, 1.0)
        self.assertEqual(qry.parent, 101)
        
        #And Reading
        qry = session.query(models.Reading).filter_by(nodeId=4242)
        #As we just did temperature there should only be one reading
        self.assertEqual(qry.count(), 1)
        qry = qry.first()
        self.assertTrue(qry)
        self.assertEqual(qry.typeId, 1)
        self.assertEqual(qry.value, 22.5)

        #Reset the sensor type to be as it should
        qry = session.query(models.SensorType).filter_by(id=1).first()
        if qry is None:
            qry = models.SensorType(id=1)
            session.add(qry)

        qry.name = "Delta Temperature"
        qry.code = "dT"
        qry.units = "deg.C/s"
        #session.flush()
        #session.commit()

    #@unittest.skip        
    def testDuplicate(self):
        """What about duplicate packets"""
        now = datetime.datetime.now()

        #Create our bitmask
        bs = Bitset(size=Packets.SC_SIZE)
        #Try to setup a temperature sample
        bs[Packets.SC_TEMPERATURE] = True

        #Then A packet
        packet = StateMsg(addr=4242)        
        packet.set_ctp_parent_id(101) #Parent Node Id
        packet.set_special(0xc7) #Special Id

        packet.set_packed_state_mask(bs.a)
        packet.set_packed_state([22.5])

        self.testbif.receive(packet) 
        self.testbif.receive(packet) #Add it twice
        output = self.blogger.mainloop()
        self.assertTrue(output)         
        output = self.blogger.mainloop() #And a duplicate
        self.assertTrue(output)          


    def testDuplicateFunction(self):
        """Test the duplicate packet function"""


        #Create our bitmask
        bs = Bitset(size=Packets.SC_SIZE)
        #Try to setup a temperature sample
        bs[Packets.SC_TEMPERATURE] = True

        #Then A packet
        packet = StateMsg(addr=4242)        
        packet.set_ctp_parent_id(101) #Parent Node Id
        packet.set_special(0xc7) #Special Id

        packet.set_packed_state_mask(bs.a)
        packet.set_packed_state([22.5])

        #Store the initial packet
        self.testbif.receive(packet) 
        output = self.blogger.mainloop()
        self.assertTrue(output)  

        now = datetime.datetime.now()
        #Check the duplicate function
        
        #session = self.blogger.getSession()
        session = self.Session()
        out = self.blogger.duplicate_packet(session = session,
                                            time = now,
                                            nodeId = 4242,
                                            localtime = 0)
        self.assertTrue(out)

        now = now+datetime.timedelta(minutes=1)
        out = self.blogger.duplicate_packet(session = session,
                                            time = now,
                                            nodeId = 4242,
                                            localtime = 0)
        self.assertFalse(out)

    #@unittest.skip
    def testrecvCombined(self):
        """Can we correctly recieve and packets with multiple readings"""
        now = datetime.datetime.now()

        #Create our bitmask
        bs = Bitset(size=Packets.SC_SIZE)
        #Try to setup a temperature sample
        bs[Packets.SC_TEMPERATURE] = True
        bs[Packets.SC_HUMIDITY] = True
        bs[Packets.SC_VOLTAGE] = True

        #Then A packet
        packet = StateMsg(addr=100)        
        packet.set_ctp_parent_id(101) #Parent Node Id
        packet.set_special(0xc7) #Special Id

        packet.set_packed_state_mask(bs.a)
        packet.set_packed_state([22.5,50.0,2.45])

        self.testbif.receive(packet)
        output = self.blogger.mainloop()
        self.assertTrue(output)


        #And check the data has arrived
        session = self.Session()
        qry = session.query(models.NodeState)
        #self.assertEqual(qry.count(), 1)
        qry = qry.first()
        self.assertEqual(qry.nodeId, 100)
        self.assertEqual(qry.parent, 101)

        #Do we get the temperature reading
        qry = session.query(models.Reading).filter_by(typeId = 0)
        #self.assertEqual(qry.count(), 1)
        qry = qry.first()
        self.assertEqual(qry.nodeId, 100)
        self.assertEqual(qry.value, 22.5)

        #Humidity
        qry = session.query(models.Reading).filter_by(typeId = 2)
        #self.assertEqual(qry.count(), 1)
        qry = qry.first()
        self.assertEqual(qry.nodeId, 100)
        self.assertEqual(qry.value, 50.0)

        #Voltage
        qry = session.query(models.Reading).filter_by(typeId = 6)
        #self.assertEqual(qry.count(), 1)
        qry = qry.first()
        self.assertEqual(qry.nodeId, 100)
        self.assertAlmostEqual(qry.value, 2.45)


