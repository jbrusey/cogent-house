"""
Table to hold details of Weather

.. module:: weather

.. codeauthor::  Ross Wiklins
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>

"""

from sqlalchemy import Column, DateTime, Float

import meta

class Weather(meta.Base, meta.InnoDBMix):
    """
    Table to deal with Weather

    :var DateTime time:
    :var Float outTemp:
    :var Float outHum:
    :var Float dew:
    :var Float gust:
    :var Float wSpeed:
    :var Float wDir:
    :var Float wChill:

    :var Float apparentTemp:
    :var Float rain:
    :var Float pressure:
    :var Float tempIn:
    :var Float humIn:

    """

    __tablename__ = "Weather"

    time = Column(DateTime, primary_key=True)
    outTemp = Column(Float)
    outHum = Column(Float)
    dew = Column(Float)

    gust = Column(Float)
    wSpeed = Column(Float)
    wDir = Column(Float)
    wChill = Column(Float)

    apparentTemp = Column(Float)

    rain = Column(Float)
    pressure = Column(Float)
    tempIn = Column(Float)
    humIn = Column(Float)
