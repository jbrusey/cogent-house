"""
Test code for feeding BaseLogger with some packets.

J. Brusey, May 2011
"""

import logging
import re
from queue import Queue
from unittest.mock import MagicMock, mock_open, patch

from pulp.base.FlatLogger import FlatLogger

# sys.path.append(os.environ["TOSROOT"] + "/tools/tinyos/python/")
# sys.path.append("../..")
from pulp.node import StateMsg


class SimpleBif(object):
    """SimpleBif is a testing version of BaseIF to allow simulation of
    messages from the SerialForwarder
    """

    def __init__(self):
        self.queue = Queue()

    def receive(self, msg):
        """receive a single state message - in this case, will be
        called by test code to add it to the queue.
        """
        self.queue.put(msg)

    def sendMsg(self, msg, dest=0xFFFF):
        """support sending (from BaseLogger) of any messages"""
        print("sendMsg", msg, "to", dest)

    def finishAll(self):
        """finish - currently just a dummy"""
        pass


def test_flat_init():
    testbif = SimpleBif()
    flat = FlatLogger(bif=testbif, tmp_dir="/tmp/")

    assert flat.tmp_file is not None


def test_flat_send_ack():
    testbif = MagicMock()
    flat = FlatLogger(bif=testbif, tmp_dir="/tmp")
    flat.send_ack(seq=1, dest=223)
    testbif.sendMsg.assert_called()


def test_store_state():
    testbif = MagicMock()

    s_msg = StateMsg(addr=22)
    s_msg.set_ctp_parent_id(101)
    s_msg.set_timestamp(307200)
    s_msg.set_special(0xC7)
    # message with type 0 value 25.5
    s_msg.setElement_packed_state_mask(0, 1)
    s_msg.setElement_packed_state_mask(1, 0)
    s_msg.setElement_packed_state_mask(2, 0)
    s_msg.setElement_packed_state(0, 25.5)

    m = mock_open()
    with patch("pulp.base.FlatLogger.open", m):
        flat = FlatLogger(bif=testbif, tmp_dir="/tmp")
        flat.store_state(s_msg)
    write_call = m.mock_calls[2]

    msg_dict = eval(write_call[1][0])
    assert msg_dict["0"] == 25.5


def test_mainloop():
    testbif = SimpleBif()

    s_msg = StateMsg(addr=22)
    s_msg.set_ctp_parent_id(101)
    s_msg.set_timestamp(307200)
    s_msg.set_special(0xC7)
    s_msg.setElement_packed_state_mask(0, 1)
    s_msg.setElement_packed_state_mask(1, 0)
    s_msg.setElement_packed_state_mask(2, 0)
    s_msg.setElement_packed_state(0, 25.5)

    testbif.receive(s_msg)
    m = mock_open()
    with patch("pulp.base.FlatLogger.open", m):
        flat = FlatLogger(bif=testbif, tmp_dir="/tmp")
        assert flat.mainloop()
    write_call = m.mock_calls[2]

    msg_dict = eval(write_call[1][0])
    assert msg_dict["0"] == 25.5


def tes_t_bif():
    """run all tests"""
    testbif = SimpleBif()

    s_msg = StateMsg(addr=22)
    s_msg.set_ctp_parent_id(101)
    s_msg.set_timestamp(307200)
    s_msg.set_special(0xC7)
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
    s_msg = StateMsg(addr=(4096 * 5 + 1))
    s_msg.set_ctp_parent_id(101)
    s_msg.set_timestamp(307200)
    s_msg.set_special(0xC7)
    s_msg.setElement_packed_state_mask(0, 1)
    s_msg.setElement_packed_state_mask(1, 0)
    s_msg.setElement_packed_state_mask(2, 0)
    s_msg.setElement_packed_state(0, 25.5)

    testbif.receive(s_msg)

    logging.basicConfig(  # filename="/tmp/BaseLogger.log",
        # filemode="a",
        format="%(asctime)s %(levelname)s %(message)s",
        level=logging.DEBUG,
    )
    base_logger = FlatLogger(bif=testbif)
    base_logger.run()
