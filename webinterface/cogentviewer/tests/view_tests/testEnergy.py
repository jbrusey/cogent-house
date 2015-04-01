import unittest2 as unittest
import datetime
from cogentviewer.views import energycalc
from collections import namedtuple

Pulse = namedtuple('Pulse', 'time, value')
GAS_TO_METERS = 2.83 #Convert to cubic meters
GAS_PULSE_TO_METERS = GAS_TO_METERS / 100.0  #As gas is in 100's of cubic feet
GAS_VOLUME = 1.022640 #Correction Value
GAS_COLORIFIC = 39.3  #Calorific Value
GAS_CONVERSION = 3.6  #kWh conversion factor

GAS_FT3_FACTOR = (GAS_PULSE_TO_METERS *
                  GAS_VOLUME * GAS_COLORIFIC / GAS_CONVERSION)


class EnergyTest(unittest.TestCase):
    """ test energy calculations """
    def test_getstatsgashour(self):
        """ test getStatsGasHour """

        data = [Pulse(t, v) for (t, v) in
                                  [(datetime.datetime(2015, 02, 14), 46116),
                                   (datetime.datetime(2015, 03, 15), 61347),
                               ]]

        result = energycalc.get_stats_gas_hour(data,
                                 as_daily=True)

        sum1 = sum([i for (_, i) in result])

        self.assertEquals(sum1, (61347 - 46116) * GAS_PULSE_TO_METERS *
                     GAS_VOLUME * GAS_COLORIFIC / GAS_CONVERSION)


    # def test_timing(self):
    #     """ time two approaches """
    #     data = [Pulse(t, v) for (t, v) in
    #                               [(datetime.datetime(2015, 02, 14), 46116),
    #                                (datetime.datetime(2015, 03, 15), 61347),
    #                            ]]

    #     iters = 10000
    #     import time
    #     start_t = time.time()
    #     for i in range(iters):
    #         result = restService.getStatsGasHour(data,
    #                              daily=True)

    #     old_t = time.time() - start_t

    #     start_t = time.time()
    #     for i in range(iters):
    #         result = my_get_stats_gas_hour(data, as_daily=True)
        
    #     new_t = time.time() - start_t

    #     print 'old took {} and new took {}'.format(old_t, new_t)
        
