******************
Cogent-House Tools
******************

Modules
========

Cogent-House Base
-------------------

Code to gather environmental data from a WSN.


Cogent-House Viewer
--------------------

This pyramid application  is designed to display the data collect by the Cogent-House sensing system.


Install Instructions
=====================

Source Code Locations
----------------------

* `Cogent-house (Base Code) <http://code.google.com/p/cogent-house/>`_
* `Cogent-Viewer (Web Interface) <https://launchpad.net/cogent-house>`_

Testing Installation
---------------------

The code has been setup to use setuptools for distribution.
code can then be tested using the *develop* function.

Additionally the applicaiton can be tested in a *virtual environment*,
this is the equivelent of a clean python install, allowing any problems 
Steps to install the project in a test enviroment are.

.. note::

   If you are installing the base code, you will also need to compile
   follow the instructons :TODO: here
   

#. Install Virtual-Env::
   
   $sudo apt-get install python-virtualenv

#. Setup Virtual Environment.  Using the *--no-site-packages* flag means that
   we get the equivalent of a clean python install::

   $virtualenv --no-site-packages testenv
   
#. Activate the virtual env::

   $cd testenv
   $source bin/activate

#. Install the code in development mode::

   $python setup.py develop


Building the Documentation
----------------------------

The Documents are built with Sphinx <http://sphinx.pocoo.org/index.html>`_

Most of the information comes from docstrings in the code itself. Please keep these up to date.

To build the Docs it is as simple as::
   
   $cd docs
   $make html

Exporters are available for HTML and Latex (amongst others)

.. warning::
   
   Some Ubuntu versions of sphinx are old, and will generate an error
   when building the graphs.  To aviod this install the latest version
   of sphinx from PyPy::

      #sudo pip install --upgrade Sphinx
   

Source and Bug Tracker
------------------------

* `Cogent-house (Upstream) <http://code.google.com/p/cogent-house/>`_
* `Project Home <https://launchpad.net/cogent-house>`_
* `Bug Tracker <https://bugs.launchpad.net/cogent-house>`_

Webserver setup
================

.. todo::
   
   Setup the Web Server  
