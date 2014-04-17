***************************
Installation Instructions
***************************

These are the installation instructions for the Web Interface.  For instructions
for the Base Code see the `google code
<https://code.google.com/p/cogent-house/>`_ site.

Getting the Source
====================

* `Cogent-house (Base Code) <http://code.google.com/p/cogent-house/>`_
* `Cogent-Viewer (Web Interface) <https://launchpad.net/cogent-house>`_

Dependencies
==================

There are some dependencies to install the web interface

#. python-dev  
#. python-pip
#. python-virtualenv
#. libmysqlclient-dev
#. git

Additionally, mysql-python currently require 

In Ubuntu (or another debian based system) these can be installed using::

   $sudo apt-get install python-dev python-pip python-virtualenv libmysqlclient-dev bzr git


Installing in a virtual environment
====================================

To aid development, this code has been configured to use setuptools for
distribution.  This allows changes to the code to be tested using the `develop
<http://peak.telecommunity.com/DevCenter/setuptools#develop-deploy-the-project-source-in-development-mode>`_
function. Allowing changes to the code to be immediately reflected in the python
environment, rather than requiring a fresh #setup.py install call.

Additionally, I recommend developing in a `virtual environment
<http://pypi.python.org/pypi/virtualenv>`_ this is the equivalent of a clean
python install, allowing any problems that may occur with missing packages /
different package versions to be seen.  This is a great advantage when
packaging, as installing from scratch allows testing of installation steps.

.. note::

   Using a virtualenv is not mandatory.  For example if you are installing on a
   production server and are unlikely to make any changes to the code.  However,
   for development its a extremely useful tool.

Setting up a virtual environment
---------------------------------

To setup the virtual environment.

.. note::

   These steps use *pip* to install packages.  However, feel free to use your favourite package manager (easy-install etc)

#. Install virtualenv::

       $pip install virtualenv

#. Setup Virtual Environment.  Using the *--no-site-packages* flag means that
   we get the equivalent of a clean python install::

   $virtualenv --no-site-packages testenv


To use the virtual environment activate it.  Missing this stage can be a common
source of problems, as the program tries to use packages that are not in the system wide library::

   $cd testenv
   $source bin/activate
   (testenv)$

And to shut everything down afterwards, deactivate it::

    (testenv)$ deactivate
    $


Installing the application
===========================

Downloading the Code
----------------------

Grab the latest version of the source from launchpad

For Stable::

     $bzr branch lp:cogent-house

To install in *development* mode::

   (testenv)$ setup.py develop 


.. note::

   There appears to be a bug in easy_install when installing numpy.
   This means that the setup.py develop step may not work.
   A simple work around is to install numpy with pip (which for some reason works)
   then rerun the setup script::

   $pip install numpy
   $python setup.py develop

Setting Up the Database
------------------------

The database setup script can be called by running::

    $initialize_cogentviewer_db <config>.ini 


Installing the Javascript Libraries
-----------------------------------

Currently, the web interface uses a local version of the javascript libaries,
this avoids any problems when there is no internet connection available.

Unpack the **jsLibs.tar.gz** file in the same base directory as the webinterface::

    dan@einstein:~$tar -xvzf jsLibs.tar.qz
    dan@einstein:~$ ls -l
    total 38956
    drwxr-xr-x 4 dan dan     4096 2012-06-15 14:53 cogent-house
    drwxr-xr-x 5 dan dan     4096 2012-06-13 12:00 jslibs
    -rw-r--r-- 1 dan dan  7456451 2012-06-15 14:57 jsLibs.tar.gz


Running a Local Copy of the Server
===================================

Once the application is installed in development mode. It is possible to test the server

#. Activate the virtual env::

   $cd testenv
   $source bin/activate

#. Navigate to the cogent-viewer base directory::

   (testenv)$cd cogentviewer

#. Start the Paste server::

   (testenv)$pserve --reload development.ini

The web interface should now be available at `127.0.0.1:6543 <127.0.0.1:6543>`_


Running Unit tests
==================

The application also has a suite of unit tests.  

Testing is performed using the `nose <http://readthedocs.org/docs/nose/en/latest/index.html>`_ test runner.


Setting up a testing database
-------------------------------

Rather than use a live database, the Unit tests use a separate testing DB.

To set this up create a new schema *testStore* and user *test_user* with password *test_user*

We also need to populate the database with its initial testing data the simplest
way to do this is to run an instance of the paste server using the test.ini
script::

    $initialize_cogentviewer_db test.ini 

.. note::

   If you want to use an alternative database, it is possible to modify the
   database string found in the **test.ini** setup file.

.. warning::

   Unfortunately it is impossible to run the unit tests using a separate sqlite database
   There have been locking issues as  parts of the code try to access the DB,
   meaning that several tests fail.


Running the Unit tests
----------------------

As the REST interface communicates with the server, we need to have an instance
of the web server running for the tests to complete.

#. Start an Instance of the paste server running the test.ini script::

   (testenv)$pserve serve --reload test.ini

#. Run the Unit tests::

   (testenv)$nosetests 





Running Under Apache using port forwarding
============================================

An alternative method to serve the web interface under apache,  setup a reverse proxy to forward requests to the paste serve

Setup Mod Proxy
-----------------

We first need to enable the mod-proxy module on the apache server::

   $sudo a2enmod proxy

.. note::
   If you get an error loading the site, you may need to enable proxy_http

Then Modify the default site */etc/apache2/sites-available/default*::

    ProxyRequests Off
    ProxyPreserveHost On

    <Proxy *>
	Order allow,deny
	Allow from all
    </Proxy>

    ProxyPass /webInterface/ http://localhost:6543/
    ProxyPassReverse /webInterface/ http://localhost:6543/

Finally we need to make a modification to the paster .ini script used to serve the application,  add the following directing to the config file,  just before the *[server:main]* directive::

    filter-with = urlprefix

    [filter:urlprefix]
    use = egg:PasteDeploy#prefix
    prefix = /webInterface

.. note::
   
   This modification has been made in the **proxy.ini** config file


Building the Documentation
============================

The Documents are built with Sphinx <http://sphinx.pocoo.org/index.html>`_

Most of the information comes from docstrings in the code itself. Please keep these up to date.

To build the Docs it is as simple as::
   
   $cd docs
   $make html

Exporters are available for HTML and Latex (amongst others)

.. warning::
   
   Some Ubuntu versions of sphinx are old, and will generate an error
   when building the graphs.  To avoid this install the latest version
   of sphinx from PyPy::

      #sudo pip install --upgrade Sphinx


.. _upgrading-the-database:

Updating the Database
======================


The webinterface requires an upto date version of the database.  If the web
interface is installed on top of an pre-exisiting base server.  You will need to
update the database using the following steps.


#. Get the and latest version of the base software, from `here <http://code.google.com/p/cogent-house/>`_

#. **Backup the Database**::
   
   $mysqldump -u chuser -l -v ch > chDump.sql

#. Install Alembic::
   
   $pip install alembic

#. **Backup the Database** (Included here incase you don't feel it is important)

#. Run the Alembic Upgrade Script::
   
   $alembic upgrade head   
