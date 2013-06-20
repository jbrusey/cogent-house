import unittest
from pyramid import testing


NAVBAR = ["timeseries",
          "exposure",
          "electricity",
          "admin",
          "databrowser",
           ]

from cogentviewer.views import homepage
import base

class TestUtils(unittest.TestCase):
    def setUp(self):
        request = testing.DummyRequest()
        config = testing.setUp(request = request)

        #And Register some routes
        config.add_route('home', '/')
        for item in NAVBAR:
            config.add_route(item,"{0}/".format(item))

        self.config = config

    def tearDown(self):
        testing.tearDown()

    def testNav(self):
        request = testing.DummyRequest()
        result = homepage.genHeadUrls(request)
        print result

class TestViews(base.FunctionalTest):
    """Testing for all views,  basic does the page load"""

    def testHome(self):
        """Testing Homepage View"""
        #Does our homepage load as expected
        res = self.testapp.get("/")
        self.failUnlessEqual(res.status_int,200)
        

    def testTimeseries(self):
        """Testing Time Series View"""
        res = self.testapp.get("/timeseries")
        self.failUnlessEqual(res.status_int,200)

    def testExpose(self):
        """Testing Exposure View"""
        res = self.testapp.get("/exposure")
        self.failUnlessEqual(res.status_int,200)

    def testAdmin(self):
        """Testing Admin View"""
        res = self.testapp.get("/admin")
        self.failUnlessEqual(res.status_int,200)

    def testDatabrowse(self):
        """Testing Databrowser View"""
        res = self.testapp.get("/data")
        self.failUnlessEqual(res.status_int,200)        
        
    
    pass
