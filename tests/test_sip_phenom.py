import unittest

from cogent.sip.sipsim import SipPhenom, flat
from datetime import datetime, timedelta

class TestSipPhenom(unittest.TestCase):
    def test1(self):
        tvd = [(0, 1, 0, 1),
              (3, 2, 1./4, 2),
              (7, 3, -1./13, 3 ),
              (20, 2, 0, 4)]
        db = []
        dt = datetime.utcnow()
        for (t, v, d, s) in tvd:
            db.append((dt + timedelta(minutes=5*t), v, d, s))
            #for r in db:
            #print r

        c = 0
        last_dt = None
        for pt in SipPhenom(src=db):
            #print c, pt
            #print last_dt, pt.dt
            self.assertTrue(last_dt is None or
                            pt.dt > last_dt)
            self.assertTrue(pt.dt is not None)
            last_dt = pt.dt
            c +=1

        self.assertEquals(21, c)

    def test2(self):
        db = [(datetime.utcnow(), 1, 0, 3)]
        c = 0
        for pt in SipPhenom(src=db):
            c +=1

        self.assertEquals(1, c)

    def test3(self):
        db = [(datetime.utcnow(), 1, 0, 4),
              (datetime.utcnow() + timedelta(minutes=5), 2, 0, 5)]
        c = 0
        for pt in SipPhenom(src=db):
            c +=1

        self.assertEquals(2, c)

if __name__ == "__main__":
    unittest.main()
