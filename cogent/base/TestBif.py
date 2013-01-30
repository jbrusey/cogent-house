#
# Test code for feeding BaseLogger with some packets.
#
# J. Brusey, May 2011

import sys
import os
sys.path.append(os.environ["TOSROOT"] + "/support/sdk/python")
sys.path.append("../..")
from cogent.node import *
from tinyos.message import MoteIF 
import time
from cogent.base.model import *
from Queue import Queue, Empty
from BaseLogger import BaseLogger


# Note: MoteIF doesn't currently support coming directly off the serial interface
#
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
    

if __name__ == '__main__':
    import logging
    tb = TestBif()


    sm = StateMsg(addr=22)
    sm.set_ctp_parent_id(101)
    sm.set_timestamp(307200)
    sm.set_special(0xc7)
    sm.setElement_packed_state_mask(0, 1)
    sm.setElement_packed_state_mask(1, 0)
    sm.setElement_packed_state_mask(2, 0)
    sm.setElement_packed_state(0, 25.5)
    

    tb.receive(sm)

    sm = StateV1Msg(addr=23)
    sm.set_ctp_parent_id(101)
    sm.set_timestamp(307200)
    sm.set_special(0xc7)
    sm.setElement_packed_state_mask(0, 1)
    sm.setElement_packed_state_mask(1, 0)
    sm.setElement_packed_state(0, 22.5)
    

    tb.receive(sm)

    # test what happens when you have an unknown nodetype
    sm = StateMsg(addr=(4096*5+1))
    sm.set_ctp_parent_id(101)
    sm.set_timestamp(307200)
    sm.set_special(0xc7)
    sm.setElement_packed_state_mask(0, 1)
    sm.setElement_packed_state_mask(1, 0)
    sm.setElement_packed_state_mask(2, 0)
    sm.setElement_packed_state(0, 25.5)
    

    tb.receive(sm)



    logging.basicConfig(#filename="/tmp/BaseLogger.log",
                        #filemode="a",
                        format="%(asctime)s %(levelname)s %(message)s",
                        level=logging.DEBUG)    
    lm = BaseLogger(bif=tb, dbfile='sqlite:///testbif.db')# 'mysql://localhost/ch')
    lm.create_tables()
    lm.run()


        
