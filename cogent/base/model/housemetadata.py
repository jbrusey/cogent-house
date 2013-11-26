"""
.. codeauthor::  Ross Wiklins 
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>
"""

import meta


from sqlalchemy import Column, Integer, String, ForeignKey, Float
#from sqlalchemy.orm import relationship


class HouseMetadata(meta.Base, meta.InnoDBMix):
    """Table to hold Metadata about houses

    :var Integer id: id
    :var Integer houseId: *foreignKey* Id of :class:`cogentviewer.models.house.House` this beongs to
    :var string name: Name of metadata
    :var string description: Description of metadata
    :var string units: Units of Metadata
    :var float value: Value of metadata

    """
    __tablename__ = "HouseMetadata"

    id = Column(Integer, primary_key=True)
    houseId = Column(Integer, ForeignKey('House.id'))
    name = Column(String(255))
    description = Column(String(255))
    units = Column(String(20))
    value = Column(Float)

