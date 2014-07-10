"""
Table to hold details of Occupiers

.. codeauthor::  Ross Wiklins 
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>

"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

import meta

class Occupier(meta.Base, meta.InnoDBMix):
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
