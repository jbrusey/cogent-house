"""
Cogent Tools
------

This file is part of Cogent Tools.

Cogent Tools is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Cogent Tools is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Cogent Tools.  If not, see <http://www.gnu.org/licenses/>.
"""

"""@file kalman.py

@brief Simple Kalman filter


This is a very cut down Kalman filter based on a single sensor point.

I have also implemeneted a Numeric version, This will work on the gumstix,
I shall leave the original numpy version for some speed comparisons :)


@author James Brusey <j.brusey@coventry.ac.uk>
@author Dan Goldsmith <goldsmid@coventry.ac.uk> (Numeric Conversion)
"""

from numpy import *
import time


class Ewma:
    """ @brief Exponentially weighted moving average

    """
    def __init__(self, x_init = 0., x_dinit = 0., alpha = 0.1, beta = 0.1):
        """@brief initialise Ewma filter for single data point
        
        @param x_init initial guess
        """
        self.xhat = x_init
        self.xhatd = x_dinit
        self.alpha = alpha
        self.beta = beta
        self.prev_time = 0.

    def filter(self, zk, t):
        """@brief filter for one time step

        @param zk sensor value 
        @param t time that measurement was taken
        """

        y = self.xhatd + self.alpha * (zk - self.xhat - self.xhatd)
        yd = self.beta * (y - self.xhatd)
        
        self.xhat = self.xhat + y
        self.xhatd = self.xhatd + yd
       
               
        return (self.xhat,self.xhatd)

