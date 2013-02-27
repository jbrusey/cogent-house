from exposure import Exposure

import sys
import csv
from numpy import *
from datetime import datetime, timedelta

#t_band_list = [16., 18., 22., 27.]
#h_band_list = [45., 65., 85.]
#c_band_list = [600., 1000., 2500.]

def test():

    exp = None
    first_time = None

    with open("testTemp.csv", "rb") as ff:
        rdr = csv.reader(ff)
	print "time,x,xhat,dx"
        for r in rdr:
            n = int(r[0])
            dt = datetime.strptime(r[1], "%Y-%m-%d %H:%M:%S")
            v = float(r[2])
	    if exp is None:
                first_time = dt
                exp = Exposure(num_bands=5, 
                bandLimits=[16., 18., 22., 27.], 
                gamma=0.999986821294764
                )
	    else:
                z2 = v
                x = exp.filter(z2, (dt - first_time).seconds)
                print dt.strftime("%s")+","+str(v)+","+repr(x)
		  

if __name__ == "__main__":

    test()
