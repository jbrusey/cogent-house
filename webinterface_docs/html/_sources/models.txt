***************************
The Database and Model API
***************************

Introduction
=============

The table classes represent the database schema used.

See :download:`Full Database Schema <NewSchema.pdf>` 


.. _gen-model-functions:

The Base Class
==============

The :class:`models.meta.InnoDBMix` class defines parameters common to all model objects.

This is used as a mixin class along side the sqlalchemy.orm.Base 

.. autoclass::	cogentviewer.models.meta.InnoDBMix
   :members:

========================
:mod:`model` Classes
========================

..

   We need to add a automodule function for each class.  Potentially
   it may be better to munge classes that are relevant to each other
   together to reduce the amount of work here

.. todo::
   
   Classes that need to be fully documented  
   #. Bitset
   #. Host
   #. LastReport
   #. NodeState
   #. NodeHistory
   #. NodeType


Deployment Related Classes
==========================

.. graphviz:: graphs/deployment.dot

.. automodule::	cogentviewer.models.deployment
   :members:


.. automodule:: cogentviewer.models.deploymentmetadata
   :members:


House Related Classes
======================

.. graphviz:: graphs/house.dot

.. automodule:: cogentviewer.models.house
   :members:

.. automodule:: cogentviewer.models.housemetadata
   :members:

.. automodule:: cogentviewer.models.location
   :members:


Reading Related Classes
========================

.. graphviz:: graphs/reading.dot

.. automodule:: cogentviewer.models.reading
   :members:


Room Related Classes
=====================

.. graphviz:: graphs/room.dot

.. automodule:: cogentviewer.models.room
   :members:

.. automodule:: cogentviewer.models.roomtype
   :members:


Node Related Classes
=====================

.. graphviz:: graphs/node.dot

.. automodule:: cogentviewer.models.node
   :members:

.. automodule:: cogentviewer.models.nodetype
   :members:

.. automodule:: cogentviewer.models.nodehistory
   :members:

.. automodule:: cogentviewer.models.nodestate
   :members:



Occupier Related Classes
=========================

.. graphviz:: graphs/occupier.dot

.. automodule:: cogentviewer.models.occupier
   :members:

Sensor Related Classes
=======================

.. graphviz:: graphs/sensor.dot

.. automodule:: cogentviewer.models.sensor
   :members:

.. automodule:: cogentviewer.models.sensortype
   :members:



Other Classes
==============

Classes that deal with other stuff

.. graphviz:: graphs/other.dot

.. automodule:: cogentviewer.models.Bitset
   :members:

.. automodule:: cogentviewer.models.host
   :members:

.. automodule:: cogentviewer.models.lastreport
   :members:
   
.. automodule:: cogentviewer.models.rawmessage
   :members:

.. automodule:: cogentviewer.models.weather
   :members:

======================================
Upgrading the Database using Alembic
======================================

Some Notes on Alembic 

Install
========

Should be as easy as::

    $pip install alembic

Setup
======

Database Upgrade scripts are kept in::

  /cogent/alembic

And the main .ini setup file can be found in::

  /cogent/alembic.ini

Hopefully everything is setup correctly.  But if you use a different database schema / username / password you may need to modify the setup string in this .ini file.


Running the Upgrade
====================

Again this should be as simple as::

    $alembic upgrade head

However, sometimes (with a new version of models.py but an old version of the
database) We can have problems with the expected tables allready existing.  In
this case a workaround (not a very good one) is to manually remove the

     # lastReport
     # location
     # host
     # rawmessage

tables from the database

.. note::

   A better solution would be not to run any of the new models code (therefore updating the DB)
   before you run the alembic upgrade



Adding a changeset
====================

If we want to change the DB follow this process





