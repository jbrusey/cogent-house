"""
Display server status
"""

import logging
log = logging.getLogger(__name__)

import datetime
import subprocess
import urllib

from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import view_config

from sqlalchemy import func

import homepage

from cogentviewer.models import meta
import cogentviewer.models as models

def generate_netmap():
    """Generate a network map of all deployments"""
    session = meta.Session()

    now = datetime.datetime.utcnow()



    #Query for nodestates

    qry = session.query(models.NodeState.parent,
                        models.NodeState.nodeId,
                        func.max(models.NodeState.time),
                        func.avg(models.NodeState.rssi),
                        func.count(models.NodeState.nodeId),
                        )

    #qry = qry.filter(models.NodeState.time > now - datetime.timedelta(days=7))
    #Ignore error node
    qry = qry.filter(models.NodeState.parent != 65535)
    qry = qry.group_by(models.NodeState.nodeId, models.NodeState.parent)

    networkbins = {}
    #First Pass to get everything binned
    graph_nodelist = [] #Temp list to hold output file

    nodedict = {}
    nodelist = []

    for item in qry:
        parentlist = networkbins.get(item[0], [])
        parentlist.append(item)
        networkbins[item[0]] = parentlist

        graph_nodelist.append('{0} -> {1} [label={2}]\n'.format(item[0],
                                                                item[1],
                                                                item[4]))

        thisnode = {"node":item[1],
                    "lasttx":item[2]}
        nodelist.append(thisnode)

    #import pprint
    #pprint.pprint(networkbins)

    #Fetch All Servers

    serverlist = []
    session = meta.Session()
    servers = session.query(models.Server)
    graph_serverlist = []
    for item in servers:
        log.debug("Houses {0}".format(item.houses))

        #houseqry = session.query(models.House).filter_by(id = item.houseid).first()
        address = [x.address for x in item.houses]
        #if houseqry:
        #    address = houseqry.address

        thisserver = {"server" : item.hostname,
                      "baseid" : item.baseid,
                      "house"  : address,
                      "nodes"  : []
                      }

        serverstr = """{0} [shape=Mrecord,label="{{ Server:{1} | Address: {2} | Node: {0}  }}"]\n""".format(item.baseid,
                                                                                                          item.hostname,address)
        graph_serverlist.append(serverstr)
        graph_serverlist.append("cogentee -> {0}\n".format(item.baseid))

        #And build up our node list
        if item.baseid:
            nodelist = []
            allnodes = networkbins.pop(item.baseid, None)
            if allnodes:
                nodelist = [x[1] for x in allnodes]
                while nodelist:
                    print "Node list for {0} {1}".format(item.baseid, nodelist)
                    for childnode in nodelist:
                        newnodes = []
                        popnodes = networkbins.pop(childnode, None)
                        if popnodes:
                            allnodes.extend(popnodes)
                            newnodes.extend([x[1] for x in popnodes])

                    nodelist = newnodes


            thisserver["nodes"] = allnodes


        serverlist.append(thisserver)

    #import pprint
    #pprint.pprint(networkbins)
    thisserver = {"server": "No Server",
                  "baseid": "N/A",
                  "house" : "N/A",
                  "nodes" : [],
                  }
    nodes = []
    for key, value in networkbins.iteritems():
        nodes.extend(value)
    thisserver["nodes"] = nodes
    serverlist.append(thisserver)

    fd = open("outfile.txt","w")
    fd.write("digraph g {\n")
    fd.write('rankdir="LR"\n')
    fd.write("cogentee\n")
    fd.writelines(graph_serverlist)
    fd.writelines(graph_nodelist)
    fd.write("}\n")
    fd.close()

    #And write our graph
    dot = subprocess.Popen(["dot -Tpng",],
                           shell=True,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           close_fds=True)

    with dot.stdin as dotfile:
        dotfile.write("digraph g {\n")
        dotfile.write('rankdir="LR"\n')
        dotfile.write("cogentee\n")
        dotfile.writelines(graph_serverlist)
        dotfile.writelines(graph_nodelist)
        dotfile.write("}\n")

    #imgfile = dot.stdout.read()
    with open("cogentviewer/static/netmap.png","w") as fd:
        for line in dot.stdout.read():
            fd.write(line)

    imgfile = None


    return serverlist, imgfile


@view_config(route_name='server',
             renderer='cogentviewer:templates/server.mak',
             permission="view")

def showserver(request):
    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)
    theUser = homepage.getUser(request)
    outDict["user"] = theUser.username

    outDict["nodeDropdowns"] = homepage.getNodeDropdowns()
    outDict["pgTitle"] = "Server Status"

    #populateSalford()


    #Get a list of servers
    servertable = []

    session = meta.Session()
    servers = session.query(models.Server)
    now = datetime.datetime.utcnow()


    outDict["currenttime"] = now

    for server in servers:
        thisrow = {"servername":server.hostname,
                   "baseid":server.baseid}

        thisrow["address"] = None #Address of server
        thisrow["lastpush"] = None #When the last push happend
        thisrow["laststate"] = None #When the last state was reported
        thisrow["skew"] = None #What (if any clock skew there is)
        thisrow["nodes"] = None
        thisrow["node_state" ] = None
        thisrow["reportingnodes"] = None

        thisrow["push_state"] = "warning" #Formatting for the pushstate
        thisrow["state_state"] = None #Formatting for the nodestate
        thisrow["skew_state"] = "warning" #Formatting for the skew state
        rowstate = ""
        #if server.houseid:
        houseqry = session.query(models.House).filter_by(serverid = server.id)

        heartbeat_time = datetime.datetime.now() - datetime.timedelta(hours = 8)
        if houseqry.count() > 0:
            thisrow["address"] = houseqry.count()
            #Work out locations assocatated with these houses
            
            all_locs = []
            for house in houseqry:
                all_locs.extend(house.locations)

            print all_locs
            
            nodecount = 0
            reportingcount = 0

            for loc in all_locs:
                for node in loc.nodes:
                    #Increment the number of nodes
                    nodecount +=1
                    #Check if we have data

                    lastreport = session.query(models.NodeState).filter_by(nodeId = node.id).filter(models.NodeState.time > heartbeat_time).first()
                    if lastreport:
                        reportingcount +=1
                        
            thisrow["nodes"] = nodecount
            thisrow["reportingnodes"] = reportingcount
            # if False:
                
                
                
            #     #thisrow["address"] = qry.address

                
                
            #     #Nodes associated with this house
            #     houselocations = qry.locations
            #     housenodes = []
            #     for loc in houselocations:
            #         locnodes = loc.nodes
            #         #if locnodes:
            #         for x in locnodes:
            #             lastreport = session.query(models.NodeState).filter_by(nodeId = x.id).order_by(models.NodeState.time.desc()).first()
            #             if lastreport is not None:
            #                 lasttime = lastreport.time
            #                 nodestate = "error"
            #                 reportdelta = now - lasttime
            #                 if reportdelta.days < 1:
            #                     nodestate = "info"
            #                     if reportdelta.seconds < 8*(60*60):
            #                         nodestate = "success"
            #                 housenodes.append(["{1} : {2}".format(loc.id,loc.room.name, x.id), lasttime, nodestate])

            #             else:
            #                 housenodes.append(["{1} : {2}".format(loc.id,loc.room.name, x.id), None, None])


            #     thisrow["nodes"] = housenodes


            #--- Nodestate (last push) Details ----
            qry = session.query(func.max(models.NodeState.time)).filter_by(parent = server.baseid)
            qrytime = qry.first()
            log.debug(qrytime)
            #rowstate = "error"

            #thisrow["laststate_days"] = None

            qrytime = qrytime[0]
            if qrytime:
                td = now - qrytime
                rowstate = "error" #Default
                #if td.days >= 1:

                if td.days <= 1:
                    rowstate = "info"
                    if td.seconds < 8*(60*60):
                        rowstate = "success"
            else:
                qrytime = None

            thisrow["laststate"] = qrytime
            thisrow["state_state"] = rowstate

        #Last Push State
        #qry = session.query(func.max(models.PushStatus.time)).filter_by(hostname = server.hostname)
        qry = session.query(models.PushStatus).filter_by(hostname = server.hostname)
        qry = qry.order_by(models.PushStatus.time.desc())
        result = qry.first()
        if result:
            thisrow["lastpush"] = result.time
            #Do States
            tdelta = now - result.time
            push_state = "warning"
            if tdelta.days < 1:
                push_state = "error"
                if tdelta.seconds < (60*60)*2:
                    push_state = "success"

            thisrow["push_state"] = push_state

            # if tdelta.days > 1:
            #     thisrow["push_state"] = "error"
            # elif tdelta.seconds < (60*60)*2:
            #     thisrow["push_state"] = "success"

            skewdelta = result.time - result.localtime
             # "Local Delta {0} {1} = {2} ({3})".format(result.time,
             #                                               result.localtime,
             #                                               skewdelta,
             #                                               skewdelta.days)
            thisrow["skew"] = skewdelta
            skew_state = "error"
            if skewdelta.days < 1:
                if skewdelta.seconds < 60*30:
                    skew_state = "success"
            thisrow["skew_state"] = skew_state



            # if ldelta.days < 1:
            #     if ldelta.days < 0:
            #         thisrow["skew_state"] = "error"
            #     elif ldelta.seconds < 60:
            #         thisrow["skew_state"] = "success"
            #     elif ldelta.seconds < 60*30:
            #         thisrow["skew_state"] = "warning"

        servertable.append(thisrow)

    outDict["servertable"] = servertable
    outDict["serverlist"] = []
    #netlist, netmap = generate_netmap()
    #outDict["serverlist"] = netlist
    #outDict["servermap"] = netmap

    return outDict
