The database schema is set up automatically by the python script, however it is still necessary to set up the database:
```
sudo mysql -p
```
At this stage, you will need to enter the root MySQL password.

Now create the database and give appropriate privileges:
```
create database ch;
grant all on ch.* to chuser@localhost;
flush privileges;
```
Note that you may also want to give access to your maintenance team:
```
grant all on ch.* to fred@localhost;
flush privileges;
```
This is all we need from mysql at the moment, so exit
```
exit
```

Add a user to run cogent-house under:
```
sudo useradd -c 'Cogent House User' -m chuser
```
Do not set a password. If you need to login to this username, use `sudo -s -u chuser`