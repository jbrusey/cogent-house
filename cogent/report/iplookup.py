from sqlalchemy import and_, distinct, func
import urllib2
from datetime import datetime, timedelta
from cogent.base.model import *



def iplookup(session):
   html = []

   
   last_ip = session.query(LastReport).filter(LastReport.name=="ip-address").first()

   try: 
      pub_ip = urllib2.urlopen("http://www.biranchi.com/ip.php").read()

      if last_ip is None or pub_ip != last_ip.value:
         if last_ip is None:
            last_ip = LastReport(name="ip-address", value=pub_ip)
            session.add(last_ip)
         else:
            last_ip.value = pub_ip
         session.commit()

         html.append('<p>My IP address has changed to <a href="http://%s/cogent-house">%s</a></p>' % (pub_ip, pub_ip))

   except Exception, e:
      html.append("<p>Couldn't find ip address due to %s</p>" % str(e))
      session.rollback()

   return html
