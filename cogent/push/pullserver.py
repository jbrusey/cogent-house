"""
Code to pull a configureation from the base server
"""

import logging
import logging.handlers

import os
import sys
import datetime
import curses

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(name)-10s %(levelname)-8s %(message)s",
                    datefmt = "%m-%d-%Y %H:%M",
                    )

#Add a File hander (Max of 5 * 5MB Logfiles)
LOGSIZE = (1024*1024) * 5 #5Mb Logs
FH = logging.handlers.RotatingFileHandler("push.log",
                                          maxBytes=LOGSIZE,
                                          backupCount = 5)
FH.setLevel(logging.DEBUG)

#Formatter
FMT = logging.Formatter("%(asctime)s %(name)-10s %(levelname)-8s %(message)s")
FH.setFormatter(FMT)

#Library Imports
import sqlalchemy
import dateutil.parser
import json
import urllib
import requests
import configobj
import time
#Local Imports
import cogent.base.model as models

from cogent.push.dictdiff import DictDiff

#Disable Requests Logging
REQUESTS_LOG = logging.getLogger("requests")
REQUESTS_LOG.setLevel(logging.WARNING)

RESULTS_PER_PAGE = 15


class PullServer(object):
    """Class to deal with pulling a configuration from a remote server"""
    def __init__(self):
        """Initliase the Remote Pull (As per Merge Script)"""
        self.log = logging.getLogger(__name__)
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
        if os.path.exists(configfile):
            log.debug("Read config file from {0}".format(configfile))
            configparser = configobj.ConfigObj(configfile)
        else:
            log.warning("No Config file specified Falling back on local copy")
            configfile = "synchronise.conf"

            configparser = configobj.ConfigObj(configfile)

        #Get the merge url
        generaloptions = configparser["general"]
        mergeurl = generaloptions["localurl"]

        log.info("Connecting to Merge Engine at {0}".format(mergeurl))
        mergeengine = sqlalchemy.create_engine(mergeurl)
        mergesession = sqlalchemy.orm.sessionmaker(bind=mergeengine)
        self.mergesession = mergesession

        #And the Rest url (Just the first active location)
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
        self.locationmap = {}
    
    def init_curses(self):
        """Create a nice curses infterface"""
        screen = curses.initscr()
        curses.noecho() #Dont Echo Resposnes to Screen
        curses.curs_set(0)  #Remove Cursor
        screen.keypad(1) # Allow Keypad
        
        self.screen = screen
        
    def teardown_curses(self):
        curses.endwin()

    def mainmenu(self):
        """Main Menu (ie what do we want to do today)"""
        screen = self.screen
        subwin = screen.subwin(23, 79, 0, 0)
        #subwin = screen.subwin(23, 79, 0,0) #DG HACK
        subwin.box()
        subwin.addstr(1,1,"Select Operation?")
        subwin.hline(2,1,curses.ACS_HLINE,77)

        #Menu Options
        subwin.addstr(3, 1, "D: Download Deployment")
        subwin.addstr(4, 1, "H: Download House")
        
        subwin.addstr(20, 1, "Q: Quit")      
        self.subwin = subwin
        screen.refresh()
        #And wait for input
        while True:
            event = screen.getch()        
            if event == ord("d"):
                subwin.erase()
                output = self.deploymentmenu()
                break
            elif event == ord("h"):
                subwin.erase()
                output = self.housemenu()
                break
            elif event == ord("q"):                
                return
                break
                


    def housemenu(self):
        """Menu to deal with mirroring Houses"""
        screen = self.screen
        subwin = self.subwin

        subwin.erase()
        subwin.box()
        subwin.addstr(1,1,"Mirror Which house?")
        subwin.hline(2,1,curses.ACS_HLINE,77)
        
        theurl = "{0}house/".format(self.resturl)
        therequest = requests.get(theurl)
        therequest = therequest.json()
        current_offset = 0        

        total_pages = int(len(therequest) / RESULTS_PER_PAGE)
        subwin.addstr(3,1,"----- Page {0} of {1} ----".format(current_offset, total_pages))
        self.printhouses(subwin, therequest, current_offset)

        
        # for item in therequest.json()[0:15]:
        #     if item.get("address", None):
        #         subwin.addstr(screenidx, 1, "{0}: {1}".format(item.get("id",None),
        #                                                       item.get("address","None")))
        #         screenidx += 1
        #     else:
        #         print "ERROR WITH ITEM ",item
            #allowedinput.append(ord(str(item["id"])))
        subwin.addstr(20,1, "Q: Quit  B: Back  F: Forth  H: Select House")
        subwin.refresh()
        screen.refresh()
                          
        while True:
            event = screen.getch()
            if event == ord("q"):
                return False
            elif event == ord("f"):
                if current_offset < total_pages:
                    current_offset += 1
                    self.printhouses(subwin, therequest, current_offset)
                    subwin.addstr(3,1,"----- Page {0} of {1} ----".format(current_offset, total_pages))
                    subwin.refresh()
            elif event == ord("b"):
                if current_offset > 0:
                    current_offset -= 1
                    self.printhouses(subwin, therequest, current_offset)
                    subwin.addstr(3,1,"----- Page {0} of {1} ----".format(current_offset, total_pages))
                    subwin.refresh()
            elif event == ord("h"):
                #Switch to house input mode
                curses.echo()

                subwin.addstr(20,1,"Please enter house id followed by return:      ", curses.A_STANDOUT)
                screen.move(20,42)
                subwin.refresh()
                hstr = screen.getstr()
                curses.noecho()
                self.download_house(hstr)
                print hstr

                return

    def download_house(self, hstr):
        screen = self.screen
        subwin = self.subwin

        
        session = self.mergesession()


        subwin.erase()
        subwin.box()
        subwin.addstr(1, 1, "Mirror House to server".format(hstr))
        subwin.hline(2, 1, curses.ACS_HLINE,77)

        #Fetch this particular house
        theurl = "{0}house/{1}".format(self.resturl, hstr)
        therequest = requests.get(theurl)
        jsonhouse = therequest.json()


        if len(jsonhouse) == 0:
            subwin.addstr(5,1,"NO SUCH HOUSE") 
            subwin.addstr(20,1, "Any key to exit")
            subwin.refresh()
            event = screen.getch()
            return
        else:

            thehouse = models.clsFromJSON(jsonhouse).next()
            originalid = thehouse.id
            qry = session.query(models.House).filter_by(address = thehouse.address).first()
            if qry is None:
                matchstr = "No Match"
                thehouse.id = None
                session.add(thehouse)
                session.flush()
            else:
                #matchstr = "({0}) {1}".format(qry.id, qry.address)
                thehouse = qry

            
        
        #Fetch Relevant deployment (Which should have been synched allready)
        if thehouse.deploymentId is None:
            subwin.addstr(5, 1, "Deployment:  None")

        else:
            theurl="{0}deployment/{1}".format(self.resturl, thehouse.deploymentId)
            therequest = requests.get(theurl)
            jsondep = therequest.json()
            thedeployment = models.clsFromJSON(jsondep).next()
            
            #Check mappings for this
            qry = session.query(models.Deployment).filter_by(name=thedeployment.name).first()
            if qry is None:
                #matchstr = "No Match"
                thedeployment.id = None
                session.add(thedeployment)
                session.flush()
                thehouse.deploymentId = thedeployment.id
            else:
                #matchstr = "({0}) {1}".format(qry.id, qry.name)
                thedeployment = qry
                thehouse.deploymentId = qry.id


        #And Update our House / Deployment Strings
        session.flush()
        subwin.addstr(4, 1, "House: {0} (Local) {1} {2} {3}".format(str(thehouse.address), thehouse.id, thehouse.address, thehouse.deploymentId))
        if thehouse.deploymentId is not None:
            subwin.addstr(5, 1, "Deployment: {0}  (Local) {1} {2}".format(thedeployment.name, thedeployment.id, thedeployment.name))

        #Fetch Locations
        params = urllib.urlencode({"houseId" : originalid})
        houseurl = "{0}location/?{1}".format(self.resturl, params)
        restqry = requests.get(houseurl)
        jsonstr = restqry.json()
        locations = models.clsFromJSON(jsonstr)

        roomurl = "{0}room/".format(self.resturl)
        restqry = requests.get(roomurl)
        jsonstr = restqry.json()
        ritr = models.clsFromJSON(jsonstr)
        rooms = {}
        for item in ritr:
            rooms[item.id] = item

        locidx = 7
        mappedlocs = {}
        #And a place for Nodes
        #nodelist = []

        for item in locations:
            roomqry = session.query(models.Room).filter_by(name = rooms[item.roomId].name).first()
            if roomqry is None:
                print "NEW ROOM {0}".format(item)
                #Add a Room (But these should have been synched)
            locqry = session.query(models.Location).filter_by(houseId = thehouse.id,
                                                              roomId = roomqry.id).first()

            #outstr = "{0} : {1} : {2}".format(item, roomqry, locqry)
            if locqry is None:
                mappedloc = models.Location(houseId = thehouse.id,
                                            roomId  = roomqry.id)
                session.add(mappedloc)
                session.flush()
                locstr = "NEW location: {0}".format(mappedloc)
            else:
                locstr = "Existing location: {0}".format(locqry)
                mappedloc = locqry                
            
            #Work out nodes
            params = urllib.urlencode({"locationId": item.id})
            nodeurl = "{0}node/?{1}".format(self.resturl, params)
            nodeqry = requests.get(nodeurl)
            nodestr = nodeqry.json()
            nodes = list(models.clsFromJSON(nodestr))
            for node in nodes:
                #Just Create this node
                nodeqry = session.query(models.Node).filter_by(id = node.id).first()
                
                if nodeqry is None:
                    thenode = models.Node(id = node.id, locationId = mappedloc.id)
                    session.add(thenode)
                    session.flush()
                    outstr = "Create node {0} at {1} ({2})".format(node.id, locstr, rooms[item.roomId].name)
                else:
                    outstr = "Update Node {0} to {1} ({2})".format(node.id, locstr, rooms[item.roomId].name)
                    #outstr = "Node {0} : {1}".format(node.id, outstr)
                    nodeqry.locationId = mappedloc.id

                subwin.addstr(locidx, 1, outstr)
                locidx +=1

        session.flush()


        subwin.addstr(20,1, "Confirm (Y)es (N)o")
        subwin.refresh()
        screen.refresh()

        while True:
            event = screen.getch()
            if event == ord("y"):
                print "SAVING"
                session.flush()
                session.commit()
                return
            elif event == ord("n"):
                print "EXITING"
                return


        
        
    def printhouses(self, subwin, therequest, offset):
        screenidx = 4
        allowedinput = []
        start = offset*RESULTS_PER_PAGE
        end = (offset+1) * RESULTS_PER_PAGE
        for item in therequest[start:end]:
            if item.get("address", None):
                subwin.addstr(screenidx, 1, "{0}: {1}".format(item.get("id",None),
                                                              item.get("address","None")))
                screenidx += 1
            else:
                print "ERROR WITH ITEM ",item
            #allowedinput.append(ord(str(item["id"])))
        subwin.refresh()


    def deploymentmenu(self):
        """Menu to deal with mirroring deployments"""
        screen = self.screen
        subwin = self.subwin
        
        subwin.erase()
        subwin.box()
        subwin.addstr(1,1,"Download Which Deployment?")
        subwin.hline(2,1,curses.ACS_HLINE,77)
        
        #We now want to fetch all the deployments from the remote server
        theurl = "{0}deployment/".format(self.resturl)
        therequest = requests.get(theurl)

        allowedinput = []
        screenidx = 4
        for item in therequest.json():
            subwin.addstr(screenidx, 1, "{0}: {1}".format(item["id"],
                                                          item["name"]))
            allowedinput.append(ord(str(item["id"])))
            screenidx += 1

        subwin.addstr(20, 1, "Q: Quit") 

        subwin.refresh()
        screen.refresh()

        while True:
            event = screen.getch() 
            if event == ord("q"):  
                return False
                break
            elif event in allowedinput:
                self.download_deployment(chr(event))
                break

    def download_deployment(self, deploymentid):
        """Download a deployment"""
        log = self.log
        log.info("Download Deployment {0}".format(deploymentid))
        
        screen = self.screen
        subwin = self.subwin

        #Fetch the relevant deployment and stick it in our testing database
        theurl = "{0}deployment/{1}".format(self.resturl, deploymentid)
        therequest = requests.get(theurl)
        jsonstr = therequest.json()
        log.info("Deployment is {0}".format(jsonstr))

        restitems = models.clsFromJSON(jsonstr)

        session = self.mergesession()
        outstr = []


        remoteid = None

        for item in restitems:
            remoteid = item.id
            localid = item.id
            #Check if it exists
            qry = session.query(models.Deployment).filter_by(name = item.name).first()

            if qry is None:
                #No Such Deployment
                #Check there is no mismatch on Id
                qry = session.query(models.Deployment).filter_by(id = item.id).first()
                if qry is None:
                    session.add(item)
                    outstr.append("Item {0} Successfully Added".format(item))
                else:
                    print "ID MISMATCH"
                    item.id = None
                    print item
                    session.add(item)
                    outstr.append("Item {0} added with new Id".format(item))

            else:
                outstr.append("Item {0} Has matching local deployment: Ignoring".format(item))

            # session.flush()
            # session.commit()

            localid = item.id
            outstr.append("Ids are L {0} R {1}".format(localid, remoteid))
  
        subwin.clear()
        subwin.box()
        curidx = 3
        subwin.addstr(1,1,"Deployment")
        subwin.hline(2,1,curses.ACS_HLINE,77)
        for line in outstr:
            subwin.addstr(curidx,1,line)
            curidx+= 1

        subwin.addstr(20,1,"(C)ontinue")                
        subwin.refresh()
        screen.refresh()
        


        while True:
            event = screen.getch() 
            if event == ord("c"):  
                self.download_houses(remoteid)
                break
        

    def download_houses(self, remoteid):
        """Download the Houses"""
          
        screen = self.screen
        subwin = self.subwin

        params = urllib.urlencode({"deploymentId" : remoteid})
        houseurl = "{0}house/?{1}".format(self.resturl, params)
        restqry = requests.get(houseurl)
        jsonstr = restqry.json()

        restitems = models.clsFromJSON(jsonstr)

        subwin.clear()
        subwin.addstr(1,1,"House")
        subwin.hline(2,1,curses.ACS_HLINE,77)
        
        session = self.mergesession()

        curidx = 3
        for item in restitems:
            
            qry = session.query(models.House).filter_by(address = item.address).first()
            if qry is None:
                subwin.addstr(curidx, 1, "Adding House {0}".format(item))
                session.add(item)
                # session.flush()
                # session.commit()
            else:
                if qry.id == item.id:
                    subwin.addstr(curidx, 1, "House {0} Exists".format(item))
                else:
                    subwin.addstr(curidx, 1, "Error Adding House {0}".format(item))

            self.add_locations(item.id)
            curidx+=1
        

        
            
        subwin.addstr(20,1,"(C)ontinue")                
        subwin.refresh()
        screen.refresh()
        

        while True:
            event = screen.getch() 
            if event == ord("c"):  
                break


    def add_locations(self,houseid):
        """Add the relevant locations to the database"""

        params = urllib.urlencode({"houseId" : houseid})
        houseurl = "{0}location/?{1}".format(self.resturl, params)
        restqry = requests.get(houseurl)
        jsonstr = restqry.json()

        restitems = models.clsFromJSON(jsonstr)

        session = self.mergesession()
        for item in restitems:
            qry = session.query(models.Location).filter_by(id = item.id).first()
            if not qry:
                # session.add(item)
                # session.flush()
                pass

            #And Check for the Node
            nodeparams = urllib.urlencode({"locationId": item.id})
            nodeurl = "{0}node/?{1}".format(self.resturl, nodeparams)
            nodeqry = requests.get(nodeurl)
            restnodes = models.clsFromJSON(nodeqry.json())
            
            for node in restnodes:
                session.merge(node)
                session.flush()

        session.commit()
            
            #And update the node



if __name__ == "__main__":
    server = PullServer()
    server.init_curses()
    #curses.wrapper(server.mainmenu())
    server.mainmenu()
    server.teardown_curses()
