"""
Class to hold details of objects and URLS that we need to push data to.

.. codeauthor::  Ross Wiklins 
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>
"""

import sqlalchemy
import logging
log = logging.getLogger(__name__)

import meta
Base = meta.Base

class UploadURL(Base,meta.InnoDBMix):
    """Table to hold URLS that we need to push data to.
    Each of these records represents a remote database connection.
    
    :var String url: URL of remote host to connect to 
    :var String dburl: SQLA database string to connect to
    :var Datetime lastUpdate: The last record that was sent to this url
    """
    __tablename__ = "UploadURL"
    url = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    dburl = sqlalchemy.Column(sqlalchemy.String)
    lastUpdate = sqlalchemy.Column(sqlalchemy.DateTime)


    
