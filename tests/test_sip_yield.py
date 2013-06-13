import unittest

from cogent.sip.calc_yield import calc_yield

class TestSipYield(unittest.TestCase):
    def test1(self):

        self.assertEquals(100.,calc_yield(7, 9, 15))

        self.assertEquals(100., calc_yield(286, 71, 100))
        self.assertEquals(100., calc_yield(286, 241, 24))

        self.assertEquals(10., calc_yield(1, 1, 10))

        self.assertEquals(100., calc_yield(1, 255, 0))
