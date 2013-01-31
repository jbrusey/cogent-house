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

DEFAULT_R = 0.0025
DEFAULT_ACCEL_COV = 1e-5

HIGH_COVARIANCE = 1e99

class KalmanSingle:
    """@brief Kalman filter for a single point measurement.
    
    A separate filter should be created for each measurand.

    @class KalmanSingle
    """


    def __init__(self, Q = 1e-5, x_init = 0., R = DEFAULT_R,
                 P_init = 99.):
        """@brief initialise Kalman filter for single data point
        
        @param Q process variance
        @param x_init initial guess
        @param R measurement variance estimate
        @param P_init initial covariance
        """
        self.Q = Q
        self.R = R
        self.xhat = x_init
        self.P = P_init


    def filter(self, zk, t, R = None):
        """@brief filter for one time step

        @param zk sensor value 
        @param t time (which is not relevant to this model)
        @param R measurement variance estimate
        """
        if not R:
            R = self.R

        # time update
        xhatminus = self.xhat
        Pminus = self.P + self.Q

        # measurement update
        if not zk:
            zz = self.xhat
        else:
            zz = zk
            
        y = zz - xhatminus
        S = Pminus + R
        # if missing value, set covariance high
        if not zk:
            S = S + 99.

        K = Pminus / S
        
        self.xhat = xhatminus + K * y
        self.P = (1 - K) * Pminus

        return (self.xhat, 0., self.P)

class NoFilter:

    def __init__(self,
                 x_init = 0.,
                 t_init = 0.,
                 R = DEFAULT_R):
        self.xhat = x_init
        self.t = t_init
        self.R = R

    def filter(self, zk, t, R = None):
        """ 
        """
        if not R:
            R = self.R
            
        dt = t - self.t
        v = zk - self.xhat
        self.xhat = zk
        self.t = t
        return (zk, v, R)


class KalmanDelta:
    """ @brief this version of the kalman filter assumes that rate of
    change of temperature is constant.

    Apologies for the interesting equasion layout,  Hopefully everything 
    is clear.
    """
    def __init__(self, 
                 accel = DEFAULT_ACCEL_COV, 
                 x_init = zeros((2, 1),'f4'), 
                 R = DEFAULT_R,
                 P_init = array([[HIGH_COVARIANCE, 0.],[0., HIGH_COVARIANCE]], 'f4'),
                 t_init = None, debug=False):
        """@brief initialise Kalman filter for single data point
        
        @param accel acceleration variance
        @param x_init initial guess
        @param R measurement variance estimate
        @param P_init initial covariance
        @param t_init initial time
        """
        self.accel = accel
        self.R = array([[R]], 'f4')
        self.xhat = x_init
        self.P = P_init
        # observation model
        self.H = array([[1.,0.]], 'f4')
        self.HT = transpose(self.H)
        if t_init == None:
            self.t = time.time()
        else:
            self.t = t_init
        self.debug = debug
        self.F = array([[1.,1.],
                        [0.,1.]], 'f4')
        self.FT = transpose(self.F)
        self.G = array([[1.],
                        [1.]], 'f4')
        self.GT = transpose(self.G)

    def filter(self, zk, t, R = None):
        """@brief filter for one time step

        @param zk sensor value 
        @param t time that measurement was taken
        """
        if not R:
            R = self.R

        # time update

        deltaT = t - self.t
        self.t = t

        self.F[0,1] = self.FT[1,0] = deltaT
        self.G[0,0] = self.GT[0,0] = deltaT * deltaT / 2.
        self.G[1,0] = self.GT[0,1] = deltaT

        Q = self.G * self.accel * self.GT   # process variance
        #Q = dot(dot(self.G, self.accel), self.GT)

        # note: no control part
        # (2x1) = (2x2) x (2x1)
        xhatminus = dot(self.F, self.xhat)
        if self.debug:
            print "xhatminus = ", xhatminus

        # (2x2) = (2x2) x (2x2) x (2x2) + (2x2)
        Pminus = self.F * self.P * self.FT + Q
        #Pminus = dot(dot(self.F, self.P), self.FT) + Q
        if self.debug:
            print "Pminus = ", Pminus


        # (1x1) = (1x1) - (1x2)*(2x1)
        if zk:
            y = asmatrix([[zk]]) - dot(self.H, xhatminus)
        else:
            y = asmatrix([[0.]])
        #y =  array([[zk]]) - dot(self.H, xhatminus)
        if self.debug:
            print "y = ", y

        # (1x1) = (1x2) x (2x2) x (2x1) + (1x1)
        S = dot(dot(self.H, Pminus), self.H.T) + self.R
        #S = dot(dot(self.H, Pminus), self.HT) + R
        if self.debug:
            print "S = ", S


        # (2x1) = (2x2) x (2x1) x (1x1)
        #K = Pminus * self.HT * LinearAlgebra.inverse(S)
        K = dot(Pminus, self.HT) / S[0,0]
        if self.debug:
            print "K = ", K

        # (2x1) = (2x1) + (2x1) x (1x1)
        #self.xhat = xhatminus + K * y
        self.xhat = xhatminus + dot(K, y)
        if self.debug:
            print "xhat = ", self.xhat

        
        # (2x2) = ((2x2) - (2x1) x (1x2)) x (2x2)
        self.P = dot(identity(2) - dot(K, self.H), Pminus)
        if self.debug:
            print "P = ", self.P

        return (self.xhat[0,0], self.xhat[1,0], self.P[0,0])





class Ewma:
    """ @brief Exponentially weighted moving average

    """
    def __init__(self, x_init = 0., alpha = 0.1):
        """@brief initialise Ewma filter for single data point
        
        @param x_init initial guess
        """
        self.xhat = x_init
        self.alpha = alpha


    def filter(self, zk, t):
        """@brief filter for one time step

        @param zk sensor value 
        @param t time that measurement was taken
        """

        y = zk - self.xhat

        self.xhat = self.alpha * y + self.xhat
        
        return (self.xhat, 0., 0.)

