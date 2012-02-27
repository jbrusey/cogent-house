"""
Table to hold details of Occupiers

.. codeauthor::  Ross Wiklins 
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>

"""


import sqlalchemy
import logging
log = logging.getLogger(__name__)

import meta
Base = meta.Base

from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref



class Occupier(Base):
    """Class representing someone who lives in a house
    
    :var Integer id: Id
    :var Integer houseId: *fk* to :class:`cogentviewer.models.house.House`
    :var String name: Name of Resident
    :var String contactNumber: Contact Number
    :var DateTime startDate: 
    :var DateTime endDate:
    """


    __tablename__ = "Occupier"

    id = Column(Integer, primary_key=True)
    houseId = Column(Integer, ForeignKey('House.id'))
    name = Column(String(255))
    contactNumber = Column(String(20))
    startDate = Column(DateTime)
    endDate = Column(DateTime)
