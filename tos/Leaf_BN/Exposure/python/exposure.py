from numpy import *
import time


class Exposure:
    """ @brief Exposure band calculations

    """
    def __init__(self, num_bands=4, bandLimits=[1,2,3,4], gamma=0. ):
        """@brief initialise Exposure filter
        
        @param num_bands Number of bands
        @param bandLimits Limits of where the bands ends
        @param gamma HalfLife
        """
        self.num_bands = num_bands
        self.bandLimits = bandLimits
        self.gamma = gamma
        #define bands
        self.bandCount=[]
        self.bandPCT=[]
        i=0
        while i < self.num_bands:
            self.bandCount.append(0.0)
            self.bandPCT.append(0.0)
            i+=1


    # find in which band a value falls.
    def findBand(self, k, bands):
	    assert k is not None
            for i in range(len(bands)):
                    if k <= bands[i]:
                            return i
            return len(bands)

    def filter(self, zk, t):
        """@brief filter for one time step

        @param zk sensor value 
        @param t time that measurement was taken
        """
        #decay all bands
        i=0
        while i < len(self.bandCount):
            self.bandCount[i]=self.bandCount[i]*self.gamma
            i+=1
        
        #find band and increase count
        self.bandCount[self.findBand(zk, self.bandLimits)] += 1
        
        #calc percentages
        i=0
        bandSum=0
        while i < len(self.bandCount):
            bandSum+=self.bandCount[i]
            i+=1

        i=0
        while i < len(self.bandPCT):
            self.bandPCT[i]=self.bandCount[i]/bandSum
            i+=1
               
        return (self.bandPCT)

