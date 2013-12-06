"""
Table to hold details of raw messages

.. module:: rawmessage

.. codeauthor::  Ross Wiklins
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>

"""

import meta

from sqlalchemy import Column, Integer, String, DateTime

class RawMessage(meta.Base, meta.InnoDBMix):
    """A Raw Message

    :var Integer id: Id
    :var Datetime time:
    :var String pickledObject:
    """

    __tablename__ = "RawMessage"


    id = Column(Integer, primary_key=True, autoincrement=False)
    time = Column(DateTime)
    pickedObject = Column(String(400))
