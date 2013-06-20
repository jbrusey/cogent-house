My Install Notes
==================

For upgrading servers to the latest version of the code

Prep
-----

Update /etc/dhcp3/dhclient.conf::

   prepend domain-name-servers 208.67.222.222,208.67.220.220;


Install following packages::

   $sudo apt-get update
   $sudo apt-get install python-dev python-pip python-virtualenv libmysqlclient-dev bzr curl

Update PIP::

    $curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | sudo python

Stop all services::

    $sudo service ch-base stop
    $sudo service ch-sf stop

Remove old cronjobs::

    sudo rm /etc/cron.daily/yieldSender 

   
Base Code
----------

SCP Latest version of the basestation code from my machine and install with setup.py develop

There may be an issue with mysql python,  in which case::

    $sudo easy_install mysql-python

Backup the DB::

    $mysqldump -u chuser -l -v ch > preupgrade.sql

And upgrade::

    $cd ~/djgoldsmith-devel/cogent/
    $sudo pip install alembic
    $alembic upgrade head

Restart services::

    $sudo service ch-base start
    $sudo service ch-sf start


Webinterface
--------------

Grab latest web interface from My Machine (Over Shared Network)::

    $bzr clone bzr+ssh://dang@10.42.0.1/home/dang/WebInterface/viewer-repo/webinterface.graphs webinterface

And install on the host machine

    $sudo python setup.py develop

Copy JS Librarys from my machine And fix up links::

   dan@euler:~/tar -xvf jslibs.tar.gz
   dan@euler:~/cd jslibs
   dan@euler:~/jslibs$ ln -s dojo-release-1.8.0/ dojo
   dan@euler:~/jslibs$ ln -s Highcharts-2.3.2/ Highcharts
   dan@euler:~/jslibs$ ln -s Highstock-1.2.2/ Highstock
   dan@euler:~/jslibs$ cd ../webinterface/cogentviewer/
   dan@euler:~/webinterface/cogentviewer$ ln -s /home/dan/jslibs .


Enable proxy::

    sudo a2enmod proxy_http

And edit /etc/apache2/sites-available/default::

    ProxyRequests Off
    ProxyPreserveHost On

    <Proxy *>
        Order allow,deny
        Allow from all
    </Proxy>

    ProxyPass /webInterface/ http://localhost:6543/
    ProxyPassReverse /webInterface/ http://localhost:6543/


Restart Apache and manually start webinterface::

    sudo /etc/init.d/apache2 restart
    pserve proxy.ini

Test by visiting http://euler.local/webInterface/timeseries

Setup webinterface auto start in /etc/init/webinterface.conf::

    description "Start Orbit Web Interface"
    author "Dj Goldsmith"

    start on runlevel [2345]
    stop on runlevel [016]

    script
        exec > /tmp/webinterface.out 2>&1
        cd /home/dan/webinterface
        exec pserve proxy.ini
    end script












