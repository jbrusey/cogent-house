## Install Ubuntu ##

A good place to start is the Ubuntu Community documentation:
https://help.ubuntu.com/community/Installation

We generally go for a "Ubuntu Server" style system as this defaults to
not installing unnecessary GUI features.

No further details of how to do this are provided here though, so come
back when you are done.

## Set for booting after a power failure (optional) ##

Setting your system to boot after power failure will help minimise the
resulting loss of data. Here is an example of how to change the BIOS
settings to support this:

Update BIOS settings to ensure that it boots after a power failure.
```
Enter into BIOS setup > Power Management setup > ErP (EUP) function > Disable
Go up a level (ESC) > Integrated Peripherals > PWR status after PWR failure > Always ON
```

## Add users as necessary (optional) ##

Make user names for your system maintainers and ensure that they are admins
```
sudo useradd -c 'person name' -m -s /bin/bash \
-G admin,adm,dialout,cdrom,plugdev,lpadmin,sambashare person
sudo passwd person
```

Note that as of Ubuntu 12.04, the admin group is now called sudo, so the following should be used instead:
```
sudo useradd -c 'person name' -m -s /bin/bash \
-G sudo,adm,dialout,cdrom,plugdev,lpadmin,sambashare person
sudo passwd person
```