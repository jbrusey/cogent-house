################
Cruft and Notes
################

.. toctree::
   dansInstallNotes
   dbVersion
   jsonFunctions
   newFeatures
   testing


Headings Should Be as follows,  Anything Below Subsection Really should be avoided.

###########
Part
###########
Normal Text   ## with overline

***********
Chapter
***********
Normal Text ** With Overline

Section
===========
Normal Text == Underline

Subsection
-----------
Normal Text -- Underline

SubSubsection
^^^^^^^^^^^^^^
Normal Text

Paragraph
""""""""""
Normal Text


..  topic:: A quick Topic

    This is a digression / seperate topic that we want to highlight



.. sidebar:: Sidebar Title
   :subtitle: An Optional Subtitle

   We can also stick text into a sidebar, This gives an alternate form of highighting

With a sidebar the text below is floated right and will flow around the sidebar itself.

This happens to all paragraphs headings etc. until we end up below the float


Running under Apache mod-wsgi
==================================

To Get the development application installed above to run under Apache
you need to:

.. warning::

   For this example we use the pyramid configuration file *development.ini* this
   keeps the debug toolbar etc.  For production servers it is recommended to use
   the *production.ini* file.


#. Install Apache and mod-wsgi::

   $sudo apt-get install apache2 libapache2-mod-wsgi


#. In the virtual env (ie testenv) created above create a pyramid.wsgi script Its contents should be along the lines of::

      from pyramid.paster import get_app
      application = get_app("/home/dang/Progamming/Pyramid/viewer-repo/webinterface.rest/development.ini","main")

   The first part of the get_app function points to the paster.ini file used to run the application.  Technically, we should point to 
   the development.ini file with its greater level of security.  But in this instance we will just point to the testing development file.
   

#. Make the pyramid.wsgi file executable

#. Edit the apache configuration files so mod wsgi knows where to look by adding
   the following to the default application **/etc/apache2/sites-available/default**::

       WSGIPythonHome /home/dang/Progamming/Pyramid/

       <VirtualHost>
       ...
       ...
       #Add MOD WSGI Pyramid Configuation
       WSGIApplicationGroup %{GLOBAL}
       WSGIPassAuthorization On
       WSGIDaemonProcess pyramid user=dang threads=4 python-path=/home/dang/Progamming/Pyramid/lib/python2.7/site-packages
       WSGIScriptAlias /myapp /home/dang/Progamming/Pyramid/pyramid.wsgi #Mount at root


       <Directory /home/dang/Progamming/Pyramid/>
    	  WSGIProcessGroup pyramid
	  Order allow,deny
	  Allow from all
       </Directory>

       </VirtualHost>
