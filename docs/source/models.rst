======
Models
======

Introduction
=============

The table classes represent the database schema used.

While they are based on the code classes used in the sensing portion of the 
project, they do contain extra funtionality to:

#. Make the system compatable with Pyramid
#. Implement various methods that will be needed in the display portion
#. Fix things that seem a little backwards (to me anyway)

.. warning::
   
   All code should be backwards compatable, The majority of changes
   are documentation, or functions. However, imports are very likely
   to be different.  Copy the classes within the files not the files
   themselves.
	


.. _gen-model-functions:

Generic Functions
==================

There are several generic functions that each table / class will have,
rather than do loads of docstings I have documented them here.

.. function:: model.update(self,**kwargs)

    :param kwargs:  Keyword arguments to initialise

    .. warning::

        There is currently no sanity checking on the named args!
        This means we can use argumnents that are not in the Table 
        But do not expect them to be saved in the database

    Update an object using keyword arguments::

	foo = Template() # Create a blank object
	foo.update(id=5,value=10) # Set id and value to 5,10 respectively	

.. function:: model.asJSON(self,parentId)

   :param parentId:	Id string representing parent object
   :rtype:		A JSONable dictionary of model parameters.

   This does not return a JSON string representation of the object but
   rather a dictionary suitable for turning into a JSON string.  This
   means that things such as Datetimes are taken care of rather than
   causing BadThings(TM) to happen.

   It is not expected that we call this function ourselves, rather it
   will be called by the :func:`model.flatten` and :func:`model.asList` methods.

  
.. function:: model.flatten(self)
   
    .. todo::
        
	Write more Documentation for this
	Also make sure we have python code as docstring style stuff.

    :rtype: A Flattened Tree Representation of this object and its children.

    .. seealso:: :func:`model.toJSON`

    Return a flattened Tree Representaion of this object, This should
    recursively travel down the database tree producing a nested list
    of inter related objects.  Of the form
    {Item:<NAME>,Children:[<Children*]} Not all data will be included
    (stuff like metadata will be ignored) but

    For example condier the schema  Deployment 1->* Houses 1->* Node

    Calling Flatten on Node will return that node object.  Howerver,
    callen Flatten on Deployment will return something along the lines
    of::

        {"item":<deploymentId>, children:[{"item:<child1>,children:[<.....>]},.....]}
    
   
    pprint is your friend to display this info.
    

.. function:: model.asList(self,parentId)

    .. todo::
        
	Write more Documentation for this
	Also make sure we have python code as docstring style stuff.

    .. seealso:: :func:`model.toJSON`

   Recusive method to turn the database tree into a list.
   This is primary used for navigaion but may also be usefull elsewhere.

========================
The :mod:`model` Classes
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

.. graphviz:: deployment.dot

.. automodule::	cogentviewer.models.deployment
   :members:

.. automodule:: cogentviewer.models.deploymentmetadata
   :members:

House Related Classes
======================

.. graphviz:: house.dot

.. automodule:: cogentviewer.models.house
   :members:

.. automodule:: cogentviewer.models.housemetadata
   :members:

.. automodule:: cogentviewer.models.location
   :members:


Reading Related Classes
========================

.. graphviz:: reading.dot

.. automodule:: cogentviewer.models.reading
   :members:


Room Related Classes
=====================

.. graphviz:: room.dot

.. automodule:: cogentviewer.models.room
   :members:

.. automodule:: cogentviewer.models.roomtype
   :members:


Node Related Classes
=====================

.. graphviz:: node.dot

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

.. graphviz:: occupier.dot

.. automodule:: cogentviewer.models.occupier
   :members:

Sensor Related Classes
=======================

.. graphviz:: sensor.dot

.. automodule:: cogentviewer.models.sensor
   :members:

.. automodule:: cogentviewer.models.sensortype
   :members:



Other Classes
==============

Classes that deal with other stuff

.. graphviz:: other.dot

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


