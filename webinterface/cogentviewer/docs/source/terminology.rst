Terminology Used
=================


.. glossary::

   Deployment
	Installing the sensing equipment in a house or group of houses

   Deployment Group
   	A Logical grouping of deployments (for example Samson Close) used to aid analysis

   House
	A Single property


   Node Numbering Scheme
   	Each node has a unique identifying id, this takes the form of

	<SET>-<NODE IN SET>-<TYPE>-<NUMBER>

	So the Node with ID **2-7-0-71** is
	
	* Part of Set 2
	* Node Number 7 in set 7
	* A Battery powered node
	* Has Unique identifier of 71

	Node Types are as follows

	+---------+----------------------+
	| Type Id | Description          |
	+---------+----------------------+
	|       0 | Battery Powered Node |
	+---------+----------------------+
	|       2 | Co2 Sensing Node     |
	+---------+----------------------+
	|      10 | Server Node          |
	+---------+----------------------+




   Node
	An individual sensing device. Nodes come in several types:
	 
	Battery Powered Nodes:
	    .. figure:: images/NodesBatt.jpg
	        :width: 640px      

	        Battery Powered Nodes


	    These nodes monitor temperature and humidity.

	    They are ideal for use in rooms where no dedicated power supply is
	    available such as kitchens, hallways and bathrooms


	Plugin Nodes
	    .. figure:: images/NodesCo2.jpg
	        :width: 640px
	    
	        Co2 Sensing Node

	    These nodes monitor additional parameters such as CO2 or VOC.  As
	    these parameters tend to be affected by occupancy these nodes are
	    ideal for deployment in commonly used areas such as the living room, or bedrooms.

	Power Monitoring Nodes 
	    These nodes are used to monitor the energy
	    consumption of a property, and need attaching to the electricity
	    meter.

	Server Node
	    The server node attaches to the server and is used transfer samples
	    between the network and the server itself.
	

   Server
        .. figure:: images/ServerComponents.jpg
	    :width: 640px

	    Server and Server Node
   
	The server is used to store information gathered by the nodes.

   Server Node:
       The Server Node is a node attached to the server responsible for receiving all communications from the network
