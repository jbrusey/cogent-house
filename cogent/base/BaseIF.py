#
# Provide an interface between the base station.
#
# J. Brusey, May 2011

import sys
import os
sys.path.append(os.environ["TOSROOT"] + "/support/sdk/python")
from cogent.node import StateMsg, ConfigMsg, Packets
from tinyos.message import MoteIF 
import time
from cogent.base.model import *
from Queue import Queue, Empty


# Note: MoteIF doesn't currently support coming directly off the serial interface
#
class BaseIF(object):
    def __init__(self, source):
        self.mif = MoteIF.MoteIF()
        self.source = self.mif.addSource(source)
        self.mif.addListener(self, StateMsg)
        self.queue = Queue()

    def receive(self, src, msg):
        self.queue.put(msg)

    def sendMsg(self, msg, dest=0xffff):
        self.mif.sendMsg(self.source, dest, msg.get_amType(), 0, msg)

    def finishAll(self):
        self.mif.finishAll()
    
def store_state(msg):
    n = msg.getAddr()
    print "storing state ",n, msg


if __name__ == '__main__':

    bif = BaseIF("sf@localhost:9002")

    while True:
        # wait up to 30 seconds for a message
        try:
            msg = bif.queue.get(True, 30)

	    j = 0
            mask = Bitset(value=msg.get_packed_state_mask())
            print "State mask size:", msg.totalSizeBits_packed_state_mask()
            state = []
            for i in range(msg.totalSizeBits_packed_state_mask()):
                if mask[i]:
                    try:
                        v = msg.getElement_packed_state(j)
                    except:
                        v = "Invalid"
                    print "%s\t%s\t%s" % (j, i, v)
                j += 1
            print ""


            #store_state(msg)
        except Empty:
            pass
    
