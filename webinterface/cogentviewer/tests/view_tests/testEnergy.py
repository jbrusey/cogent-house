import unittest2 as unittest
import datetime
from cogentviewer.views import restService
from collections import namedtuple

class EnergyTest(unittest.TestCase):

    def test_getstatsgashour(self):
        """ test getStatsGasHour """
        Pulse = namedtuple('Pulse', 'time, value')

        result = restService.getStatsGasHour([Pulse(t, v) for (t, v) in
                                  [(datetime.datetime(2015, 02, 14), 46116),
                                   (datetime.datetime(2015, 03, 15), 61347),
]],
                                 daily=True)
        GAS_TO_METERS = 2.83 #Convert to cubic meters
        GAS_PULSE_TO_METERS = GAS_TO_METERS / 100.0  #As gas is in 100's of cubic feet
        GAS_VOLUME = 1.022640 #Correction Value
        GAS_COLORIFIC = 39.3  #Calorific Value
        GAS_CONVERSION = 3.6  #kWh conversion factor

        self.assertEquals(result[0][1], (61347 - 46116) * GAS_PULSE_TO_METERS *
                     GAS_VOLUME * GAS_COLORIFIC / GAS_CONVERSION)
        #self.assertAlmostEquals(result[0][1], 4812.02)
