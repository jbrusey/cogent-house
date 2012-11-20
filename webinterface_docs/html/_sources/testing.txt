=====================
The Testing Database
=====================

.. graphviz::
   graphs/testingDb.dot

Assumptions
============

 * Each Sensor records 1 sample per hour
 * Sample Value is (NodeId*X) [1,2,...N]
 

House 1
========

 * Lasts for two weeks,
 * Has a total of four Nodes

Rooms and Nodes
-----------------

 * Master Bedroom -> Node37
 * Second Bedroom -> Node38
 * Living Room -> Node39

Corner Case
------------

During the Deployment we move one of the nodes,

Week1: Node 40 is in the Living Room
Week2: Node 40 Moves to the Master Bedroom

       


House 2
========

 * Lasts for one week, (The Second Week of the Deployment)
 * Has a total of two Nodes

Rooms and Nodes
-----------------

 * Master Bedroom -> Node69
 * Living Room -> Node70

