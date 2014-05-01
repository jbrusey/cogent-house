import unittest
from distutils.version import StrictVersion as V
import cogent.sip.sipsim
from cogent.sip.sipsim import SipPhenom
from datetime import datetime, timedelta

class TestSipPhenom(unittest.TestCase):
    """ unit tests for sipphenom
    """
    def test1(self):
        """ basic test """
        tvd = [(0, 1, 0, 1),
              (3, 2, 1./4, 2),
              (7, 3, -1./13, 3),
              (20, 2, 0, 4)]
        data = []
        now = datetime.utcnow()
        for (t, v, d, s) in tvd:
            data.append((now + timedelta(minutes=5*t), v, d, s))
            #for r in data:
            #print r

        count = 0
        last_dt = None
        for ptup in SipPhenom(src=data):
            #print count, ptup
            #print last_dt, ptup.dt
            self.assertTrue(last_dt is None or
                            ptup.dt > last_dt)
            self.assertTrue(ptup.dt is not None)
            last_dt = ptup.dt
            count += 1

        self.assertEquals(21, count)

    def test2(self):
        """ from a single data element, only one row should be
        generated """
        data = [(datetime.utcnow(), 1, 0, 3)]

        self.assertEquals(1, len(list(SipPhenom(src=data))))

    def test3(self):
        """ from two data elements that are at consecutive five min
        periods, two rows should be generated """

        db1 = [(datetime.utcnow(), 1, 0, 4),
              (datetime.utcnow() + timedelta(minutes=5), 2, 0, 5)]
        self.assertEquals(2, len(list(SipPhenom(src=db1))))


    def test4(self):
        """ test that sipphenom puts dashed indicators in the right
        place
        """
        # first make sure that the version of sipsim is right
        self.assertTrue(V(cogent.sip.sipsim.__version__) >= V("0.1a1"))
        tvd = [(0, 1, 0, 1),
              (3, 2, 1./4, 2),
              (7, 3, -1./13, 3),
              (20, 2, 0, 5)]  # missed 4
        data = []
        now = datetime.utcnow()
        for (t, v, d, s) in tvd:
            data.append((now + timedelta(minutes=5*t), v, d, s))

        count = 0
        last_dt = None
        for ptup in SipPhenom(src=data):
            #print count, ptup
            #print last_dt, ptup.dt
            self.assertTrue(last_dt is None or
                            ptup.dt > last_dt)
            self.assertTrue(ptup.dt is not None)
            intvl = int((ptup.dt - now).total_seconds() /
                        timedelta(minutes=5).total_seconds())
            # print intvl, ptup.dashed
            self.assertTrue(not (intvl > 7 and intvl <= 20) or
                            ptup.dashed)
            self.assertTrue(intvl > 7 and intvl <= 20 or
                            not ptup.dashed)
            last_dt = ptup.dt
            count += 1

        self.assertEquals(21, count)

    def test5(self):
        """ test that sipphenom puts dashed indicators in the right
        place - particularly for resets (goes back to zero)
        """
        # first make sure that the version of sipsim is right
        self.assertTrue(V(cogent.sip.sipsim.__version__) >= V("0.1a1"))
        tvd = [(0, 1, 0, 254),
               (3, 2, 1./4, 255),
               (7, 3, -1./13, 0),  # wrap around
               (20, 2, 0, 1),
               (22, 2, 0, 0),  # reset
               (25, 2, 1, 1)]
        data = []
        now = datetime.utcnow()
        for (t, v, d, s) in tvd:
            data.append((now + timedelta(minutes=5*t), v, d, s))

        count = 0
        last_dt = None
        for ptup in SipPhenom(src=data):
            #print count, ptup
            #print last_dt, ptup.dt
            self.assertTrue(last_dt is None or
                            ptup.dt > last_dt)
            self.assertTrue(ptup.dt is not None)
            intvl = int((ptup.dt - now).total_seconds() /
                        timedelta(minutes=5).total_seconds())
            # print intvl, ptup.dashed
            self.assertTrue(not (intvl > 20 and intvl <= 22) or
                            ptup.dashed)
            self.assertTrue(intvl > 20 and intvl <= 22 or
                            not ptup.dashed)
            last_dt = ptup.dt
            count += 1

        self.assertEquals(26, count)


if __name__ == "__main__":
    unittest.main()
