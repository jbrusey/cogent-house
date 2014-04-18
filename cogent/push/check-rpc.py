"""
Script to check if there are any remote procedure calls 
setup at cogentee.
"""

import logging
import logging.handlers
import urllib
import json
import configobj
import sys
import os
import re
import subprocess

import requests


logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(name)-10s %(levelname)-8s %(message)s",
                    datefmt = "%m-%d-%Y %H:%M",
                    )

#Add a File hander (Max of 5 * 5MB Logfiles)
LOGSIZE = (1024*1024) * 5 #5Mb Logs
FH = logging.handlers.RotatingFileHandler("rpc.log",
                                          maxBytes=LOGSIZE,
                                          backupCount = 5)
FH.setLevel(logging.DEBUG)

#Formatter
FMT = logging.Formatter("%(asctime)s %(name)-10s %(levelname)-8s %(message)s")
FH.setFormatter(FMT)


class RPC_Engine(object):
    """Main Class to deal with RPC requests.

    When called this class will connect to cogentee and check
    if there are any Remote procedue calls requested.
    If so it will call the appropriate function
    """

    def __init__(self):
        """Setup the RPC Object"""
        self.log = logging.getLogger(__name__)
        log = self.log
        log.addHandler(FH)

        #Load the config file
        self.read_config()
        hostname, commands = self.checkRPC()
        if commands:
            self.processRPC(hostname, commands)

    def read_config(self):
        """Read the configuration file"""

        log = self.log
        #Read the configuration file
        if sys.prefix  == "/usr":
            conf_prefix = "/" #If its a standard "global" instalation
        else :
            conf_prefix = "{0}/".format(sys.prefix)

        configpath = os.path.join(conf_prefix,
                                  "etc",
                                  "cogent-house",
                                  "push-script")

        configfile = os.path.join(configpath,
                                  "synchronise.conf")

        log.debug("Checking for Config file in {0}".format(configfile))
        if os.path.exists(configfile):
            log.debug("Read config file from {0}".format(configfile))
            configparser = configobj.ConfigObj(configfile)
        else:
            log.warning("No Config file specified Falling back on local copy")
            configfile = "synchronise.conf"

            configparser = configobj.ConfigObj(configfile)

        #Get the merge url
        generaloptions = configparser["general"]

        locations = configparser["locations"]
        for item in locations:
            #Check if we need to synchronise to this location.
            needsync = locations.as_bool(item)
            log.debug("Location {0} Needs Sync >{1}".format(item, needsync))

            if needsync: #Enqueue
                thisloc = configparser[item]["resturl"]
                break

        log.info("Rest URL is {0}".format(thisloc))
        self.resturl = thisloc
        
        #And work out address for ch-ssh
        chssh = os.path.join(conf_prefix,
                             "etc",
                             "cogent-house",
                             "push-script",
                             "ch-ssh")

        log.debug("CH SSH Path {0}".format(chssh))

        self.chssh = chssh

    def checkRPC(self, hostname = None):
        """Check if this server has any RPC

        :param hostname: Host name (<name><id>) to use when checking for RPC
        :return: hostname, list of functions returned by the server
        """
        log = self.log
        log.info("Checking for RPC")

        theUrl = "{0}rpc/".format(self.resturl)

        #Work out my hostname
        if hostname is None:
            hostname = os.uname()[1]
            log.debug("Hostname {0}".format(hostname))

        #Fetch All room Types the Remote Database knows about
        log.debug("Fetching data from {0}".format(theUrl))
        try:
            remoteqry = requests.get(theUrl, timeout=60)
        except requests.exceptions.Timeout:
            log.warning("Timeout on connection to cogentee")
            return

        jsonbody = remoteqry.json()
        log.debug(jsonbody)

        allcommands = []
        for item in jsonbody:
            host, command = item
            if host.lower() == hostname.lower():
                log.debug("Host has RPC queued {0}".format(command))
                allcommands.append(command)

        print "== {0}".format(allcommands)
        return hostname, allcommands

    def processRPC(self, hostname, commands):
        """Process any remote procedure calls

        :param hostname: Hostname we are connecting under
        :param commands: List of RPC commands for this particualr server
        """
        log = self.log
        log.info("Processing RPC")
        #Go through the JSON and see if we have any RPC
        for item in commands:
            log.debug(item)
            if item == "tunnel":
                try:
                    theport = int(re.findall(r"\d+", hostname)[0])
                    log.debug("Port to use is {0}".format(theport))
                except ValueError:
                    log.warning("Unable to get port from hostname {0}"
                                .format(hostname))
                    theport = 0

                log.debug("Attempting to start SSH Process on port {0}"
                          .format(theport))
                proc = subprocess.Popen([self.chssh,
                                         "start" ,
                                         "{0}".format(theport)],
                                        stderr=subprocess.PIPE)

                for line in iter(proc.stderr.readline, ''):
                    log.debug("E-> {0}".format(line.strip()))

                log.debug("Killing existing SSH Process")
                    #Wait for Exit then Kill
                subprocess.check_output([self.chssh,
                                         "stop"], shell=True)

if __name__ == "__main__":
    log = logging.getLogger("__name__")
    logging.info("Starting Engine")
    engine = RPC_Engine()
