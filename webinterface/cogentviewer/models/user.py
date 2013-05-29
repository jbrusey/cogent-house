"""
Table to represent users of the system.

.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>
"""


#SQL Alchemy Relevant information
import sqlalchemy

#And Backrefs and Relations.
import sqlalchemy.orm

#Import Pyramid Meta Data
import meta

class User(meta.Base, meta.InnoDBMix):
    """Table to hold information about users of the database


    """

    __tablename__ = "User"

    id = sqlalchemy.Column(sqlalchemy.Integer,primary_key=True)
    username = sqlalchemy.Column(sqlalchemy.String(256))
    email = sqlalchemy.Column(sqlalchemy.String(256))
    password = sqlalchemy.Column(sqlalchemy.String(256))
    level = sqlalchemy.Column(sqlalchemy.String(32)) #Root, User etc

