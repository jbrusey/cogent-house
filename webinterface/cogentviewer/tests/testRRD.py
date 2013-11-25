import unittest
import cogentviewer.views.rrdstore as rrdstore

import os
import os.path

RRDPATH = rrdstore.RRDPATH

class RRDTest(unittest.TestCase):
    def testInit(self):
        #Test if we can create RRD object
        print 
        expectedFd = os.path.join(RRDPATH,"500_500_500.rrd")
        print "Expected RRD item is {0}".format(expectedFd)

        #Check it doesn't exist
        self.assertFalse(os.path.exists(expectedFd))

        theRRD = rrdstore.RRDStore(500,500,500)
        #Now the RRD File should Exist
        self.assertTrue(os.path.exists(expectedFd))
        
        #Clean up 
        os.remove(expectedFd)
        #Check it doesn't exist
        self.assertFalse(os.path.exists(expectedFd))
        
        
