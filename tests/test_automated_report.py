"""Test Cases for the automated report module"""

#Logging
import logging
logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)

import unittest2 as unittest

#SQLA
import sqlalchemy
from sqlalchemy.orm import sessionmaker

#Cogent House
import cogent.report.automated_report as automated_report

#Webinterface version of the DB
import cogentviewer.models as models
import cogentviewer.models.meta as meta



class TestAutoReport(unittest.TestCase):
    """Test the automated reporting module"""

    @classmethod
    def setUpClass(cls):
        """Class method, called each time this is initialised"""
        #cls.config = testing.setUp()

        #Load settings from Configuration file
        LOG.debug("Init Test Class Database for {0}".format(cls.__name__))
        cls.engine = sqlalchemy.create_engine("sqlite:///automate-test.db")
        meta.Base.metadata.bind = cls.engine
        meta.Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker()
        cls.Session.configure(bind=cls.engine)

        cls.needsinit = True
        cls.reporter = automated_report.OwlsReporter("sqlite:///automate-test.db")

    def setUp(self):
        """Setup for individual tests"""
        LOG.debug("Init Stat (Start) {0}".format(self.needsinit))
        if self.needsinit == True:
            LOG.debug("Needs Initialisation")
            self.needsinit = False
            models.populateData.init_data(docalib=False)
            session = self.Session()
            import populate_testdb
            populate_testdb.cleardb(session) #Remove all the old cruft
            populate_testdb.populatedata(session) #And populate with fresh data

        else:
            LOG.debug("DB Initialised")

        LOG.debug("Init Status {0}".format(self.needsinit))

    def testFetchOverview(self):
        """Does the overview class work as expected"""

        outdict = self.reporter.fetch_overview()

        #So we should have 2 deployed servers,  4 houses and 8 Nodes


        expectdict = {"deployed_serv": 2,
                      "deployed_houses": 5,
                      "deployed_nodes": 8}

        self.assertEqual(outdict, expectdict)

        session = self.Session()

        #However the DB should have 3 servers (only two deployed and 10 Nodes)
        qry = session.query(models.Server)
        self.assertEqual(qry.count(), 3)

        qry = session.query(models.Node)
        self.assertEqual(qry.count(), 10)


    def testPushStatus(self):
        """Test if the pushstatus stuff has worked ok"""

        outdict = self.reporter.fetch_pushstatus()

        #Fake it up so that 3 servers have pushed this week but only two today
        expectdict = {"push_week": 3,
                      "push_today": 2,
        }

        self.assertEqual(outdict, expectdict)


    def test_housestatus(self):
        """Test house status is as expected"""

        outstr = "{0} has {1} nodes reporting expected {2}".format("address1",
                                                                   0,
                                                                   2)

        expectdict = {"houses_today": 3,
                      "houses_missing": [[outstr, [0, 1], 2],
                                         ["address5 has no registered nodes", [], 0]
                                     ]
        }

        outdict = self.reporter.fetch_housestatus()
        LOG.debug("HOUSE STATUS {0}".format(outdict))
        self.assertEqual(expectdict, outdict)

    def test_nodestatus(self):
        expectdict = {"node_week": 8,
                      "node_today": 6}

        outdict = self.reporter.fetch_nodestatus()

        self.assertEqual(outdict, expectdict)



    def test_pulsenodes(self):
        expectdict = {"pulse_warnings": [21]}

        outdict = self.reporter.check_pulse_nodes()

        self.assertEqual(outdict, expectdict)
        pass


    @unittest.skip
    def test_render(self):
        """NOTE: This doesn't test for substiturion in render
        However, it will check that we can render"""

        import os
        import os.path

        #We need a quick hack here to get the right path
        if os.path.basename(os.path.abspath("")) == "cogent-house":
            os.chdir("cogent/report")
        outstr = self.reporter.render_report()
        self.assertTrue(outstr)
