#
# Provide an interface between the base station.
#
# J. Brusey, May 2011

import sys
import os
from pulp.node import StateMsg, ConfigMsg, Packets, BootMsg
from tinyos3.message import MoteIF
import time
from queue import Queue, Empty
import logging


# Note: MoteIF doesn't currently support coming directly off the serial interface
#
class BaseIF(object):
    def __init__(self, source, retries=5, retry_delay=1.0):
        """Initialise the TinyOS interface.

        Occasionally the serial forwarder is not ready when this class is
        created which results in a ``ConnectionRefusedError`` bubbling out of
        the tinyos packet code.  To make the start up sequence more robust we
        catch that error and retry a few times with a short delay between
        attempts.

        :param source: Serial forwarder source string.
        :param retries: Number of connection attempts before giving up.
        :param retry_delay: Delay in seconds between retries.
        """

        self.mif = MoteIF.MoteIF()
        attempt = 0
        while True:
            try:
                self.source = self.mif.addSource(source)
                break
            except OSError as err:
                attempt += 1
                if attempt > retries:
                    raise
                logging.getLogger(__name__).warning(
                    "Connection to %s refused, retrying in %s seconds", source, retry_delay
                )
                time.sleep(retry_delay)

        self.mif.addListener(self, StateMsg)
        self.mif.addListener(self, BootMsg)
        self.queue = Queue()

    def get(self, wait=True, timeout=30):
        if self.source.isDone():
            raise Exception("source is no longer connected")
        return self.queue.get(wait, timeout)

    def receive(self, src, msg):
        self.queue.put(msg)

    def sendMsg(self, msg, dest=0xFFFF):
        self.mif.sendMsg(self.source, dest, msg.get_amType(), 0, msg)

    def finishAll(self):
        self.mif.finishAll()


def store_state(msg):
    n = msg.getAddr()
    print(f"storing state {n}-{msg}")


if __name__ == "__main__":

    bif = BaseIF("sf@localhost:9002")

    while True:
        try:
            msg = bif.get(True, 5)
            store_state(msg)
        except Empty:
            pass
