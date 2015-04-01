""" energycalc - calculations regarding energy

"""
import datetime

GAS_TO_METERS = 2.83 #Convert to cubic meters
GAS_PULSE_TO_METERS = GAS_TO_METERS / 100.0  #As gas is in 100's of cubic feet
GAS_VOLUME = 1.022640 #Correction Value
GAS_COLORIFIC = 39.3  #Calorific Value
GAS_CONVERSION = 3.6  #kWh conversion factor

GAS_FT3_FACTOR = (GAS_PULSE_TO_METERS *
                  GAS_VOLUME * GAS_COLORIFIC / GAS_CONVERSION)


def resample(readings, period=datetime.timedelta(hours=1)):
    """ resample readings at a particular period with padding """
    next_t = None
    last_v = None
    for (time, value) in readings:
        if next_t is None:
            next_t = time + period
            last_v = value
        else:
            while time >= next_t:
                yield (next_t, last_v)
                next_t += period
            last_v = value
    yield next_t, last_v


def diff(readings):
    """ find difference between subsequent readings with time point at end """
    last_v = None
    for (time, value) in readings:
        if last_v is not None:
            yield (time, value - last_v)

        last_v = value


def scale(readings, multiplier):
    """ scale reading values by a factor """
    for (time, value) in readings:
        yield (time, value * multiplier)


def get_stats_gas_hour(pulse_readings,
                          as_daily=False):
    """ hourly or daily summary for gas
    """
    if as_daily:
        resampled = resample(pulse_readings,
                             period=datetime.timedelta(days=1))
    else:
        resampled = resample(pulse_readings,
                             period=datetime.timedelta(hours=1))

    return scale(diff(resampled), GAS_FT3_FACTOR)
