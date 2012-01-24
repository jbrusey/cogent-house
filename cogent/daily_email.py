#!/usr/bin/python
#
# ------------------------------------------------------------
# daily-email.py
#
# J. Brusey, December 2011
#
# run a set of status queries but only send a message out when
# something significant happens.
#
# Report query methods can be found in cogent/report/*
#
# ------------------------------------------------------------


from sqlalchemy import create_engine, and_, distinct, func
from sqlalchemy.orm import sessionmaker

from datetime import datetime, timedelta
from cogent.base.model import *
from cogent.report import *

import platform
import smtplib
import time

host=platform.node()
me = "yield@"+host
_DBURL = "mysql://chuser@localhost/ch?connect_timeout=1"
you="chuser@localhost"


def header():
    return """From: """+host+"""<"""+me+""">
To: """+you+"""
MIME-Version: 1.0
Content-type: text/html
Subject: cogent-house status for """+host+""" 
<html><head></head><body>"""

def footer():
    return "</body></html>"

def run_reports(dry_run=False, time_queries=False):

    try:
        session = Session()

        if time_queries:
            start_time = time.time()

        html = []
        for (report, method) in reports:
            html.extend(method(session))
            if time_queries:
                html.append("<p>%s took: %ld secs</p>" % (report, time.time() - start_time))
                start_time = time.time()

        if len(html) == 0:
            html = ['No status updates to report']

    finally:
        session.close()    

    message = header() + "".join(html) + footer()

    if dry_run:
        print message
    else:
        # Send the message via local SMTP server.

        s = smtplib.SMTP('localhost')
        s.sendmail(me, you, message)
   
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
    
    engine = create_engine(_DBURL, echo=False)
    Base.metadata.create_all(engine)
    init_model(engine)

    run_reports(dry_run=options.dry_run, time_queries=options.time_queries)
