""" 
Display server status
"""

import logging
log = logging.getLogger(__name__)

import datetime

from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import view_config

import homepage

from ..models import meta
import cogentviewer.models as models

from sqlalchemy import func

def generate_netmap():
    """Generate a network map of all deployments"""
    session = meta.Session()
    
    #now = datetime.datetime.now()

    now = datetime.datetime(2014,01,07,16,45,00)

    #Query for nodestates
    #now = datetime.datetime(2014,01,07,16,45,00)
    qry = session.query(models.NodeState.parent,
                        models.NodeState.nodeId,
                        func.max(models.NodeState.time),
                        func.avg(models.NodeState.rssi),
                        func.count(models.NodeState.nodeId),
                        )

    qry = qry.filter(models.NodeState.parent != 65535)
    qry = qry.filter(models.NodeState.time > now - datetime.timedelta(days=7))
    qry = qry.group_by(models.NodeState.nodeId, models.NodeState.parent)

    networkbins = {}
    #First Pass to get everything binned
    graph_nodelist = [] #Temp list to hold output file

    #htmlstr = '<table border=1><tr><td>Id:</td><td>"{0}"</td></tr><tr><td>Last Tx:</td><td>"{1}"</td></tr></table>'

    nodedict = {}
    nodelist = []

    for item in qry:
        parentlist = networkbins.get(item[0],[])            
        parentlist.append(item)
        networkbins[item[0]] = parentlist
           
        #graph_nodelist.append('{0} [label=<<table border="1"><tr><td>Id:</td><td>"{0}"</td></tr><tr><td>Last Tx:</td><td>"{1}"</td></tr></table>>]\n'.format(item[1],item[2]))

        graph_nodelist.append('{0} -> {1} [label={2}]\n'.format(item[0],item[1],item[4]))
        #Add the item to the nodedict
        # thisnode =  nodedict.get(item[1],None)
        # if thisnode is None:
        #     thisnode = {"node":item[1],
        #                 "lasttx":item[2]}
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
        houseqry = session.query(models.House).filter_by(id = item.houseid).first()
        address = None
        if houseqry:
            address = houseqry.address

        thisserver = {"server" : item.hostname,
                      "baseid" : item.baseid,
                      "house"  : address,
                      "nodes"  : []                 
                      }

        graph_serverlist.append('{0} [shape=Mrecord, label="{{ Server:{1} | Address: {2} | Node: {0}  }}"]\n'.format(item.baseid,item.hostname,address))
        graph_serverlist.append("cogentee -> {0}\n".format(item.baseid))

        #And build up our node list            
        if item.baseid:
            nodelist = []
            allnodes = networkbins.pop(item.baseid, None)
            if allnodes:
                nodelist = [x[1] for x in allnodes]
                while nodelist:
                    print "Node list for {0} {1}".format(item.baseid,nodelist)
                    for childnode in nodelist:
                        newnodes = []
                        popnodes = networkbins.pop(childnode, None)
                        print "--> Checking {0} for Children {1}".format(childnode,popnodes)
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
#    print "="*60
    for key, value in networkbins.iteritems():
#        print key,value
        nodes.extend(value)
#        print "-"*30
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


    return serverlist
    #return networkbins

    # #First we want a list of all base nodes
    # root = {'name' : "Server",
    #         'nid' : None,
    #         'lasttx' : now,
    #         'children' : None}
    
    # #Now we want to fetch all children for this deployment
    # children = []
    # qry = session.query(models.Server)
    # for item in qry:
    #     if item.houseid:
    #         hqry = session.query(models.House).filter_by(id = item.houseid).first()
            
    #         children.append({"name":hqry.address, 
    #                          "nid" :item.baseid})



    #root["children"] = children
    #import pprint
    #print pprint.pprint(root)

def get_children(nodeid):
    """Helper function to find children for a given node

    :param nodeid: Id of node to search for
    :return: Either a list of child nodes or None
    """

    
    pass
    
    

@view_config(route_name='server', renderer='cogentviewer:templates/server.mak',permission="view")
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
    #now = datetime.datetime.now()
    now = datetime.datetime(2014,01,27,11,00,00)

    for server in servers:
        thisrow = {"servername":server.hostname,
                   "baseid":server.baseid}

        thisrow["address"] = None
        thisrow["lastpush"] = None
        thisrow["laststate"] = None
        thisrow["localtime"] = None
        thisrow["state_state"] = None
        thisrow["push_state"] = "warning"
        thisrow["local_state"] = "warning"
        rowstate = ""
        if server.houseid:
            qry = session.query(models.House).filter_by(id=server.houseid).first()
            if qry:
                thisrow["address"] = qry.address

            #Last Nodestate
            qry = session.query(func.max(models.NodeState.time)).filter_by(parent = server.baseid)
            qrytime = qry.first()
            log.debug(qrytime)
            #rowstate = "error"


            thisrow["laststate_days"] = None

            qrytime = qrytime[0]
            if qrytime:
                td = now - qrytime
                #if td.days >= 1:
                rowstate = "info"

                if td.days >= 3:
                    rowstate = "error"
                elif td.days >= 2:
                    rowstate = "warning"

                else:
                    if td.seconds <= 8*(60*60):
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
            thisrow["localtime"] = result.localtime
            #Do States
            tdelta = now - result.time
            if tdelta.days > 1:
                thisrow["push_state"] = "error"
            elif tdelta.seconds < (60*60)*2:
                thisrow["push_state"] = "success"
        
            ldelta = result.time - result.localtime
            print "Local Delta {0} {1} = {2} ({3})".format(result.time, result.localtime, ldelta, ldelta.days)
            if ldelta.days < 1:
                if ldelta.days < 0:
                    thisrow["local_state"] = "error"
                elif ldelta.seconds < 60:
                    thisrow["local_state"] = "success"
                elif ldelta.seconds < 60*30:
                    thisrow["local_state"] = "warning"

                    


        

        servertable.append(thisrow)
        
    outDict["servertable"] = servertable
    outDict["serverlist"] = []
    outDict["serverlist"] = generate_netmap()

    return outDict
