import unittest

from cogent.sip.sipsim import CubicSpline

class TestCubic(unittest.TestCase):
    def testC(self):
        spline = CubicSpline(0, 1, 2, 0, 5)

        testpoly = [1,
                    -4,
                    5,
                    0]

        for i in range(len(testpoly)):
            self.assertAlmostEquals( spline.poly[i], testpoly[i] )

if __name__ == "__main__":
    unittest.main()
