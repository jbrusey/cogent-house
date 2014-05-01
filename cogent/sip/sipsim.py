"""

 Sipsim - named tuple version

 cogent.sip.sipsim

Versions:

0.1a1 jpb 27/4/14 use sequence numbers to identify which paths should
be shown as dashed.

"""
import random
import sys
import csv
import types
from collections import namedtuple
from math import sqrt
from datetime import timedelta

__version__ = "0.1a2"

# PhenomTuple consists of:

# sp - spline approximation to the original value
# ev - True if a SIP event occurred
# ls - last smoothed value (at the event)
# lt - last smoothed delta
# s - estimated / smoothed value
# t - estimated / smoothed delta
# xn - value with noise
# x - original value (if simulating)
# v - velocity or rate of change
# dashed - whether or not path up to here should be dashed
#          due to sequence number issues.

PhenomTuple = namedtuple('PhenomTuple',
                         'dt, sp, ev, ls, lt, s, t, xn, x, v, dashed')

# NULL_PHENOM can be used to make a new tuple using _replace to only
# supply certain elements.

NULL_PHENOM = (PhenomTuple(
    dt=None,
    x=None,
    v=None,
    sp=None,
    ev=None,
    ls=None,
    lt=None,
    s=None,
    t=None,
    xn=None,
    dashed=None
    ))


class Phenom(object):
    """ Phenom generates a randomly walking phenomena data stream
    Outputs: x, v
    """
    def __init__(self,
                 init_x=0.,
                 init_v=0.,
                 accel_var=0.):
        self.init_x = init_x
        self.init_v = init_v
        self.accel_var = accel_var

    def __iter__(self):
        while True:
            yield NULL_PHENOM._replace(x=self.init_x,
                              v=self.init_v)
            self.init_x += self.init_v
            self.init_v += (20 - self.init_x) * 0.01
            self.init_v += random.gauss(0, self.accel_var)


class PhenomCsvFile(object):
    """ PhenomCsvFile generates a data stream based on a single column
    of an input file.
    Outputs: xn
    """
    def __init__(self,
               filename=None,
               delimiter=',',
               column=0):
        self.file = csv.reader(open(filename, 'rb'), delimiter=delimiter)
        self.column = column

    def __iter__(self):
        for row in self.file:
            # assumed we know noisy value but not true value or velocity
            yield NULL_PHENOM._replace(xn=float(row[self.column]))


class Noise(object):
    """ Noise takes a raw phenom input and adds noise
    Inputs: x
    Outputs: xn
    """
    def __init__(self,
                 src=None,
                 var=0.):
        self.phen = src
        self.var = var

    def __iter__(self):
        for pt1 in self.phen:
            yield pt1._replace(xn=ptup.x + random.gauss(0, self.var))


class Dewma(object):
    """ Dewma takes a noisy phenomena input and provides a smoothed
    estimate of value and rate of change.
    Inputs: xn
    Outputs: s, t
    """
    def __init__(self,
               src=None,
               alpha=0.,
               beta=0.):
        self.src = src
        self.alpha = alpha
        self.beta = beta
        self.si = None
        self.ti = None

    def __iter__(self):
        for ptup in self.src:
            if self.si is None:
                si = ptup.xn
                ti = 0.
            else:
                si = self.alpha * ptup.xn + (1 - self.alpha) * (self.si + self.ti)
                ti = self.beta * (si - self.si) + (1 - self.beta) * self.ti
            yield ptup._replace(s=si,
                              t=ti)
            self.si = si
            self.ti = ti

class Event(object):
    """ Event takes a smoothed data stream and detects if the current value is
    predictable. If not, it reports an event.
    Input: s, t
    Output: ev, ls, lt
    """
    def __init__(self,
                 src = None,
                 threshold =0.5):
        self.src = src
        self.threshold = threshold
        self.last = None

    def __iter__(self):
        for ptup in self.src:
            if self.last is None or abs(self.last[0] - ptup.s) > self.threshold:
                yield ptup._replace(ev=True,
                                  ls=ptup.s,
                    lt=ptup.t)
                self.last = (ptup.s + ptup.t, ptup.t)
            else:
                yield ptup._replace(ev=False,
                                  ls=self.last[0],
                    lt=self.last[1])
                (s1, t1) = self.last
                self.last = (s1 + t1, t1)


class SipPhenom(object):
    """ expand out SIP data from the database into a time series to
    allow a reconstruction

    If a gap in sequence numbers is detected, it could be because of
    missed packets or due to a reset (if the sequence number goes to
    zero).

    Input: tuple with (datetime, value, delta, seq)
    Output: PhenomTuple with dt, ev, ls, lt, s, t, dashed
    """
    def __init__(self,
                 src=None,
                 seq_max=256,
                 interval=timedelta(minutes=5),
                 duplicate_interval=timedelta(seconds=20)):
        self.src = src
        self.interval = interval
        self.duplicate_interval = duplicate_interval
        self.seq_max = seq_max

    def __iter__(self):
        first = True
        last_dt = None
        last_seq = None
        for (date, value, delta, seq) in self.src:
            if first:
                yield NULL_PHENOM._replace(ev=True,
                                           ls=value,
                                           lt=delta,
                                           s=value,
                                           t=delta,
                                           dt=date,
                                           dashed=False
                                           )
                (last_s, last_t) = (value, delta)
                first = False

            elif date - last_dt > self.duplicate_interval:
                # yield records for each period from last_dt until < dt
                expected_seq = (last_seq + 1) % self.seq_max
                dashed = seq != expected_seq
                while date - last_dt > self.interval + self.duplicate_interval:
                    last_s += last_t
                    last_dt = last_dt + self.interval
                    yield NULL_PHENOM._replace(ev=False,
                                               ls=last_s,
                                               lt=last_t,
                                               dt=last_dt,
                                               dashed=dashed
                                               )

                yield NULL_PHENOM._replace(ev=True,
                                           ls=value,
                                           lt=delta,
                                           s=value,
                                           t=delta,
                                           dt=date,
                                           dashed=dashed
                                           )
                (last_s, last_t) = (value, delta)
            last_seq = seq

            last_dt = date

#------------------------------------------------------------
# spline calculations
#------------------------------------------------------------

class Spline(object):
    """ Spline - virtual class that helps with calculating polynomial
    and generating the resulting value
    """
    def __init__(self, poly, steps):
        self.poly = poly
        self.steps = steps

    def calc_poly(self, t):
        total = 0.
        for v in self.poly:
            total = total * t + v
        return total

    def __iter__(self):
        for t in range(1, self.steps+1):
            yield self.calc_poly(t * 1./(self.steps))

class QuadStartSpline(Spline):
    """ Quadratic start spline
    a - start point (x_0)
    b - end point (x_{n-1})
    c - gradient at start point (\dot{x}_0)
    steps - number of steps to generate over
    """
    def __init__(self, a, b, c, steps):
        c *= steps
        Spline.__init__(self,
                         [ b - a - c,
                           c,
                           a],
                         steps)

class QuadEndSpline(Spline):
    """ Quadratic end spline
    a - start point (x_{n-1})
    b - end point (x_n)
    c - gradient at end point (\dot{x}_n)
    """
    def __init__(self, a, b, c, steps):
        c *= steps
        Spline.__init__(self,
                        [ a - b + c,
                          -2 * a + 2 * b - c,
                          a],
                        steps)

class CubicSpline(Spline):
    """ Cubic spline that meets the start and end points and gradients
    a - start point
    b - start gradient
    c - end point
    d - end gradient
    steps - number of steps
    """
    def __init__(self,
                 a,b,c,d, steps):
        # apply the chain rule to convert gradient to be in terms of f'(t) rather than f'(x)
        b *= steps
        d *= steps
        Spline.__init__(self,
                         [2 * a + b - 2 * c + d,
                          -3 * a - 2 * b + 3 * c - d,
                          b,
                          a],
                          steps)

class Reconstruct(object):
    """ Spline based reconstruction using a single cubic spline
    """
    def __init__(self,
                 src = None):
        self.src = src
        self.stack = []
        self.last = None

    def __iter__(self):
        for ptup in self.src:
            self.stack.append(ptup)
            if ptup.ev:
                if self.last is not None:
                    # reconstruct spline between last and current
                    spline = CubicSpline(self.last[0],
                                         self.last[1],
                        ptup.s,
                        ptup.t,
                        len(self.stack))

                    for v in spline:
                        pt1 = self.stack.pop(0)
                        yield pt1._replace(sp=v)
                    assert len(self.stack) == 0
                else:
                    for pt1 in self.stack:
                        yield pt1._replace(sp=pt1.s)
                    self.stack = []

                self.last = (ptup.s, ptup.t)


class PartSplineReconstruct(object):
    """ Simple spline reconstruction based on two quadratic splines that meet
    (not smoothly) at an extrapolated n-1 point.

    - given (a) x0 and xdot0 giving initial linear extrapolation
    - (b) xn and xdotn giving eventful end point
    - and threshold (epsilon)
    - calculate (c) extrapolated limits to x(n-1) based on threshold
    and x0, xdot0
    - calculate (d) reverse extrapolated estimate of x(n-1) from xn, xdotn
    - if d < c^- use c^-, if > c+ use c+, else use d
    - calculate spline that goes through d, xn and has slope xdotn at xn
    Input: ev, ls, lt, s, t
    Output: sp
    """

    def __init__(self,
                 src=None,
                 threshold=None):
        self.src = src
        self.stack = []
        self.last = None
        self.threshold = threshold

    def __iter__(self):
        for ptup in self.src:
            self.stack.append(ptup)
            if ptup.ev:
                if ptup.dashed:
                    # linear interpolate
                    if self.last is not None:
                        start_x = self.last[0]
                    else:
                        start_x = self.stack[0].ls
                    gradient = (ptup.ls - start_x) * 1. / len(self.stack)
                    for i, item in enumerate(self.stack):
                        yield item._replace(sp=gradient * (i+1) + start_x)
                    self.stack = []
                elif self.last is not None:
                    # find xhat_1
                    (lx, lxdot) = (ptup.ls, ptup.lt)
                    lx_1 = lx - lxdot
                    lx_1upper = lx_1 + self.threshold
                    lx_1lower = lx_1 - self.threshold

                    xhat_1 = ptup.s - ptup.t
                    # bound
                    if xhat_1 > lx_1upper:
                        xhat_1 = lx_1upper
                    elif xhat_1 < lx_1lower:
                        xhat_1 = lx_1lower

                    # reconstruct spline between initial point and gradient and
                    # n-1 point

                    start_spline = QuadStartSpline(self.last[0],
                                                   xhat_1,
                                                   self.last[1],
                                                   len(self.stack)-1)
                    end_spline = QuadEndSpline(xhat_1,
                                               ptup.s,
                                               ptup.t,
                                               1)

                    for v in start_spline:
                        yield self.stack.pop(0)._replace(sp=v)
                    for v in end_spline:
                        yield self.stack.pop(0)._replace(sp=v)

                    assert len(self.stack) == 0
                else:
                    for ptup in self.stack:
                        yield ptup._replace(sp=ptup.s)
                    self.stack = []

                self.last = (ptup.s, ptup.t)


class QuarticSpline(Spline):
    def __init__(self,
                 a,b,c,d,e,s, steps):
        assert s > 0 and s < 1
        b *= steps
        d *= steps
        s2 = s * s
        s3 = s * s2
        A =  -( a * (2 * s3 - 3 * s2 + 1) +
                b * (s2 - 2 * s + 1) * s +
                s2 * (d *(s - 1) - c *(2 * s - 3)) - e
            ) / ((s - 1) * (s - 1) * s2)
        Spline.__init__(self,
                        [ A,
                          -2 * A + 2 * a + b - 2 * c + d,
                          A - 3 * a - 2 * b + 3 * c - d,
                          b,
                          a],
                          steps
            )




class ReconstructQuartic(object):
    """ Spline with power 4 polynomial

    """
    def __init__(self,
                 src = None,
                 threshold = 0.5
                 ):
        self.src = src
        self.threshold = threshold
        self.stack = []
        self.last = None

    def __iter__(self):
        for ptup in self.src:
            self.stack.append(ptup)
            if ptup.ev:
                if self.last is not None:
                    # reconstruct spline between last and current

                    steps = len(self.stack)

                    spline = CubicSpline(self.last[0], self.last[1], ptup.s, ptup.t, steps)

                    k1 = (steps // 2)

                    xk1 = 0.5 #(steps - 1) * 1. / steps
                    r = self.last[0] + k1 * self.last[1]
                    h = spline.calc_poly(xk1)

                    if h > r + self.threshold:
                        e = r + self.threshold

                    elif h < r - self.threshold:
                        e = r - self.threshold
                    else:
                        e = None

                    if e is not None:
                        spline = QuarticSpline(self.last[0],
                                               self.last[1],
                                               ptup.s,
                                               ptup.t,
                                               e,
                                               xk1,
                                               steps)
                    for v in spline:
                        yield self.stack.pop(0)._replace(sp=v)

                    assert len(self.stack) == 0
                else:
                    for pt1 in self.stack:
                        yield pt1._replace(sp=pt1.s)
                    self.stack = []
                self.last = (ptup.s, ptup.t)


def flat(ilist):
    """ flatten a list of tuples within tuples """
    rlist = []
    for item in ilist:
        if type(item) is types.TupleType:
            rlist.extend(flat(item))
        else:
            rlist.append(item)
    return rlist


def test():
    """ testing method """
    i = 0
    random.seed(1000)
    sse = 0.
    sse2 = 0.
    for pt1 in (Reconstruct(
            src=Event(
                src=Dewma(alpha=0.1,
                                beta=0.4,
                                src=Noise(var=0.25,
                  src=Phenom(init_x=23.,
                             init_v=0.1,
                             accel_var=0.0005)))))):
        err = pt1.sp - pt1.s

        err2 = pt1.ls - pt1.s
        sse += err * err
        sse2 += err2 * err2
        #print " ".join([str(ss) for ss in flat(pt1)])
        i += 1
        if i > 100000:
            break

    print >>sys.stderr, ("rmse in spline = {}, rmse in linear interp = {}"
                         .format(sqrt(sse/i), sqrt(sse2/i)))


if __name__ == "__main__":
    test()
