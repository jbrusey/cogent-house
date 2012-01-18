
from sqlalchemy import create_engine, and_, distinct, func
from sqlalchemy.orm import sessionmaker
import urllib2
import time
from datetime import datetime, timedelta
from cogent.base.model import *

import platform
import smtplib
import re
#from email.mime.multipart import MIMEMultipart
#from email.mime.text import MIMEText

me = "yield@"+platform.node()+".local"
_DBURL = "mysql://chuser@localhost/ch?connect_timeout=1"
host=platform.node()
you="chuser@localhost"
batlvl = 2.6

from cogent.base.model import *
from cogent.report import *

import unittest



class TestIP(unittest.TestCase):

    def test_lowbat(self):

        try:
            s = Session()

            x = lowBat(s)
            #print repr(x)
            self.assertTrue(len(x) == 4)
            y = lowBat(s)
            self.assertTrue(len(y) == 0)
        finally:
            s.close()

    def test_packetyield(self):
        try:
            s = Session()
            x = packetYield(s)
            #print x
            y = packetYield(s)
            #self.assertTrue(len(y) == 0)
            print y
        finally:
            s.close()

    def test_ccyield(self):
        try:
            s = Session()
            x = ccYield(s)
            print x
            y = ccYield(s)
            print y
            #self.assertTrue(len(y) == 0)
        finally:
            s.close()

        
if __name__ == "__main__":
    engine = create_engine("sqlite:///", echo=False)
    Base.metadata.create_all(engine)
    init_model(engine)
    try:
        s = Session()
        h = House(address="Test house")
        s.add(h)
        rt = RoomType(name="Test")
        s.add(rt)
        r = Room(name="Example room", roomType=rt)
        s.add(r)
        n = Node(id=22, house=h, room=r)
        s.add(n)
        s.add(Node(id=23, house=h, room=r))
        s.add(Node(id=24, house=h, room=r))
        s.add(Node(id=4098, nodeTypeId=1, house=h, room=r))
        s.add(Node(id=4099, nodeTypeId=1, house=h, room=r))

        t = datetime.utcnow() - timedelta(days=1)
        for i in range(288):
            ns = NodeState(time=t,
                           nodeId=23,
                           parent=0,
                           localtime=0)
            s.add(ns)

            s.add(Reading(typeId=6,
                        time=t,
                        value=3.0 - i / 288.,
                        nodeId=22))

            s.add(Reading(typeId=11,
                          time=t,
                          value=300.0,
                          nodeId=4098))
            if i < 200:
                s.add(Reading(typeId=11,
                              time=t,
                              value=300.0,
                    nodeId=4099))
            
            if i > 6:
                s.add(NodeState(time=t,
                                nodeId=24,
                                parent=0,
                                localtime=0))
            t = t + timedelta(minutes=5)
            
        s.commit()
    finally:
        s.close()
    unittest.main()
