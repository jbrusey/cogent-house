"""
Metaclass to bring everything together in a simulation
of a Pyramid environment

This really just makes sure all database code is in the same place
meaning the DB is consistently initiated in all test cases.

:module author:  Daniel Goldsmtih <djgoldsmith@googlemail.com>
"""

import os
import unittest2 as unittest #Hax for python 2.6


import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)



from pyramid.config import Configurator
from paste.deploy.loadwsgi import appconfig
from pyramid import testing

from sqlalchemy.orm import sessionmaker
from sqlalchemy import engine_from_config

import cogentviewer.models.meta as meta
import cogentviewer.models as models

#Setup the Testing to load pyramid settings from the test.ini file
ROOT_PATH = os.path.dirname(__file__)
SETTINGS_PATH = os.path.join(ROOT_PATH, "../../","test.ini")

log.info("")
log.info("------------- TESTING START -------------")

def initDatabase():
    """Method to initialise the database"""

    log.debug("------- INITIALISE TESTING DATABASE ---------")

    #Setup and configure the code
    settings = appconfig('config:' + SETTINGS_PATH)

    #Setup the configurator
    config = Configurator(settings = settings)
    #Scan for all models
    config.scan("cogentviewer.models")

    engine = engine_from_config(settings, prefix="sqlalchemy.")
    log.debug("--> Database Engine Started: {0}".format(engine))

    #Create the tables
    log.debug("--> Creating Tables")
    meta.Base.metadata.create_all(engine)

    log.debug("--> Configuring Session")
    meta.Session.configure(bind=engine)
    #log.debug("Initialising SQL")
    #meta.Base.metadata.bind = engine
    log.debug("--> Adding Initial Data")
    models.populateData.init_data()
    #models.populateData.populate_data()
    #log.debug("----------------------------------------------")



#Check to see if we have a database all ready initialised (Avoids bug where the
#test overrides everything)
if meta.Base.metadata.bind is None:
    log.info("--> No Database Initiated")
    initDatabase()
    #populatedata()
    print "====================="

class BaseTestCase(unittest.TestCase):
    """Base class for testing"""

    @classmethod
    def setUpClass(cls):
        """Class method, called each time this is initialised"""
        #cls.config = testing.setUp()

        #Load settings from Configuration file
        log.debug("Init Test Class Database for {0}".format(cls.__name__))
        settings = appconfig('config:' + SETTINGS_PATH)
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        cls.Session = sessionmaker()
        #cls.Session.configure(bind=cls.engine)


    def setUp(self):
        """Called each time a test case is called,
        He we wrap the test case in Transaction Magic(TM)
        Meaning we can roll the test case back, returning the database to normal
        """
        connection = self.engine.connect()

        #Begin the Transaction
        self.transaction = connection.begin()

        #And bind the session
        self.session = self.Session(bind=connection)

    def tearDown(self):
        """
        Close the transaction and rollback after each test case is called
        """
        testing.tearDown()
        self.transaction.rollback()
        self.session.close()


class FunctionalTest(BaseTestCase):
    """ Add Functional Testing (for the web pages themselves) functionality"""

    @classmethod
    def setUpClass(cls):
        """
        New Setup Function, creates an app
        """
        #super(BaseTestCase, cls).setUpClass()

        #Load settings from predefined .ini file
        settings = appconfig('config:' + SETTINGS_PATH)
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        cls.Session = sessionmaker()

        #super(BaseTestCase, cls).setUp()
        from cogentviewer import main
        cls.app = main({}, **settings)

        from webtest import TestApp
        cls.testapp = TestApp(cls.app)

    def setUp(self):
        """Setup Transaction"""
        self.testapp.post("/login",
                          {"username":"test",
                           "password":"test",
                           "submit":""})

        connection = self.engine.connect()
        #Begin the Transaction
        self.transaction = connection.begin()
        #And bind the session
        self.session = self.Session(bind=connection)

    def tearDown(self):
        """Rollback and teardown transaction"""
        self.testapp.get("/logout")
        print "Rollback transaction"
        testing.tearDown()
        self.transaction.rollback()
        self.session.close()


class ModelTestCase(BaseTestCase):
    """Subclass to test models

    Tests the inherited functionality that should be present in all models
    """

    def testEq(self):
        #Placeholder to test for equality
        self.fail("You need to implement the Equality Test for this Model")

    def testCmp(self):
        #Placeholder to for cmp tests
        self.fail("You need to implement the CMP test for this Model")

    def assertReallyEqual(self, a, b):
        """Use overloaded testEq and testCmp methods
        to ensure equality tests are setup correctly"""
        # assertEqual first, because it will have a good message if the
        # assertion fails.
        self.assertEqual(a, b)
        self.assertEqual(b, a)
        self.assertTrue(a == b)
        self.assertTrue(b == a)
        self.assertFalse(a != b)
        self.assertFalse(b != a)
        self.assertEqual(0, cmp(a, b))
        self.assertEqual(0, cmp(b, a))

    def assertReallyNotEqual(self, a, b):
        """Ensure that the equality works when objects are
        not equal"""
        # assertNotEqual first, because it will have a good message if the
        # assertion fails.
        self.assertNotEqual(a, b)
        self.assertNotEqual(b, a)
        self.assertFalse(a == b)
        self.assertFalse(b == a)
        self.assertTrue(a != b)
        self.assertTrue(b != a)
        self.assertNotEqual(0, cmp(a, b))
        self.assertNotEqual(0, cmp(b, a))

    def _serialobj(self):
        """Helper method, return an object to serialise"""
        self.fail("You need to implement a serialObj method for this class")

    def _dictobj(self):
        """Helper method, return a dictionary representation of
        the _serialobj object"""
        self.fail("You need to implement a serialObj method for this class")

    def testSerialise(self):
        """Test Serialisation of objects"""
        theObj = self._serialobj()

        #convert to dictionary
        theDict = theObj.dict()

        #Convert Back
        newObj = models.newClsFromJSON(theDict)
        self.assertEqual(theObj, newObj)

    def testDict(self):
        """Test Conversion to a dictionary"""
        theItem = self._serialobj()
        theDict = self._dictobj()

        objDict = theItem.dict()
        self.assertIsInstance(objDict,dict)
        self.assertEqual(objDict, theDict)
