## Programming a node ##
Assuming that you have a working version of TinyOS installed and have sourced the appropriate directory, the first step is to change into the Node directory and double check that you have up-to-date code:
```
    cd /opt/cogent-house-read-only/tos/Node
    svn up
```
To install the code on a mote, attach a single mote to your USB port and issue:
```
    make telosb install.n
```
where n should be changed to whatever node number you want. To avoid recompiling, if you have just compiled the code, use:
```
    make telosb reinstall.n
```

## Programming root node ##
To program the server node follow the instructions:
```
    cd /opt/cogent-house-read-only/tos/Root
    svn up
```
Run the same command as before:
```
   make telosb install.m
```