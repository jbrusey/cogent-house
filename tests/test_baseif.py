import unittest

import cogent.base.BaseIF as BaseIF


class test_baseif(unittest.TestCase):
    """Tests for the baseIF class"""

    #As we dont want to have several baseIF's knocking around
    @classmethod 
    def setUpClass(cls):
        #Create a baseIF
        print "Creating BIF"
        cls.bif = BaseIF.BaseIF("sf@localhost:9002")
        pass

    @classmethod
    def tearDownClass(cls):
        print "Tearing Down BIF"
        cls.bif.finishAll()
        pass

    def testRecieve(self):
        pass

    def testTransmit(self):
        pass


