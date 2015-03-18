Check out the current version:
```
hg clone https://code.google.com/p/cogent-house/ cogent-house-read-only
```
Move it into `/opt` so everyone can see it:
```
sudo mv cogent-house-read-only /opt/
```
Make sure you have the `tinyos` environment set up:
```
source /opt/tinyos-main-read-only/tinyos.sh
```
Make the node code:
```
cd /opt/cogent-house-read-only
make all
```

You might get some warnings but you should not get any errors.
Now install the code fully:
```
sudo make install
```

Create the database tables
```
initialize_cogent_db
```

Test that everything starts up after a reboot:
```
sudo reboot
     ...
sudo service ch-sf status
sudo service ch-base status
```
You should see that it starts and stays started. You can also look at the log in `/var/log/ch/BaseLogger.log` and `/tmp/ch-*`
Point your web-browser to:
```
http://<server>/cogent-house/index.py
```
and check that the web portal comes up ok.