"""
.. codeauthor::  Ross Wiklins
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>

"""

from sqlalchemy import Column, String

import meta

class LastReport(meta.Base, meta.InnoDBMix):
    """
    Class to deal with LastReports
	This holds details of the last report E-Mailed to chuser

    :var String name: Name
    :var String value: Value

    """

    __tablename__ = "LastReport"

    name = Column(String(40), primary_key=True)
    value = Column(String(4096))
