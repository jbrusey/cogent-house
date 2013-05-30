import unittest

from cogent.sip.sipsim import QuarticSpline

class TestQuartic(unittest.TestCase):
    def testQ(self):
        spline = QuarticSpline(0,1,2,0,1.3, 0.8, 5)

        a = 0
        b = 1*5
        c = 2
        d = 0*5
        e = 1.3
        s = 0.8

        s2 = s * s
        s3 = s2 * s

        A =  -( a * (2 * s3 - 3 * s2 + 1) +
                b * (s2 - 2 * s + 1) * s +
                s2 * (d *(s - 1) - c *(2 * s - 3)) - e
            ) / ((s - 1) * (s - 1) * s2)


        testpoly = [A,
                    -2 * A + 5-4,
                    A - 10 + 6,
                    5,
                    0]

        for i in range(len(testpoly)):
            self.assertAlmostEquals( spline.poly[i], testpoly[i] )

if __name__ == "__main__":
    unittest.main()
