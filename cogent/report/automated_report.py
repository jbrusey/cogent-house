"""
Module to generate an automated reports for deployments

:version: 0.2
:module-author:  Dan Goldsmith <djgoldsmith@googlemail.com>

:since 0.2:

* changed so mako template is in /etc/cogent-house

"""

import datetime

import sqlalchemy

import logging
logging.basicConfig(level=logging.INFO)

import argparse #Apparently this is installed in 2.6 (at least on cogentee)

import cogentviewer.models as models
import cogentviewer.models.meta as meta
#import cogent.base.model as models
#import cogent.base.model.meta as meta

from mako.template import Template

import smtplib

import sys
import os



Base = meta.Base

class OwlsReporter(object):
    """Main reporter class to generate and render automated reports"""
    def __init__(self, enginestr, reportdate=datetime.datetime.utcnow()):
        """Initialise the reporter
        :param enginestr:  SQLA String to connect to database
        :param reportdate: Date to run report for
        """
        self.enginestr = enginestr
        engine = sqlalchemy.create_engine(enginestr, echo=False)
        meta.Session.configure(bind=engine)
        Base.metadata.bind = engine
        self.reportdate = reportdate


        #Work out the template location
        if sys.prefix  == "/usr":
            conf_prefix = "/" #If its a standard "global" instalation
        else :
            conf_prefix = "{0}/".format(sys.prefix)

        templatepath = os.path.join(conf_prefix,
                                  "etc",
                                  "cogent-house",
                                  "report-templates",
                                  "report-template.mak")

        self.templatepath = templatepath

    def fetch_overview(self):
        """Fetch data to populate the first "overview" table"""

        session = meta.Session()

        #Total deployed servers
        qry = session.query(models.House.serverid)
        qry = qry.filter(models.House.serverid != None)
        qry = qry.distinct()
        deployed_serv = qry.count()
        logging.debug("Total Deployed Servers: {0}".format(deployed_serv))

        #Total Houses
        qry = session.query(models.House)
        deployed_houses = qry.count()
        logging.debug("Total Deployed houses: {0}".format(deployed_houses))

        #Deployed Nodes
        qry = session.query(models.Node).filter(models.Node.locationId != None)
        deployed_nodes = qry.count()
        logging.debug("Total Deployed Nodes: {0}".format(deployed_nodes))


        outdict = {"deployed_serv": deployed_serv,
                   "deployed_houses": deployed_houses,
                   "deployed_nodes": deployed_nodes}

        return outdict

    def fetch_pushstatus(self):
        """How many servers have pushed etc"""

        #Deployed this week
        #Deplyoed today
        #Houses with data this week
        #Houses with data today

        session = meta.Session()

        now = self.reportdate
        today = now.date()
        lastweek = today - datetime.timedelta(days=7)
        logging.debug("Today is {0}".format(today))

        #This week
        qry = session.query(models.PushStatus)
        qry = qry.filter(models.PushStatus.time >= lastweek)
        qry = qry.group_by(models.PushStatus.hostname)

        push_week = qry.count()

        logging.debug("Servers that have pushed this week: {0}"
                      .format(push_week))

        qry = session.query(models.PushStatus)
        qry = qry.filter(models.PushStatus.time >= today)
        qry = qry.group_by(models.PushStatus.hostname)

        push_today = qry.count()

        logging.debug("Servers that have pushed this today: {0}"
                      .format(push_today))


        outdict = {"push_week": push_week,
                   "push_today": push_today,
                   }

        return outdict

    def fetch_housestatus(self):
        """Fetch details of houses that have had readings today"""

        session = meta.Session()

        now = self.reportdate
        today = now.date()

        #qry = session.query(models.House)
        houseqry = session.query(models.House)

        houses_today = 0 #Houses that have pushed today
        houses_missing = [] #Houses with problems
        houses_partial = []
        #For each house
        for house in houseqry:
            #Locations associated with this house
            houselocs = [h.id for h in house.locations]
            #And Nodes
            if houselocs == []:
                logging.warning("House {0} has no registered nodes"
                                .format(house))
                houses_missing.append(["{0} has no registered nodes"
                                       .format(house.address),
                                    [],
                                    0])
                continue

            qry = session.query(models.Node)
            qry = qry.filter(models.Node.locationId.in_(houselocs))
            nodeids = [n.id for n in qry]
            logging.debug("House {0} Expects {1} Nodes".format(house, nodeids))

            #Final Query:  Filter expected nodes
            qry = session.query(models.NodeState)
            qry = qry.filter(models.NodeState.nodeId.in_(nodeids))
            #Filter by today
            qry = qry.filter(models.NodeState.time >= today)
            qry = qry.group_by(models.NodeState.nodeId)

            house_nodes = qry.count()
            qrynodes = [n.nodeId for n in qry.all()]

            if house_nodes > 0:
                houses_today += 1

            #And check for expected
            if house_nodes == 0:
                outlist = ["{0} has {1} nodes reporting expected {2}"
                           .format(house.address,
                                   house_nodes,
                                   len(nodeids))]
                missingNodes = []


                for nid in nodeids:
                    if nid not in qrynodes:
                        #Run a query
                        #missingNodes.append(nid)
                        nqry = session.query(models.Node).filter_by(id = nid)
                        nqry = nqry.first()
                        roomname = nqry.location.room.name
                        logging.debug("Location {0}".format(roomname))
                        missingNodes.append("{0} ({1})".format(nqry.id,
                                                               roomname))


                outlist.append(missingNodes)
                #Work out and append the difference
                outlist.append(len(nodeids) - house_nodes)
                houses_missing.append(outlist)

            elif house_nodes != len(nodeids):
                logging.debug("---> House is missing nodes {0}"
                              .format(house.address))

                outlist = ["{0} has {1} nodes reporting expected {2}"
                           .format(house.address,
                                   house_nodes,
                                   len(nodeids))]
                missingNodes = []


                for nid in nodeids:
                    if nid not in qrynodes:
                        #Run a query
                        nqry = session.query(models.Node).filter_by(id = nid)
                        nqry = nqry.first()
                        roomname = nqry.location.room.name
                        #logging.debug("Location {0}".format(roomname))
                        missingNodes.append("{0} ({1})".format(nqry.id,
                                                               roomname))

                outlist.append(missingNodes)
                #Work out and append the difference
                outlist.append(len(nodeids) - house_nodes)
                houses_partial.append(outlist)


        sorted_missing = sorted(houses_missing,
                               key = lambda thekey: thekey[2],
                               reverse=True)
        logging.debug("MISSING {0} \n SORTED {1}".format(houses_missing,
                                                         sorted_missing))

        sorted_partial = sorted(houses_partial,
                                key = lambda thekey: thekey[2],
                                reverse=True)

        logging.debug("PARTIAL {0} \n SORTED {1}".format(houses_partial,
                                                         sorted_partial))

        logging.debug("Houses Reporting today {0}".format(houses_today))
        return {"houses_today": houses_today,
                "houses_missing": sorted_missing,
                "houses_partial": sorted_partial
        }

    def fetch_nodestatus(self):
        """Details of deployed Nodes"""
        session = meta.Session()

        now = self.reportdate
        today = now.date()
        lastweek = today - datetime.timedelta(days=7)
        qry = session.query(models.NodeState)
        qry = qry.filter(models.NodeState.time >= lastweek)
        qry = qry.group_by(models.NodeState.nodeId)

        node_week = qry.count()

        logging.debug("Nodes that have data this week: {0}".format(node_week))

        qry = session.query(models.NodeState)
        qry = qry.filter(models.NodeState.time >= today)
        qry = qry.group_by(models.NodeState.nodeId)

        node_today = qry.count()

        logging.debug("Nodes that have data today: {0}".format(node_week))

        outdict = {"node_week": node_week,
                   "node_today": node_today}

        return outdict

    def check_pulse_nodes(self):
        """Check for pulse output nodes that could be having issues.
        IE the value has not increased in the past 24 hours
        """

        session = meta.Session()

        now = self.reportdate
        yesterday = now - datetime.timedelta(days=1)

        #Get sensor type ids for the pulse output nodes
        pulsenodes = ["Heat Energy", "Heat Volume", "Gas Pulse Count"]
        qry = session.query(models.SensorType)
        qry = qry.filter(models.SensorType.name.in_(pulsenodes))
        logging.debug("Pulse Output Nodes {0}".format(qry.all()))
        pulseids = [n.id for n in qry]

        #and the main query
        qry = session.query(models.Reading.nodeId,
                            sqlalchemy.func.min(models.Reading.value),
                            sqlalchemy.func.max(models.Reading.value)
                            )
        qry = qry.filter(models.Reading.typeId.in_(pulseids))
        qry = qry.filter(models.Reading.time >= yesterday)
        qry = qry.group_by(models.Reading.nodeId)

        pulse_warnings = []

        for item in qry:
            logging.debug(item)
            if item[2] == item[1]:
                logging.debug("No Change for Node {0} in the past 24 hours"
                              .format(item[0]))
                nqry = session.query(models.Node).filter_by(id = item[0])
                nqry = nqry.first()
                roomname = nqry.location.room.name
                pulse_warnings.append("{0} ({1})".format(item[0], roomname))

        logging.debug("Pulse Node Warnings {0}".format(pulse_warnings))
        return {"pulse_warnings": pulse_warnings}

    def render_report(self):
        """Render the report"""

        projectstring = self.enginestr.split("/")[-1]
        currentdate = self.reportdate
        #Dictionary to hold our output
        outdict = {"project": projectstring,
                   "date": currentdate
        }

        #Overview
        dat = self.fetch_overview()
        outdict.update(dat)

        dat = self.fetch_pushstatus()
        outdict.update(dat)

        dat = self.fetch_housestatus()
        outdict.update(dat)

        dat = self.fetch_nodestatus()
        outdict.update(dat)

        dat = self.check_pulse_nodes()
        logging.debug(dat)
        outdict.update(dat)




        #Fetch and append overview
        thetemplate = Template(filename=self.templatepath)
        out = thetemplate.render(**outdict)

        return out

#Render
# currentdate = datetime.datetime.now()
# outvars = {"project": "OWLS",
#            "date": currentdate}


# thetemplate = Template(filename="template.mak")


# print thetemplate.render(**outvars)
if __name__ == "__main__": # pragma: no cover

    defaultdb = "mysql://chuser@localhost/owls"
    #Set up command line parser
    parser = argparse.ArgumentParser(description="Automated Report Generation")

    parser.add_argument("-db",
                        "--database",
                        help="SQLA db to connect to ({0})".format(defaultdb),
                        default=defaultdb
    )

    parser.add_argument("-o",
                        "--output",
                        help="Output to file <name>",
                        required=False
    )

    parser.add_argument("-t",
                        "--term",
                        help="output to terminal",
                        required=False)

    parser.add_argument("-d",
                        "--date",
                        help="Optional date to run report for <DD>-<MM>-<YYYY>",
                        default = datetime.datetime.utcnow(),
                        required=False
    )

    parser.add_argument("-e",
                        "--email",
                        help="Email addresses to send to",
                        required=False)

    args = parser.parse_args()


    thedate = args.date
    if type(thedate) == str:
        parts = [int(x) for x in thedate.split("-")]
        thedate = datetime.datetime(parts[2], parts[1], parts[0])


    reporter = OwlsReporter(args.database,
                            thedate
    )

    output = reporter.render_report()

    if args.output:
        fd = open(args.output, "w")
        fd.write(output)
        fd.close()
    elif args.term:

        print output

    if args.email:
        addresses = args.email.split(",")
        logging.debug("Sending E-Mail")
        s = smtplib.SMTP('localhost')
        sender = "nobody@cogentee.coventry.ac.uk"
        receivers = ["dang@cogentee.coventry.ac.uk"]

        Header = ["From: Automated Reporting <nobody@cogentee.coventry.ac.uk>",
                  "To: dang <reports@cogentee.coventry.ac.uk>",
                  "MIME-Version: 1.0",
                  "Content-type: text/html",
                  "Subject: Automated Deployment Status Report {0}".format(
                      datetime.datetime.now()),
                  "",
                  ]

        theheader = "\n".join(Header)
        message = "{0} \n\n{1}".format(theheader, output)
        s.sendmail(sender, addresses, message)
