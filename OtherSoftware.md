### Install important packages ###

Make sure apt-get's list is up to date:
```
sudo apt-get update
```
Install any pending fixes:
```
sudo apt-get upgrade
```
Install essential build tools for TinyOS and a number of other packages needed for cogent-house
```
sudo apt-get install autoconf automake gawk build-essential libtool \
    openssh-server mysql-server subversion apache2 \
    python-setuptools python-dev python-mysqldb openjdk-6-jdk emacs23 \
    libapache2-mod-python python-matplotlib avahi-daemon graphviz ntp \
    mercurial
```
Note that this will ask to set up a root password for your MySQL
database and you'll need this later on.

Install SQLAlchemy, transaction, and alembic
```
sudo easy_install SQLAlchemy transaction alembic
```