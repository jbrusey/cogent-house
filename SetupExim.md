Install exim4:
```
sudo apt-get install exim4
```
Adjust `/etc/exim4/update-exim4.conf.conf` as follows:
```
dc_eximconfig_configtype='smarthost'
dc_other_hostnames=''
dc_local_interfaces='127.0.0.1 ; ::1'
# note: on raspberry pi, remove ::1 from above
dc_readhost='localhost'
dc_relay_domains=''
dc_minimaldns='false'
dc_relay_nets=''
dc_smarthost='smtp.gmail.com::587'
CFILEMODE='644'
dc_use_split_config='false'
dc_hide_mailname='false'
dc_mailname_in_oh='true'
dc_localdelivery='mail_spool'
```
Change `/etc/mailname` to:
```
localhost
```
Copy `` `/etc/exim4/passwd.client` `` file from an existing working server such as cogentee.

Do the update:
```
sudo update-exim4.conf
```
Edit `/etc/aliases` and put in an appropriate redirect for root and chuser. e.g.
```
root: james
james: james.brusey@...il.com
elena: egaura@...il.com
ross: ross.wilkins87@...il.com
ramona: arabeladear@...il.com
chuser: james,elena,ross,ramona
```
To test that it works:
```
echo hi | mail -s test ramona
```

The following cheatsheet is useful for figuring out any problems: http://bradthemad.org/tech/notes/exim_cheatsheet.php