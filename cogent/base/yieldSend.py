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


def yieldSender(dry_run=False, time_queries=False):

   html = ["""From: """+host+"""<"""+me+""">
To: """+you+"""
MIME-Version: 1.0
Content-type: text/html
Subject: """+host+""" yield
"""]

   start_time = time.time()
   try: 
      pub_ip = urllib2.urlopen("http://www.biranchi.com/ip.php").read()
      html.append("<html><head></head><body><p>Hi!</p><p>This is <b>"+platform.node()+"</b>, my current ip address is <b>"+pub_ip+"</b></p>")
   except Exception, e:
      html.append("<html><head></head><body><p>Couldn't find ip address due to %s</p>" % str(e))

   if time_queries:
      html.append("<p>ip lookup took: %ld secs</p>" % (time.time() - start_time))
      start_time = time.time()
   
   try:
      session = Session()
      

      if time_queries:
         html.append("<p>creating session took: %ld secs</p>" % (time.time() - start_time))
         start_time = time.time()
      t = datetime.utcnow() - timedelta(days=1)
      
      lowBatHeader = True
      for (r, addr, name) in session.query(distinct(Reading.nodeId), House.address, Room.name).filter(and_(Reading.typeId==6,Reading.value<=batlvl,Reading.time > t)).join(Node, House, Room).order_by(House.address, Room.name):  
         
	 if (lowBatHeader):
            html.append("<h3>Nodes reporting low battery levels in last 24 hours</h3>")
            html.append("<table border=\"1\">")
            html.append("<tr><th>Node</th><th>House</th><th>Room</th></tr>"  )
            lowBatHeader=False
         #r = r[0]
   
         html.append("<tr><td>%d</td><td>%s</td><td>%s</td></tr>" % (r,addr,name))

      if not lowBatHeader:
         html.append("</table>")
         
      if time_queries:
         html.append("<p>low battery check took: %ld secs</p>" % (time.time() - start_time))
         start_time = time.time()


      html.append("<h3>Yield in last 24 hours</h3>")
      html.append("<table border=\"1\">")
      html.append("<tr><th>Node</th><th>House</th><th>Room</th><th>Message Count</th><th>Last Heard</th><th>Yield</th></tr>"  )

      t = datetime.utcnow() - timedelta(days=1)
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

	    if y>80:
               html.append("<tr><td>%d</td><td>%s</td><td>%s</td><td>%d</td><td>%s</td><td>%8.2f</td></tr>" % (int(ns.nodeId), n.house.address, room, cnt, str(maxtime), y))
	    else:
               html.append("<tr><td><b>%d</b></td><td><b>%s</b></td><td><b>%s</b></td><td><b>%d</b></td><td><b>%s</b></td><td><b>%8.2f</b></td></tr>" % (int(ns.nodeId), n.house.address, room, cnt, str(maxtime), y))

      if time_queries:
         html.append("<p>yield check took: %ld secs</p>" % (time.time() - start_time))
         start_time = time.time()


      report_set = set([int(x) for (x,) in session.query(distinct(NodeState.nodeId)).filter(NodeState.time > t).all()])
      all_set = set([int(x) for (x,) in session.query(Node.id).filter(Node.houseId != None).all()])
      missing_set = all_set - report_set
      extra_set = report_set - all_set

      if time_queries:
         html.append("<p>missing query took: %ld secs</p>" % (time.time() - start_time))
         start_time = time.time()


      if len(missing_set) > 0:
         html.append("</table><p><p><h3>Registered nodes not reporting in last hour</h3><p>")

         html.append("<table border=\"1\">")
         html.append("<tr><th>Node</th><th>House</th><th>Room</th><th>Last Heard</th></tr>"  )

         for (ns, maxtime, hn, rn) in session.query(NodeState,func.max(NodeState.time),House.address,Room.name).filter(NodeState.nodeId.in_(missing_set)).group_by(NodeState.nodeId).join(Node,House,Room).order_by(House.address, Room.name).all():
            html.append("<tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (int(ns.nodeId), hn, rn, str(maxtime)))
                  

      html.append("</table>")
      if len(extra_set) > 0:
         html.append("</p><h3>Extra nodes that weren't expected in last 24 hours</h3><p>")
         for i in sorted(extra_set):
            html.append("%d<br/>" % i)


      if time_queries:
         html.append("<p>getting house/room for registered nodes not reporting took: %ld secs</p>" % (time.time() - start_time))
         start_time = time.time()

         
      html.append("</body></html>")
         
   finally:
      session.close()    
  
   #send out the emails
   html.append("</table></body></html>")

   # Send the message via local SMTP server.
   if dry_run:
      print "".join(html)
   else:
      s = smtplib.SMTP('localhost')
      s.sendmail(me,you,"".join(html))
   
if __name__ == "__main__":
   from optparse import OptionParser

   parser = OptionParser()
   parser.add_option("-n", "--dry-run", 
                     action="store_true",
                     default=False,
                     help="don't send e-mail--just print to stdout")
   parser.add_option("-t", "--time-queries", 
                     action="store_true",
                     default=False,
                     help="time how long each query takes")

   (options, args) = parser.parse_args()

   yieldSender(dry_run=options.dry_run, time_queries=options.time_queries)
