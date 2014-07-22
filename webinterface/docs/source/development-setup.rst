****************************
Installing Instructions
****************************



Installing in a virtual environment (Optional)
================================================

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
   for development its a extremely useful tool as it keeps your default python
   installation clean.


Setting up a virtual environment
---------------------------------

To setup the virtual environment.

.. note::

   These steps use *pip* to install packages.  However, feel free to use your favourite package manager (easy-install etc)

#. Install virtualenv::

       $pip install virtualenv

#. Setup Virtual Environment.  Using the *--no-site-packages* flag means that
   we get the equivalent of a clean python install::

   $virtualenv --no-site-packages env


To use the virtual environment activate it.  Missing this stage can be a common
source of problems, as the program tries to use packages that are not in the system wide library::

   $cd env
   $source bin/activate
   (env)$

And to shut everything down afterwards, deactivate it::

    (env)$ deactivate
    $


Installing the Web Interface
=============================

Get the Codez
---------------
Grab the latest release of the web interface from launchpad::

    $bzr branch lp:~cogent-house


Install the web interface
----------------------------

Install the web interface::

    $python setup.py develop


Install the database
----------------------

To setup the database you will a new (or existing) database schema **ch** and relevant user **chuser**. 

To ensure the webinterface database is 



Install the required Javascript librarys
--------------------------------------------

TODO::



Test






