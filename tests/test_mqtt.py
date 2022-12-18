"""
Test code for feeding BaseLogger with some packets.

J. Brusey, May 2011
"""

import logging
import re
from queue import Queue
from unittest.mock import MagicMock, patch, mock_open

from pulp.base.MqttLogger import MqttLogger, mqtt

# sys.path.append(os.environ["TOSROOT"] + "/tools/tinyos/python/")
# sys.path.append("../..")
from pulp.node import StateMsg


class SimpleBif(object):
    """SimpleBif is a testing version of BaseIF to allow simulation of
    messages from the SerialForwarder
    """

    def __init__(self):
        self.queue = Queue()

    def get(self, wait=True, timeout=30):
        return self.queue.get(wait, timeout)

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


def test_mqtt_init():
    testbif = SimpleBif()
    with patch("pulp.base.MqttLogger.mqtt.Client") as c:
        flat = MqttLogger(bif=testbif)

        flat.client.loop_start.assert_called_with()
        flat.client.connect.assert_called_with(
            host="localhost", port=1883, keepalive=60
        )


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
    with patch("pulp.base.MqttLogger.mqtt.Client") as c:
        flat = MqttLogger(bif=testbif, topic="topic")
        assert flat.mainloop()
        flat.client.publish.assert_called_with("topic/22/temperature", 25.5)

    testbif = SimpleBif()
    testbif.receive(s_msg)
    with patch("pulp.base.MqttLogger.mqtt.Client") as c:
        with patch(
            "pulp.base.MqttLogger.open", mock_open(read_data="22,front-room")
        ) as m:
            flat = MqttLogger(
                bif=testbif, topic="topic", location_file="/tmp/locationfile"
            )
            assert flat.mainloop()
            flat.client.publish.assert_called_with("topic/front-room/temperature", 25.5)
