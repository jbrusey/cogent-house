"""

.. todo::

    Find out what this class is inteded to be used for


.. module:: host

.. codeauthor::  Ross Wiklins
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>
"""

import sqlalchemy

import meta

class Host(meta.Base, meta.InnoDBMix):
    """
    Table to hold information about Hosts

    :var integer id: id (pk)
    :var string hostname: name
    :var DateTime lastupdate: lastupdate
    """


    __tablename__ = "Host"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    hostname = sqlalchemy.Column(sqlalchemy.String(255))
    lastupdate = sqlalchemy.Column(sqlalchemy.DateTime)
