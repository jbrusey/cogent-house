"""
unit tests that can be done offline
"""

import random
from pytest import approx

from dewma import Ewma


def testKalmanDelta():
    DEWMA = Ewma(x_init=10.0, x_dinit=1 / 64.0)
    sse = 0.0
    for i in range(1, 2001):
        z = (i / 64.0) + 10.0
        v = DEWMA.filter(z, i * 1024)
        err = v[0] - z
        sse += err * err

    print(v[0])
    print(v[1])
    print(sse)

    assert v[0] == 10.0 + 2000.0 / 64.0
    assert v[1] == 1.0 / 64.0
    assert sse == 0.0


def testKalmanDelta2():
    DEWMA = Ewma(x_init=10.0, x_dinit=1 / 64.0, alpha=0.01, beta=0.001)
    sse = 0.0
    sse2 = 0.0
    for i in range(1, 6001):
        z = ((i / 64.0) + 10.0) + random.gauss(0, 1.0)
        v = DEWMA.filter(z, i * 1024)
        err = v[0] - z
        err2 = v[1] - 1 / 64.0
        sse += err * err
        sse2 += err2 * err2

    print(v[0])
    print(v[1])
    print(sse)
    print(sse2)

    assert v[0] == approx(10.0 + 6000.0 / 64.0, abs=0.5)
    assert v[1] == approx(1.0 / 64.0, rel=0.01)
    assert sse < 6000


"""       
    def testKalmanDeltaNoise(self):

        self.ewma = Ewma(x_init = 10.)
        self.kd = KalmanDelta(t_init = 0, x_init=array([[10.], [0.02]], 'f4'), 
                              accel=1e-7, R=(0.05 * 0.05),
                              P_init = array([[0.,0.],[0.,0.]], 'f4'))
        kd2 = KalmanDelta(t_init = 0, x_init=array([[10.], [0.02]], 'f4'), 
                          accel=1e-7, R=(0.05 * 0.05),
                          P_init = array([[0.,0.],[0.,0.]], 'f4'))
        sse = 0.
        sse2 = 0.
        bias = 0.
        bias2 = 0.
        random.seed(1.)
        for i in xrange(1,2001):
            z = ((i / 50.) + 10.) 
            z2 = z + random.gauss(0, 0.05)
            v = self.kd.filter(z2, i)
            v2 = self.ewma.filter(z2, i)
            v3 = kd2.filter(z, i)
            #if i == 1: print "i=1:",z, z2, v, v3

            #print v

            err = v[0] - z
            err2 = v2[0] - z
            bias += err
            bias2 += err2
            #print err
            sse += err * err
            sse2 += err2 * err2

        #print "testKalmanDeltaNoise", v, v2[0], bias, bias2
        #print sse, sse2


        self.assertAlmostEquals(v[1], 0.02, 4)
        self.assertAlmostEquals(v[0], 50., 1)

        self.assertAlmostEquals(sse / 2000, 0, 3)
        
    def testKalmanDeltaSineDiscretised(self):
        kd2 = KalmanDelta(t_init = 0, x_init=array([[0.], [1.]], 'f4'), 
                          accel=0.02, R=(0.05 * 0.05),
                          P_init = array([[0.,0.],[0.,0.]], 'f4'))
        sse = 0.
        for i in xrange(1,2002):
            z = math.sin(i / 2000. * math.pi)

            z2 = math.floor(z * 10. + 0.5) / 10.
            v = kd2.filter(z2, i)

            err = v[0] - (z)
            #print err
            sse += err * err
        mse=sse / 2001.
        #print mse
        self.assert_(sse / 2001. < 6., "mse was too large %f" % (sse/2001.))


    def testKalmanDeltaSineDiscretisedRand(self):
        kd2 = KalmanDelta(t_init = 0, x_init=array([[0.], [1.]], 'f4'), 
                          accel=0.02, R=(2*0.05 * 0.05),
                          P_init = array([[0.,0.],[0.,0.]], 'f4'))

        sse = 0.
        for i in xrange(2001):
            z = math.sin(i / 2000. * math.pi)

            z2 = math.floor(z * 10. + 0.5) / 10.
            #z2 = z2 + random.gauss(0, 0.05)
            z2 = z2 + (random.randint(0, 65535) / 655360. - 0.05)
            v = kd2.filter(z2, i)

            err = v[0] - (z)
            #print err
            sse += err * err
        #print sse / 2001.
        self.assertAlmostEquals(sse / 2001., 0, 2)
"""
