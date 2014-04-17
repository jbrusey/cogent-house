"""
Test Yield script functionality
"""

import unittest

import datetime

#from cogentviewer.views import homepage
import cogentviewer.tests.base as base

from cogentviewer.views import yields

class yieldTest(base.FunctionalTest):
    def test_page(self):
        #Can we actually open the page
        res = self.testapp.get("/yield/")
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.content_type,"text/html")
        res.mustcontain("<title>Yield Report</title>")



    def test_queue(self):
        """Does the queue function work as expected.

        This version tests when node.locationId's are available
        """

        #So for houseId 1 we should have
        # Location, Room,         Node
        # 1         Master Bed ,  837
        # 2         Bathroom   ,  838

        out = yields.queuenodes(1)
        #Is split into two tuples
        nids, desc = out

        #Are the node Ids as expected
        self.assertEqual(nids, [837, 838])

        #Are the dscriptions as expected
        thedesc = [{"nodeid":837,
                    "locationid":1,
                    "room": "Master Bedroom",
                    },
                   {"nodeid":838,
                    "locationid":2,
                    "room": "Bathroom",
                    }
                   ]

        self.assertEqual(desc, thedesc)

    def test_queue_noIds(self):
        """Does the queue function work as expected.

        This version tests when node.locationId's are
        Null
        """

        #So for houseId 2 we should have
        # Location, Room,         Node
        # 3         Master Bed ,  1061
        # 4         Bathroom   ,  1063

        out = yields.queuenodes(2)
        #Is split into two tuples
        nids, desc = out

        #Are the node Ids as expected
        self.assertEqual(nids, [1061, 1063])

        #Are the dscriptions as expected
        thedesc = [{"nodeid":1061,
                    "locationid":3,
                    "room": "Master Bedroom",
                    },
                   {"nodeid":1063,
                    "locationid":4,
                    "room": "Bathroom",
                    }
                   ]

        self.assertEqual(desc, thedesc)

    def test_calculate(self):
        """Can we calculate yield correctly

        Really just for completeness but both of these deployments
        (used for other tests) should have 100% yield
        """

        theyield = yields.calcyield(837)

        lastsample, datayield, packetyield = theyield
        lastdate = datetime.datetime(2013,1,10,23,55)

        self.assertAlmostEqual(datayield, 100, 0)
        self.assertAlmostEqual(packetyield, 100, 0)
        self.assertEqual(lastsample, lastdate)


        #Repeat for node 838
        theyield = yields.calcyield(838)

        lastsample, datayield, packetyield = theyield
        lastdate = datetime.datetime(2013,1,10,23,55)

        self.assertAlmostEqual(datayield, 100, 0)
        self.assertAlmostEqual(packetyield, 100, 0)
        self.assertEqual(lastsample, lastdate)


    def test_calculate_sip_1061(self):
        """Can we calcualte SIP nodes correrctly (node 1061)

        This skips every over sample so should be about 50%

        """
        theyield = yields.calcyield(1061)

        lastsample, datayield, packetyield = theyield
        lastdate = datetime.datetime(2013,1,10,23,55)

        #Accurate to the Integer
        self.assertAlmostEqual(datayield, 50, 0)
        self.assertAlmostEqual(packetyield, 50, 0)
        self.assertEqual(lastsample, lastdate)


    def test_calculate_sip_1063(self):
        """Can we calcualte SIP nodes correrctly (node 1063)

        Skips a sample every 15 mins (aprox 1/3rd missing)
        """
        theyield = yields.calcyield(1063)

        lastsample, datayield, packetyield = theyield
        lastdate = datetime.datetime(2013,1,10,23,55)

        #Accurate to the integer
        self.assertAlmostEqual(datayield, 66.6, 0)
        self.assertAlmostEqual(packetyield, 66.6, 0)
        self.assertEqual(lastsample, lastdate)
