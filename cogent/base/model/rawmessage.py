"""
Table to hold details of raw messages

.. module:: rawmessage

.. codeauthor::  Ross Wiklins 
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>

"""

import sqlalchemy
import logging
log = logging.getLogger(__name__)

import meta
Base = meta.Base


# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, backref


class RawMessage(Base,meta.InnoDBMix):
    """A Raw Message

    :var Integer id: Id
    :var Datetime time:
    :var String pickledObject:
    """

    __tablename__ = "RawMessage"


    id = Column(Integer,primary_key=True,autoincrement=False)
    time = Column(DateTime)
    pickedObject = Column(String(400))
    
