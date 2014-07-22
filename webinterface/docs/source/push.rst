*************************
Database Uploads
*************************

.. warning::

   The Push scripts (and webinterface) require the latest version of the
   database.  Even if the server is not running the web inteface. You will need
   to follow the database upgrade instructions found here
   :ref:`upgrading-the-database`

.. note::

   These scripts require a mysql database, even for testing.
   Unfortunately sqlites table locking mechinism does not play 
   nicely when reading / writing data from several scripts.

.. note::

   Currently the sync is one time / one way only, (ie push from local to remote
   database) This means that any changes made in either database will not be
   reflected.  This would be an interesting todo for the future.


Overview
========

The Database Upload (Push) functionality, enables a database on a remote server to
be uploaded to a remote (central) server. Without having to resort to command
line scripting, mysql dumps etc.

The push function is designed to be run as a daemon process, periodically
pushing updates to the central point.

This functionality makes use of the REST interface (See :ref:`rest-interface`.)


Installing Push Script
-------------------------

The Push Script currently lives in the Base `Cogent-house
<http://code.google.com/p/cogent-house/>`_ software.  Follow the install
instructions at this site to install the push script.


Testing / Configuring the push script
======================================

Test the connection to the remote server by visiting the <base>/rest/sensortype/
url in your webbrowser (for example http://127.0.0.1:6543/rest/sensortype/ if
you are running the web interface via the paste server) There should be a JSON
dictionary of sensortype objects displayed.

Configuring the Push Script
-----------------------------

Modify the synchronise.conf file (base/push/synchronise.conf) with the details
of the remote rest server you visited above.

Running the Push Script
-------------------------

To run the push script::

   python RestPusher.py


The script should output logging information to a logfile.



Running the Push Script as a Daemon
-------------------------------------

.. note::

   Write code / Docs for this


  
Algorithm Overview 
===================

Each Iteration of the *sync* function does the following:

#. Read the Configuration Files
#. For Each Server that needs to be updated

   #. Ensure all local nodes are in the remote table
   #. Map *Active* Deployments
   #. Map *Active* Houses
   #. Synchronise the Location Table
   #. Update Nodes with new locations
   #. Upload the Relevant Node States
   #. Upload the Relevant Readings
   #. Update Configuration Files with last transmitted sample


These steps are described in detail below:

Synchronising Nodes
--------------------

This method uses SQLA to synchronise the node tables between the local and remote servers.
As nodeIds should be static (ie node 69 will allways be node 69) then this function can make use of a simplistic approach.

#. For each local node, where the node id is not on the remote server:
   #. Create a new node with this Id
   #. Create a new set of sensors linked to this node

.. note::

   Currently, we only create new sensors when adding a node.  At some point we may need to update the code to deal with this

Mapping Deployments and Houses
--------------------------------

.. note::

   We Assume that the following parameters are unique

   #. Deployment.name
   #. House.address

To reduce the amount of network traffic, we only map *Active* Deployments /
Houses, where an active house is defines as one that::

    object.endDate == None
    object.endDate >= lastUpdate


These database items are fetched from the local database, and mapped to their equivelent on the remote database.
If no such item exists on the remote database then 


The following queries are first run on the local database

#. Get Deployments / Houses to be updated

   Given the date of the last update, we fetch all deployments and houses where
   the finishdate is either None, or After the last update.  This should reduce
   the amount of locations mapped to a minimum.  

   If for some reason there are no deployments, then we get all active "houses"
   using the same parameters on the house table. 


   
#. Get Locations to be Updated

   Based on the houseID's of those houses that need are current.  We fetch a set
   of locations from the local database.

#. Get Rooms to be Updated

   Now we have the location Id's, it is possible to get a list of rooms that will need updating


#. Create new objects
   


.. Pusher.py
.. ==========

.. This module aims to syncronise a local and remote database.  And
.. contains functionality to push information from this database with a
.. remote database object.


.. .. _push-config:

.. Config Files
.. =============

.. .. since 0.3::

..    The Push Script has been updated to deal with configuration files rather than 
..    Using a database table to keep track of where we need to push information to.
..    This should make it easier to deal with initial default values, 
..    as well as allowing quicker editing when in the field.

.. .. todo::
..    Update this when we have a location for the config file to be saved

.. The configuration file *synchronise.conf* contains the information needed to synchronise databases

.. The Locations Section
.. ----------------------

.. Each location we wish to push to should have an entry in the locations section of the config file.
.. This should be of the form  <location> = <sync flag>

.. There should then be a corresponding header containing details of the location given later in the file.

.. For example, the following config section, gives two locations that we could push to, *local* and *cogentee*
.. The push script will attempt to push data to *local*, however we have turned pushing to *cogentee* off.

.. .. code-block:: ini

..    [locations]
..    local = 1  #Push to the server specified in the local section
..    cogentee = 0 #Ignore the server specified in cogentee section


.. Server Details
.. ---------------

.. For each item in the Locations block, we need a corrisponding server configuration.

.. .. code-block:: ini

..    #A Update config for a specific URL
..    [local]
..    #Url we need to transmit the data to
..    url = 127.0.0.1
..    #Database connection string for MSQLA
..    dbstring = mysql://test_user:test_user@127.0.0.1:3307/pushTest
..    #The Last time an update was sent to this host (Delete this or set to if we want to start from scratch)
..    lastupdate = None
..    #SSH Username
..    sshuser = dang
..    #URL of .ssh folder
..    sshfolder = /home/dang/.ssh
..    #Name of keyfile
..    sshkey = work_key.pub


.. Deleting the *lastupdate*, or setting to None will attempt to upload every item from the local database.



.. Globals
.. --------
.. .. py:data:: Pusher.LOCAL_URL 
   
..    Sqlalchemy dbstring to use to connect to the local database

.. .. py:data:: Pusher.PUSH_LIMIT
   
..    Limit on the number of samples to transfer

.. .. py:data:: Pusher.SYNC_TIME

..    Number of seconds the __main__ function will sleep between updates


.. Core Methods
.. -------------

.. .. py:function:: init([localUrl])

..    Initialise the Pusher Object.  The optional localURL parameter gives 
..    a sqlalchemy connection string to use to connect to the local DB.
..    If this is not provied, a hardcoded URL is used.

.. .. py:function:: sync()

..    Synchronise all data up to the current time
   
..    Performs all the tasks needed to keep the database in sync
..    Its functionality is described below.
   

.. Synchronisation Overview
.. --------------------------

.. The Push Algorithm follows

.. #. For Each Remote Database that needs synchronising

..    #. Setup SSH Tunnel
..    #. Syncronise Nodes (:func:`Pusher.syncNodes`)
..    #. While there is still data to be Syncronised

..       #. Sync the next :data:`Pusher.PUSH_LIMIT` Dataitems (:func:`Pusher.syncReadings`)

..    #. Close SSH Tunnel.   

.. #. Sleep for :data:`Pusher.SYNC_TIME` seconds
.. #. Goto 1

.. Node Synchronisation
.. ^^^^^^^^^^^^^^^^^^^^^

.. To Synhronise Nodes the following process takes place.

.. .. note::

..    It should be noted that NodeID's are expected to be global, as are sensor type ID's
..    If this changes then some sanity checking needs to be added here.



.. #. Get a list of remote Nodes.

..   * Fetch all remote nodes then strip out node Id's

.. #. Compare local nodes to the remote nodes to see which items we need to update

..   #. Query(models.Node) filter where (Node.id is not in the list of remote node Id's)
..   #. Strip out Id's of new nodes that need adding

.. #. For each new Node

..   #. Syncronise Loccation / House / Rooms / Deployments
..   #. Synchronise Sensors

..      #. For each sensor attached to this Node

..      	#. Create a new sensor of this type on the remote DB
   
.. Reading Synchronisation
.. ^^^^^^^^^^^^^^^^^^^^^^^^^

.. Makes use of a Location dictionary to cache the relationshp between
.. local and remote locations


.. #. Retreive the Last update time from the UploadURL database
.. #. Fetch the next X items after this time from the local Database 
.. #. For each item

..    #. If Reading.location not in Location{}
      
..       #. Fetch / Update the Location

..    #. Else

..       #. Add a new reading to the remote database session

.. #. Commit Readings
.. #. Update last Upldate in Upload URL
.. #. Update the Remote Nodestate Table
      

   

.. UploadURL Table
.. ----------------

.. Holds details of 

.. remoteModels.py
.. ================

.. Contains functionality to map classes to the remote database via reflecion.
.. The Majority of this module are support or helper functions to achieve this.

.. This means that it should be possible to manipulate remote database
.. objects using similar syntax to local database objects. However, we do
.. need to take acount of sessions.

.. .. note::

..    Technically it appears that this may not be necessary, rather the session 
..    used influences the database (as long as the table structure is the same)

.. For instance::
    
..     #Get A Local Reading
..     >>> localSession = meta.Session()
..     >>> localReading = localSession.query(models.Reading).first()
..     >>> print localReading
..     Reading(......)

..     #And a Remote Reading
..     >>> remoteSession = remote.Session()
..     >>> remoteReading = remoteSession.query(remoteModels.Reading).first()
..     >>> print remoteReading
..     Reading(.....)
    

.. The advantage of using reflection, is that minor differences to the
.. tables can be taken account of, For example, if there is a different
.. minor revision of the database running on each server this should not
.. make a difference.


.. .. function:: push.remoteModels.reflectTables(engine,RemoteMetadata)
   
..    Given a remote database engine, connect, reflect the remote tables,
..    and associate them with the mapper.

..    :param engine: Sqlalchemy database engine to use
..    :param RemoteMetadata: Sqlalchemy metadata object associated with this object.
   

.. sshClient.py
.. =============

.. Functionalty to support ssh tunneling via Paramiko
.. This code has been modified from the paramiko demos.

.. While SSH tunneling via paramiko does complicate the code to connect,
.. It has the advantage of:

.. * Easier Connection (and handling of remote keys)
.. * Better Error handling

.. This greatly simplifies the code to work with ssh

.. Using the SSH Module
.. --------------------

.. Example code to use the ssh module would be::

..     import paramiko
..     import sshClient
..     import threading
..     import socket	
    
..     #Setup SSH Client
..     ssh = paramiko.SSHClient()
..     #Allow keys to be added to paramiko keyring
..     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

..     #Try To Connect
..     try:
..         ssh.connect(<host>,username=<username>)
..     except socket.error,e:
..         #Deal with connection (no network etc) ettors
..     except paramiko.AuthenitcationException:
..         #Deal with authentication errors

..     #Setup tunneling
..     server = sshClient.forward_tunnel(3307,"127.0.0.1",3306,ssh.get_transport())
..     #And start the ssh forwading in a seperate thread
..     serverThread = threading.Thread(target=server.serve_forever)
..     serverThread.deamon = True
..     serverThread.start()

..     #Do Whatever Tunnel Based communication is needed
..     # ...

..     #Then shut everything down ready to start next time.
..     #It is vital that this is called after any error otherwise we can get
..     #Address in use errors.

..     server.shutdown()
..     server.socket.close()
..     ssh.close()
    

.. Testing Scripts
.. ================

.. I have also added the following testing scripts

.. Datagen.py
.. -----------

.. Generates fake data.

.. .. py:data:: Datagen.LOCAL_URL 

..    Sqlalchemy database string to connect to the local database

.. .. py:data:: Datagen.READING_GAP

..    Time (in seconds) to leave between readings

.. .. py:data:: Datagen.STATE_SWITCH

..    How many samples to insert before adding items to the nodestate table.


.. Every :py:data:`Datagen.READING_GAP` seconds the script adds new data
.. items to the local database.  Temperature readings will be added for
.. *Node37* with a value 0..100 and *Node38* with a value of 100..0

.. Every :py:data:`Datagen.STATE_SWITCH` readings a new set of node
.. states is added to the database.  Additionally the ccalue counters for
.. each node are reset.


.. ClearDB.py
.. -----------

.. Clean all data from the local and remote databases
