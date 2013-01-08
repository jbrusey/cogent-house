===================================
Database Versioning and Migration
===================================

This document outlines modifications to the database and the process's needed to perfor versioning.


Requirements
=============

The database migration code makes use of sqlalchemy-migrate [http://code.google.com/p/sqlalchemy-migrate/]

Install using pip (or easy_install)::
  pip install sqlalchemy-migrate


Setup
=====

Create a new repository for the database::
    #migrate create <repo-name> "<desc>"
    migrate create cogent-db-repo "Cogent Database"

Then version control the current DB
     python /cogent-db-repo/manage.py version_control <sqlite db string> cogent-db-repo


We can also setup a quick access script with the addresses preconfigured using::
    migrate manage manage.py --repository=cogent-db-repo/ --url=mysql://root:Ex3lS4ga@localhost/ch



Making Changes
==============

First setup a new changeset::
      python manage.py script "scriptName"

This create a file in '''repo/versions/<vurrent>_<script>''' we edit this to make our changes.

The script has two predefiend funcions ''upgrade()'' and ''downgrade()'' we need to make sure these are complete, otherwise there could be inconsistencys in the way things work::

  #from sqlalchemy import *
  import sqlalchemy
  from migrate import *

  meta = sqlalchemy.MetaData()

  """
  Association object to link rooms to Nodes
  This means we can have a many to many link between rooms and nodes, 
  while still maintianing whatever functionality the cogent software relies on
  """
    roomNodes = sqlalchemy.Table('room-nodes',
                                 meta,
                                 sqlalchemy.Column('roomId',
                                                   sqlalchemy.Integer,
                                                   sqlalchemy.ForeignKey('Room.id')),
                                 sqlalchemy.Column('nodeId',
                                                   sqlalchemy.Integer ,
                                                   sqlalchemy.ForeignKey('Node.id'))
                                 )                                            

    def upgrade(migrate_engine):
        # Upgrade operations go here. Don't create your own engine; bind
        # migrate_engine to your metadata
        meta.bind = migrate_engine
	
	#Reflect any tables with FK's etc
	Room = sqlalchemy.Table("Room",meta,autoload=True)
    	Node = sqlalchemy.Table("Node",meta,autoload=True)

        roomNodes.create()

    def downgrade(migrate_engine):
        # Operations to reverse the above upgrade go here.
        meta.bind = migrate_engine
        roomNodes.drop()


And test the changes::

    python manage.py test    



      
