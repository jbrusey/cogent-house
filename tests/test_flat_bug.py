import pytest

# Use real FlatLogger; dependency stubs are provided via tests/conftest.py
from pulp.base.FlatLogger import FlatLogger

# Stub message used to trigger str+bytes bug
class SimpleAckMsg:
    def __init__(self, *args, **kwargs):
        pass
    def set_seq(self, seq):
        self.seq = seq
    def set_node_id(self, nid):
        self.node_id = nid
    def dataGet(self):
        return b"abc"
    def offset_data(self, i):
        return 0

class BuggyBif:
    def sendMsg(self, msg, dest=0xFFFF):
        data = ""
        # emulate buggy concatenation in tinyos3's MoteIF.sendMsg
        data += msg.dataGet()[0 : msg.offset_data(0)]


def test_send_ack_typeerror():
    import pulp.base.FlatLogger as FL
    FL.AckMsg = SimpleAckMsg
    flat = FlatLogger(bif=BuggyBif(), tmp_dir="/tmp")
    with pytest.raises(TypeError):
        flat.send_ack(seq=1, dest=42)
