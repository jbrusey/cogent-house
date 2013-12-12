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

    @unittest.skip
    def test_nodata(self):
        """Check what happens if we have no data recieved from the bif"""
        output = self.blogger.mainloop()
        self.assertFalse(output)

    def testRcv(self):
        """Test a single receive"""
        now = datetime.datetime.now()

        #Add the node
        #session = self.Session()
        #thenode = models.Node(id=4242)
        #session.add(thenode)
        #session.commit()
        #session.close()
        
        #Create our bitmask
        bs = Bitset(size=Packets.RS_SIZE)
        #Try to setup a temperature sample
        bs[Packets.RS_TEMPERATURE] = True

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

    def test_Rcv_Node(self):
        """Does Recieve work when that node is not in the DB"""

        now = datetime.datetime.now()

        #Create our bitmask
        bs = Bitset(size=Packets.RS_SIZE)
        #Try to setup a temperature sample
        bs[Packets.RS_TEMPERATURE] = True

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
        
        
    def testrecvCombined(self):
        """Can we correctly recieve and store multiple packets"""

        
        

