import sys
import random
from math import sqrt
from pulp.sip.sipsim import Reconstruct, Dewma, Noise, Phenom, Event


def flat(ilist):
    """flatten a list of tuples within tuples"""
    rlist = []
    for item in ilist:
        if type(item) is tuple:
            rlist.extend(flat(item))
        else:
            rlist.append(item)
    return rlist


def test_sipsim():
    i = 0
    random.seed(1000)
    sse = 0.0
    sse2 = 0.0

    # create a phenomena with initial value 23 and initial velocity
    # 0.1 and accel of 0.0005, add some noise, then smooth with dewma,
    # then event trigger, then reconstruct

    for pt1 in Reconstruct(
        src=Event(
            src=Dewma(
                alpha=0.1,
                beta=0.4,
                src=Noise(
                    var=0.25, src=Phenom(init_x=23.0, init_v=0.1, accel_var=0.0005)
                ),
            )
        )
    ):
        err = pt1.sp - pt1.s

        err2 = pt1.ls - pt1.s
        sse += err * err
        sse2 += err2 * err2
        # print " ".join([str(ss) for ss in flat(pt1)])
        i += 1
        if i > 100000:
            break

    print(
        (
            "rmse in spline = {}, rmse in linear interp = {}".format(
                sqrt(sse / i), sqrt(sse2 / i)
            )
        ),
        file=sys.stderr,
    )
    # it would improve this code if there was a reason for these
    # particular errors to be expected.
    assert sqrt(sse / i) < 0.1
    assert sqrt(sse2 / i) < 0.25
