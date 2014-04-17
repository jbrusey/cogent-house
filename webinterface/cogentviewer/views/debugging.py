import logging
log = logging.getLogger(__name__)

import datetime
import subprocess
import urllib

import sqlalchemy

from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import view_config

import homepage
from ..models import meta
import cogentviewer.models as models


@view_config(route_name='pushdebug',
             renderer='cogentviewer:templates/pushstatus.mak',permission="admin")
def pushstatus(request):
    log = logging.getLogger(__name__)
    outdict = {}

    user = homepage.getUser(request)
    outdict["user"] = user.username
    outdict["headLinks"] = homepage.genHeadUrls(request, user)
    outdict["pgTitle"] = "Push Status"
    
    #Get the list of servers
    session = meta.Session()
    qry = session.query(models.PushStatus,
                        sqlalchemy.func.min(models.PushStatus.time),                       
                        sqlalchemy.func.max(models.PushStatus.time),
                        sqlalchemy.func.count(models.PushStatus.time),
                        )
    qry = qry.group_by(models.PushStatus.hostname)
    hostlist = qry.all()
    serverlist = []
    for item in hostlist:
        print item
        qry = session.query(models.PushStatus)

        qry = qry.filter_by(hostname = item[0].hostname)
        qry = qry.order_by(models.PushStatus.time.desc())
        lastpush = qry.first()
        qry = session.query(models.Server)
        qry = qry.filter_by(hostname=item[0].hostname)
        theserver = qry.first()

        skew = lastpush.time - lastpush.localtime
        
        serverdict = {"hostname":lastpush.hostname,
                      "firstpush":item[1],
                      "lastpush":item[2],
                      "numsamps":item[3],
                      "skew":skew,
                      "houses" : " ".join([x.address for x in theserver.houses]),
                      "rowcolor" : "success",
                      }



        if skew.days > 0:
            serverdict["rowcolor"] = "error"
        elif skew.seconds > 60*5:
            serverdict["rowcolor"] = "warning"
        
        now = datetime.datetime.now()
        now = datetime.datetime(2014,02,14,15,20,00)
        
        pushdelta = now - lastpush.time
        if pushdelta.days > 0:
            serverdict["rowcolor"] = "error"
        elif pushdelta.hours > 6:
            serverdict["rowcolor"] = "warning"


        serverlist.append(serverdict)
            
    outdict["serverlist"] = serverlist
    return outdict
    

@view_config(route_name='housedebug',
             renderer='cogentviewer:templates/housedebug.mak',permission="view")
def housedebugging(request):
    log = logging.getLogger(__name__)
    outdict = {}
    outdict["headLinks"] = homepage.genHeadUrls(request)
    outdict["sideLinks"] = homepage.genSideUrls(request)
    theUser = homepage.getUser(request)
    outdict["user"] = theUser.username

    outdict["nodeDropdowns"] = homepage.getNodeDropdowns()
    outdict["pgTitle"] = "House Status"

    #So we want a list of active houses
    session = meta.Session()

    theid = request.matchdict.get("id")
    if theid == "":
        theid = 1
    else:
        theid = int(theid)
    log.debug("Given Id >{0}< {1}".format(theid,type(theid)))
    #House
    thehouse = session.query(models.House).filter_by(id=theid).first()
    log.debug("House is {0}".format(thehouse))
    outdict["house"] = thehouse.address
      
    #Get Locations associated with this house
    locs = [[x.id,x.room.name] for x in thehouse.locations]
    outdict["locs"] = locs


    regnodes = []
    allnodes = []

    for loc in thehouse.locations:
        outlist = {"location": loc.id,
                   "room" : loc.room.name}
        nodelist = [x.id for x in loc.nodes]
        allnodes.extend(nodelist)
        outlist["registered"] = ",".join([str(x) for x in nodelist])
        qry = session.query(models.Reading).filter_by(locationId = loc.id)
        qry = qry.group_by(models.Reading.nodeId)
        outlist["data"] =  ",".join(str(x.nodeId) for x in qry)
        regnodes.append(outlist)

    outdict["regnodes"] = regnodes
            
    #Nodes that have data but are not registered to this house
    locids = [x.id for x in thehouse.locations]
    qry = session.query(models.Reading).filter(models.Reading.locationId.in_(locids))
    qry = qry.group_by(models.Reading.nodeId)
    datanodes = qry.all()
    unreg = []
    for item in datanodes:
        qry = session.query(models.Node).filter_by(id = item.nodeId)
        thisnode = qry.first()
        if thisnode.locationId != item.locationId:
            unreg.append([thisnode.id, 
                          "({0}) {1} {2}".format(thisnode.location.id,
                                                 thisnode.location.house.address,
                                                 thisnode.location.room.name)])

    outdict["unreg"] = unreg 

    #Finally, where are nodes that are linked here reporting data to
    reglocs = []
    for item in allnodes:
        thisitem = {"nid": item,
                    "currentloc":None,
                    "dataloc":None}
        qry = session.query(models.Node).filter_by(id = item)
        node = qry.first()
        thisitem["currentloc"] = "({0}) {1} {2}".format(node.location.id,
                                                        node.location.house.address,
                                                        node.location.room.name)

        #And work out where this node should be reporting to
        datalocs = []
        qry = session.query(models.Reading).filter_by(nodeId = item)
        qry = qry.group_by(models.Reading.locationId)
        for d_item in qry:
            datalocs.append("({0}) {1} {2}".format(d_item.location.id,
                                                   d_item.location.house.address,
                                                   d_item.location.room.name))
        
        thisitem["dataloc"] = datalocs
        reglocs.append(thisitem)
    outdict["reglocs"] = reglocs

    return outdict

@view_config(route_name='heatmap',
             renderer='cogentviewer:templates/heatmap.mak',permission="admin")
def heatmap(request):
    return {}


@view_config(route_name='netmap',
             renderer='cogentviewer:templates/netmap.mak',permission="view")
def netmap(request):
    return {"time":datetime.datetime.now()}


