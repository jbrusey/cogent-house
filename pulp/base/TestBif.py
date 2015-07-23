""" 
Test code for feeding BaseLogger with some packets.

J. Brusey, May 2011
"""
import sys
import os
sys.path.append(os.environ["TOSROOT"] + "/tools/tinyos/python/")
sys.path.append("../..")
from pulp.node import StateMsg
from Queue import Queue
from pulp.base.BaseLogger import BaseLogger
import logging

# Note: MoteIF doesn't currently support coming directly off the
# serial interface
#
class TestBif(object):
    """ TestBif is a testing version of BaseIF to allow simulation of
    messages from the SerialForwarder
    """
    def __init__(self):
        self.queue = Queue()

    def receive(self, msg):
        """ receive a single state message - in this case, will be
        called by test code to add it to the queue.
        """
        self.queue.put(msg)

    def sendMsg(self, msg, dest=0xffff):
        """ support sending (from BaseLogger) of any messages """
        print "sendMsg", msg, "to", dest

    def finishAll(self):
        """ finish - currently just a dummy """
        pass


def main():
    """ run all tests """
    testbif = TestBif()


    s_msg = StateMsg(addr=22)
    s_msg.set_ctp_parent_id(101)
    s_msg.set_timestamp(307200)
    s_msg.set_special(0xc7)
    s_msg.setElement_packed_state_mask(0, 1)
    s_msg.setElement_packed_state_mask(1, 0)
    s_msg.setElement_packed_state_mask(2, 0)
    s_msg.setElement_packed_state(0, 25.5)


    testbif.receive(s_msg)

    # s_msg = StateV1Msg(addr=23)
    # s_msg.set_ctp_parent_id(101)
    # s_msg.set_timestamp(307200)
    # s_msg.set_special(0xc7)
    # s_msg.setElement_packed_state_mask(0, 1)
    # s_msg.setElement_packed_state_mask(1, 0)
    # s_msg.setElement_packed_state(0, 22.5)


    # testbif.receive(s_msg)

    # test what happens when you have an unknown nodetype
    s_msg = StateMsg(addr=(4096*5+1))
    s_msg.set_ctp_parent_id(101)
    s_msg.set_timestamp(307200)
    s_msg.set_special(0xc7)
    s_msg.setElement_packed_state_mask(0, 1)
    s_msg.setElement_packed_state_mask(1, 0)
    s_msg.setElement_packed_state_mask(2, 0)
    s_msg.setElement_packed_state(0, 25.5)


    testbif.receive(s_msg)



    logging.basicConfig(#filename="/tmp/BaseLogger.log",
                        #filemode="a",
                        format="%(asctime)s %(levelname)s %(message)s",
                        level=logging.DEBUG)
    base_logger = BaseLogger(bif=testbif,
                             dbfile='sqlite:///testbif.db')
    # 'mysql://localhost/ch')
    base_logger.create_tables()
    base_logger.run()


if __name__ == '__main__':
    main()
