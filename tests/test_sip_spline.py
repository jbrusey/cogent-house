import unittest
from cogent.sip.sipsim import (SipPhenom,
                               PartSplineReconstruct)
from datetime import datetime, timedelta
from tests.test_sip_phenom import my_total_seconds

class TestSipSpline(unittest.TestCase):
    """ test sipsim.PartSplineReconstruct """
    def test1(self):
        """ sequence 4 is missed, so we should have straight line
        interpolation between 3 and 5.
        """
        tvd = [(0, 1, 0, 1),
               (3, 2, 1./4, 2),
               (7, 3, -1./13, 3),
               (20, 3, 1./13, 5),  # missed seq 4
               (24, 1, 0, 9)]  # missed 6,7,8
        data = []
        now = datetime(2001, 1, 1)
        for (t, v, d, s) in tvd:
            data.append((now + timedelta(minutes=1*t), v, d, s))

        result = list(PartSplineReconstruct
                     (src=SipPhenom(src=data,
                                    interval=timedelta(minutes=1)),
                      threshold=0.1))
        for ptup in result:
            self.assertTrue(ptup.dashed is not None)
            intvl = int(my_total_seconds((ptup.dt - now)) /
                        my_total_seconds(timedelta(minutes=1)))
            if intvl >= 7 and intvl <= 20:
                self.assertEquals(ptup.sp, 3)
            if intvl > 20 and intvl <= 25:
                self.assertEquals(ptup.sp, (intvl - 20) * (1.-3.)/(24-20) + 3)


        for i, ptup in enumerate(result):
            intvl = int(my_total_seconds((ptup.dt - now)) /
                        my_total_seconds(timedelta(minutes=1)))
            self.assertEquals(i, intvl)

