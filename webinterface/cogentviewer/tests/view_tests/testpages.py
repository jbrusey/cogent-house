"""
Very simple testing of views,
Can we:
  * Login
  * Navigate
  * Logout

"""

NAVBAR = ["timeseries",
          "exposure",
          "electricity",
          "admin",
          "databrowser",
          "export",
          "serverstatus"
           ]

NAVLEN = 6

import cogentviewer.tests.base as base

class TestViews(base.FunctionalTest):
    """Testing for all views,  basic does the page load"""

    def setUp(self):
        super(base.FunctionalTest, self).setUp()
        res = self.testapp.post("/login",
                                {"username":"test",
                                 "password":"test",
                                 "submit":""})

    def tearDown(self):
        super(base.FunctionalTest, self).tearDown()
        res = self.testapp.get("/logout")

    def testHome(self):
        """Testing Homepage View"""
        #Does our homepage load as expected
        res = self.testapp.get("/")
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.content_type, "text/html")
        res.mustcontain("<title>Homepage</title>")

    def testNotLogin(self):
        """Testing what happens if we are not logged in"""
        self.testapp.get("/logout")

        res = self.testapp.get("/")
        res.mustcontain("<title>Login</title>")

        res = self.testapp.get("/timeseries")
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.content_type, "text/html")
        res.mustcontain("<title>Login</title>")

        res = self.testapp.get("/export")
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.content_type, "text/html")
        res.mustcontain("<title>Login</title>")

    def testTimeseries(self):
        res = self.testapp.get("/timeseries", extra_environ=dict(group='user'))
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.content_type, "text/html")
        self.assertNotIn("<title>Login</title>", res)

    def testExpose(self):
        """Testing Exposure View"""
        res = self.testapp.get("/exposure")
        self.failUnlessEqual(res.status_int, 200)
        self.assertNotIn("<title>Login</title>", res)

    def testExport(self):
        """Testing Export View"""
        res = self.testapp.get("/export")
        self.failUnlessEqual(res.status_int, 200)
        self.assertNotIn("<title>Login</title>", res)

    def testAdmin(self):
        """Testing Admin View"""
        res = self.testapp.get("/admin")
        self.failUnlessEqual(res.status_int, 200)
        self.assertNotIn("<title>Login</title>", res)

    def testServer(self):
        """Testing Server View"""
        res = self.testapp.get("/server")
        self.failUnlessEqual(res.status_int, 200)
        self.assertNotIn("<title>Login</title>", res)
