### Signup for No-IP service ###
Go to the following address and sign up for an account
```
http://www.no-ip.com/
```

When you have created an account and logged on, create a free host with the following format
```
<server_name>-ch.hopto.org
```

### Install No-IP ###
SSH into the server

Install noip2
```
cd 
wget http://www.no-ip.com/client/linux/noip-duc-linux.tar.gz
tar xf noip-duc-linux.tar.gz
cd noip-2.1.9-1/
sudo make install
```

You will then be prompted to login with your No-IP.com account username and password.

### Add in a start up script ###

Create an upstart script
```
cat >noip2.conf <<EOF
# noip2.conf
#
# start noip2
#
# 
#

description "NoIP2 to update ip address periodically"
author "J. Brusey <james.brusey@gmail.com>"

start on (net-device-up
          and local-filesystems
          and runlevel [2345])
stop on runlevel [016]

expect fork

script 
  exec /usr/local/bin/noip2
end script
EOF
sudo mv -i noip2.conf /etc/init/
```

Start the script running
```
sudo service noip2 start
```

You can check to see that it is running ok by looking at the log
```
tail /var/log/syslog
```

### To configure noip ###
To reconfigure noip later on, issue the command:
```
sudo /usr/local/bin/noip2 -C
```

You will then be prompted for your username and password for No-IP, as well as which host names you with to update. Be careful, one of the questions is "Do you wish to update all hosts". If answered incorrectly this could effect host names in your account that are pointing at other locations.

Now the client is installed and configured, reboot the system