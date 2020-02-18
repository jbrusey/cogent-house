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
    
    I did have the url as the primary key,  However it is may be possible we
    want to connect to multiple databases on one host. Therefore add a ID 

    :var integer Id: Id of upload object
    :var String url: URL of remote host to connect to 
    :var String dburl: SQLA database string to connect to
    :var Datetime lastUpdate: The last record that was sent to this url
    """
    __tablename__ = "UploadURL"
    id = sqlalchemy.Column(sqlalchemy.Integer,primary_key=True)
    url = sqlalchemy.Column(sqlalchemy.String(100))
    dburl = sqlalchemy.Column(sqlalchemy.String(100))
    lastUpdate = sqlalchemy.Column(sqlalchemy.DateTime)

    def __str__(self):
	return "{0} {1}".format(self.dburl,self.lastUpdate)
    
