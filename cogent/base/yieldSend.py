#!/usr/bin/python

from sqlalchemy import create_engine, and_, distinct, func
from sqlalchemy.orm import sessionmaker
import urllib2
import datetime
import time
from datetime import datetime, timedelta
from cogent.base.model import *

import platform
import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

me = "yield@"+platform.node()+".local"
_DBURL = "mysql://chuser@localhost/ch?connect_timeout=1"
engine = create_engine(_DBURL, echo=False)
Session = sessionmaker(bind=engine)
host=platform.node()
you="chuser@localhost"

batlvl = 2.6

def yieldSender():

   html = ["""From: """+host+"""<"""+me+""">
To: """+you+"""
MIME-Version: 1.0
Content-type: text/html
Subject: """+host+""" Yield
"""]
    
   pub_ip = urllib2.urlopen("http://www.biranchi.com/ip.php").read()
   html.append("<html><head></head><body>Hi!<br><br>This is <b>"+platform.node()+"</b>, my current ip address is <b>"+pub_ip+"</b><br>")

   
   try:
      session = Session()

      html.append("<h3>Nodes reporting low battery levels in last 24 hours</h3>")
      t = datetime.now() - timedelta(days=1)
      for (r, n) in session.query(distinct(Reading.nodeId), House.address, Room.name
                             ).filter(
         and_(Reading.typeId==6,
              Reading.value<=batlvl,
              Reading.time > t)).join(
         Node, House, Room).order_by(
         House.address, Room.name):
         r = r[0]
            
         html.append("<p>%d</p>" % (r,6,60,60,r))


      html.append("<h3>Yield in last 24 hours</h3>")
      html.append("<table border=\"1\">")
      html.append("<tr><th>Node</th><th>House</th><th>Room</th><th>Message Count</th><th>Last Heard</th><th>Yield</th></tr>"  )

      t = datetime.now() - timedelta(days=1)
      nodestateq = session.query(NodeState,func.count(NodeState),func.max(NodeState.time)).filter(NodeState.time > t).group_by(NodeState.nodeId).join(Node,House,Room).order_by(House.address, Room.name).all()
      for (ns, cnt, maxtime) in nodestateq:
         n = ns.node
         if n.house is not None:
            yield_secs = (1 * 24 * 3600)
            
            y = (cnt) / (yield_secs / 300.0) * 100.0
            
            
            room = 'unknown'
            if n.room is not None:
               room = n.room.name
                
            values = [ns.nodeId, n.house.address, room, cnt, maxtime, y]
            html.append("<tr><td>%d</td><td>%s</td><td>%s</td><td>%d</td><td>%s</td><td>%8.2f</td></tr>" % (int(ns.nodeId), n.house.address, room, cnt, str(maxtime), y))
      
   finally:
      session.close()    
  
   #send out the emails
   html.append("</table></body></html>")

   # Send the message via local SMTP server.
   s = smtplib.SMTP('localhost')
   s.sendmail(me,you,"".join(html))
            
if __name__ == "__main__":
    yieldSender()
