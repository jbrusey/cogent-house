"""
Test code for feeding BaseLogger with some packets.

J. Brusey, May 2011
"""

import logging
import re
import json
from queue import Queue
from unittest.mock import MagicMock, mock_open, patch
import types
import sys
import pulp

node_module = types.ModuleType("pulp.node")


class AckMsg:
    def set_seq(self, seq):
        self.seq = seq

    def set_node_id(self, node_id):
        self.node_id = node_id


class Packets:
    SPECIAL = 0xC7
    AM_BOOTMSG = 1
    AM_STATEMSG = 2
    SC_PACKED_SIZE = 16


node_module.AckMsg = AckMsg
node_module.Packets = Packets
node_module.StateMsg = object
node_module.ConfigMsg = object
node_module.BootMsg = object
sys.modules["pulp.node"] = node_module
setattr(pulp, "node", node_module)

tinyos_module = types.ModuleType("tinyos3")
tinyos_message_module = types.ModuleType("tinyos3.message")


class MoteIF:
    @staticmethod
    def set_debug_level(level):
        pass


tinyos_message_module.MoteIF = MoteIF
sys.modules["tinyos3"] = tinyos_module
sys.modules["tinyos3.message"] = tinyos_message_module

from pulp.base.FlatLogger import FlatLogger

# sys.path.append(os.environ["TOSROOT"] + "/tools/tinyos/python/")
# sys.path.append("../..")
# Minimal StateMsg stand-in for testing without tinyos3 dependencies
class StateMsg:
    def __init__(self, addr=0):
        self._addr = addr
        self._ctp_parent_id = 0
        self._timestamp = 0
        self._special = 0
        self._seq = 0
        self._rssi = 0
        self._mask = 0
        self._packed = {}

    def set_ctp_parent_id(self, value):
        self._ctp_parent_id = value

    def get_ctp_parent_id(self):
        return self._ctp_parent_id

    def set_timestamp(self, value):
        self._timestamp = value

    def get_timestamp(self):
        return self._timestamp

    def set_special(self, value):
        self._special = value

    def get_special(self):
        return self._special

    def setElement_packed_state_mask(self, index, value):
        if value:
            self._mask |= 1 << index
        else:
            self._mask &= ~(1 << index)

    def get_packed_state_mask(self):
        return [self._mask, 0]

    def totalSizeBits_packed_state_mask(self):
        return 16

    def setElement_packed_state(self, index, value):
        self._packed[index] = value

    def getElement_packed_state(self, index):
        return self._packed[index]

    def getAddr(self):
        return self._addr

    def get_seq(self):
        return self._seq

    def get_rssi(self):
        return self._rssi

    def get_amType(self):
        return Packets.AM_STATEMSG


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


def test_flat_init(tmp_path):
    testbif = SimpleBif()
    flat = FlatLogger(bif=testbif, tmp_dir=str(tmp_path))

    assert flat.tmp_file is not None


def test_flat_send_ack(tmp_path):
    testbif = MagicMock()
    flat = FlatLogger(bif=testbif, tmp_dir=str(tmp_path))
    flat.send_ack(seq=1, dest=223)
    testbif.sendMsg.assert_called()


def test_store_state(tmp_path):
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
        flat = FlatLogger(bif=testbif, tmp_dir=str(tmp_path))
        flat.store_state(s_msg)
    write_call = m.mock_calls[2]

    msg_dict = eval(write_call[1][0])
    assert msg_dict["0"] == 25.5


def test_mainloop(tmp_path):
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
        flat = FlatLogger(bif=testbif, tmp_dir=str(tmp_path))
        assert flat.mainloop()
    write_call = m.mock_calls[2]

    msg_dict = eval(write_call[1][0])
    assert msg_dict["0"] == 25.5


def test_startup_processes_tmp_dir(tmp_path):
    tmp_dir = tmp_path / "tmp"
    out_dir = tmp_path / "out"
    tmp_dir.mkdir()
    out_dir.mkdir()

    valid = tmp_dir / "valid.log"
    invalid = tmp_dir / "invalid.log"
    valid.write_text(json.dumps({"x": 1}) + "\n")
    invalid.write_text("{bad json}\n")

    FlatLogger(bif=MagicMock(), tmp_dir=str(tmp_dir), out_dir=str(out_dir))

    assert (out_dir / "valid.log").exists()
    assert not valid.exists()
    assert not invalid.exists()


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
