# temp 0.2 0.2
# hum 0.15 0.15
# battery 0.001 0.01
# co2 0.2 0.2
# aq 0.05 0.05
# voc 0.05 0.05

from dewma import Ewma

import csv
from datetime import datetime


def test():

    kd = None
    first_time = None

    with open("testVOC.csv", "rb") as ff:
        rdr = csv.reader(ff)
        print("time,x,xhat,dx")
        for r in rdr:
            dt = datetime.strptime(r[1], "%Y-%m-%d %H:%M:%S")
            v = float(r[2])
            if kd is None:
                first_time = dt
                kd = Ewma(x_init=v, x_dinit=0.0, alpha=0.05, beta=0.05)
            else:
                z2 = v
                x = kd.filter(z2, (dt - first_time).seconds)
                print(
                    dt.strftime("%s") + "," + str(v) + "," + str(x[0]) + "," + str(x[1])
                )


if __name__ == "__main__":

    test()
