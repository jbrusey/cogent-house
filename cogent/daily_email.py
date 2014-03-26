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

from cogent.base.model import *
from cogent.report import *

import platform
import smtplib
import time

DBURL = "mysql://{user}@localhost/{database}?connect_timeout=1"

def header(you=None,
           me=None,
           host=None):
    return """From: """+host+"""<"""+me+""">
To: """+you+"""
MIME-Version: 1.0
Content-type: text/html
Subject: cogent-house status for """+host+"""
<html><head></head><body>"""

def footer():
    return "</body></html>"

def run_reports(dry_run=False,
                time_queries=False,
                you="nobody@localhost",
                me="yield@"+platform.node(),
                host=platform.node()
           ):

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

    message = header(you=you, me=me, host=host) + "".join(html) + footer()

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
    parser.add_option("-d", "--database",
                      default="ch",
                      help="mysql database to use")
    parser.add_option("-u", "--user",
                      default="chuser",
                      help="mysql user to login to database with")
    parser.add_option("-m", "--mailto",
                      default="chuser@localhost",
                      help="Address to send emails to")

    (options, args) = parser.parse_args()

    engine = create_engine(DBURL.format(user=options.user,
                                        database=options.database),
                                        echo=False)
    Base.metadata.create_all(engine)
    init_model(engine)

    run_reports(dry_run=options.dry_run,
                time_queries=options.time_queries,
                you=options.mailto
        )
