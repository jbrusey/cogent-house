****************************
Installing Instructions
****************************


Installing in a virtual environment (Optional)
================================================

.. sidebar:: Using Virtualenv

   Using a virtualenv is not mandatory.  For example if you are installing on a
   production server and are unlikely to make any changes to the code.  However,
   for development its a extremely useful tool as it keeps your default python
   installation clean.


To aid development, this code has been configured to use setuptools for
distribution.  This allows changes to the code to be tested using the `develop
<http://peak.telecommunity.com/DevCenter/setuptools#develop-deploy-the-project-source-in-development-mode>`_
function. Allowing changes to the code to be immediately reflected in the python
environment, rather than requiring a new $setup.py install call.

Additionally, I recommend developing in a `virtual environment
<http://pypi.python.org/pypi/virtualenv>`_ this is the equivalent of a clean
python install, allowing any problems that may occur with missing packages /
different package versions to be seen.  This is a great advantage when
packaging, as installing from scratch allows testing of installation steps.



Setting up a virtual environment
---------------------------------

To setup the virtual environment.

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

.. note::

   If you are planning on using a virtualenv make sure you source it first.

Grab the latest release of the web interface from launchpad::

    $bzr branch lp:~cogent-house


Install the web interface
----------------------------


Install the web interface::

    $cd cogent-house
    $python setup.py develop

Initialise the database::

    $initialize_webinterface_db development.ini

.. note::

   Initialising the database will setup a root level user (if one does not
   exist) and also call in all required calibration data, node types etc.


And test the install::

    $pserve --reload development.ini

If you navigate to `127.0.0.1:6543 <http://127.0.0.1:6543/>`_  you should see the login screen.


Install the required Javascript libraries
--------------------------------------------

The web interface requires several javascript libraries, as we cannot guarantee
that these will be available (for example if we are running a server in
isolation without Internet access) then we install a local copy, rather than use a CDN.

    $get_webinterface_js


Adding New Users
------------------

Currently this can only be done through the shell::

    $add_webinterface_user development.ini


Getting the Paste server to work with apache
==============================================

While using pserve to run the database is fine for testing, firewall settings etc can interfere with serving the page across the Internet.

Therefore we need to setup the web interface under apache,  though setup a reverse proxy to forward requests to the paste server.

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


