#
# Provide an interface between the base station.
#
# J. Brusey, May 2011

import sys
import os
sys.path.append(os.environ["TOSROOT"] + "/support/sdk/python")
from cogent.node import StateMsg, StateV1Msg, ConfigMsg, Packets
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
        self.mif.addListener(self, StateV1Msg)
        self.queue = Queue()

    def get(self, wait=True, timeout=30):
        #This goes into an infinate loop
        if self.source.isDone():
            raise Exception("source is no longer connected")

        return self.queue.get(wait, timeout)

    def receive(self, src, msg):
        self.queue.put(msg)

    def sendMsg(self, msg):
        # assumption is that msg is a ConfigMsg
        self.mif.sendMsg(self.source, 0xffff, msg.get_amType(), 0, msg)

    def finishAll(self):
        self.mif.finishAll()
    
def store_state(msg):
    n = msg.getAddr()

    print "storing state ",n, msg

config_changed_flag = True
def config_changed():
    global config_changed_flag
    t = config_changed_flag
    config_changed_flag = False
    return t

def get_config():
    cm = ConfigMsg()
    configured = Bitset(size=Packets.RS_SIZE)
    configured[Packets.RS_TEMPERATURE] = True
    configured[Packets.RS_HUMIDITY] = True
    configured[Packets.RS_PAR] = True
    configured[Packets.RS_TSR] = True
    configured[Packets.RS_VOLTAGE] = True
    configured[Packets.RS_DUTY] = True
    cm.setElement_byType_samplePeriod(0,30*1024)
    bytes = configured.a
    for i in range(len(bytes)):
        cm.setElement_byType_configured(0, i, bytes[i])

    cm.set_typeCount(1)
    return cm

if __name__ == '__main__':

    bif = BaseIF("sf@localhost:9002")

    while True:
        # wait up to 30 seconds for a message
        try:
            msg = bif.queue.get(True, 30)
            store_state(msg)
        except Empty:
            pass

        if config_changed():
            cm = get_config()
            print "sending ", cm
            bif.sendMsg(cm)
    
