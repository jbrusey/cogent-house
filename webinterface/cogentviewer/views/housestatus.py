"""
Display server status
"""

import logging

import datetime

import sqlalchemy

from pyramid.view import view_config


from cogentviewer.models import meta
from ..models.meta import DBSession
import cogentviewer.models as models
import cogentviewer.views.homepage as homepage
import cogentviewer.views.yields as yields

import json

STATE_OK = 0
STATE_INFO = 1
STATE_WARNING = 2
STATE_ERROR = 3

def togglestate(current, new):
    """Toggle a state message based on a sequence
    Only changing if the state is escelated
    """

    if new > current:
        return new
    return current


def statetotext(state):
    """Turn a state constant into text"""
    if state == STATE_OK:
        return "success"
    elif state == STATE_INFO:
        return "info"
    elif state == STATE_WARNING:
        return "warning"
    elif state == STATE_ERROR:
        return "error"
    return None



@view_config(route_name='housestatus',
             renderer='cogentviewer:templates/housestatus.mak',
             permission="view")
def housestatus(request):
    """Overall status screen for all houses in the deployment"""
    log = logging.getLogger(__name__)
    outdict = {}
    outdict["headLinks"] = homepage.genHeadUrls(request)
    outdict["sideLinks"] = homepage.genSideUrls(request)
    theUser = homepage.getUser(request)
    outdict["user"] = theUser.username

    outdict["nodeDropdowns"] = homepage.getNodeDropdowns()
    outdict["pgTitle"] = "House Status"

    #So we want a list of active houses

    now = datetime.datetime.utcnow()

    qry = DBSession.query(models.House)
    qry = qry.filter(sqlalchemy.or_(models.House.endDate >= now,
                                    models.House.endDate == None))

    activehouses = []
    for item in qry:
        log.debug("{0} House {1} {0}".format("+"*30, item.address))
        itemdict = {"id":item.id,
                    "address":item.address}

        rowstate = STATE_OK

        #Check for a server linked to this house
        itemdict["lastpush"] = "NA"

        if item.server:
            itemdict["hostname"] = item.server.hostname
            #Fetch the last push
            pushqry = DBSession.query(models.PushStatus)
            pushqry = pushqry.filter_by(hostname=item.server.hostname)
            pushqry = pushqry.order_by(models.PushStatus.time)
            lastpush = pushqry.first()
            if lastpush:
                itemdict["lastpush"] = lastpush.time
        else:
            itemdict["hostname"] = None



        #Number of Nodes
        locations = item.locations
        locationIds = [x.id for x in locations]
        log.debug("Locations {0}".format(locations))
        log.debug("Location Ids {0}".format(locationIds))

        nodeqry = DBSession.query(models.Node)
        nodeqry = nodeqry.filter(models.Node.locationId.in_(locationIds))
        nodes = nodeqry.all()
        log.debug("Nodes {0}".format(nodes))
        nodeids = [x.id for x in nodes]
        log.debug("Node Ids {0}".format(nodeids))
        itemdict["numnodes"] = len(nodeids)

        if len(nodeids) < 3:
            rowstate = togglestate(rowstate, STATE_WARNING)
        elif len(nodeids) > 5:
            rowstate = togglestate(rowstate, STATE_WARNING)

        #Work out which ones are active in the last 8 hours
        hbtime = now - datetime.timedelta(hours=8)
        stateqry = DBSession.query(models.NodeState)
        stateqry = stateqry.filter(models.NodeState.nodeId.in_(nodeids))
        stateqry = stateqry.filter(models.NodeState.time >= hbtime)
        stateqry = stateqry.group_by(models.NodeState.nodeId)
        #log.debug(stateqry)
        itemdict["activenodes"] = stateqry.count()


        hbtime = now - datetime.timedelta(days=7)
        stateqry = DBSession.query(models.NodeState,
                                 sqlalchemy.func.max(models.NodeState.time))
        stateqry = stateqry.filter(models.NodeState.nodeId.in_(nodeids))
        stateqry = stateqry.filter(models.NodeState.time >= hbtime)
        stateqry = stateqry.group_by(models.NodeState.nodeId)
        #log.debug(stateqry)
        #log.debug(stateqry.all())
        itemdict["weeknodes"] = stateqry.count()

        if itemdict["weeknodes"] > itemdict["activenodes"]:
            rowstate = togglestate(rowstate, STATE_INFO)


        #Most Recent Sample
        if stateqry.count() > 0:
            maxtime = max([x[1] for x in stateqry])
            log.debug(maxtime)

            if (now-maxtime).days >= 1:
                pass
                #rowstate = togglestate(rowstate, STATE_WARNING)
        else:
            log.debug("No Recent Readings")
            #rowstate = togglestate(rowstate,STATE_ERROR)
            maxtime = None
        itemdict["lastreading"] = maxtime


        ##Calculate Yields
        yieldtime = now - datetime.timedelta(days=7)
        nodeyields = []
        for nid in nodeids:
            log.debug("Calcualte Yield for {0} From {1}".format(nid, yieldtime))
            values = yields.calcyieldNew(nid, yieldtime)
            log.debug(values)
            nodeyields.append(values[1])

        if len(nodeyields) > 0:
            itemdict["avgyield"] = sum(nodeyields) / float(len(nodeyields))
            itemdict["minyield"] = min(nodeyields)
            #if itemdict["avgyield"] <= 70:
            #    rowstate = togglestate(rowstate, STATE_ERROR)
            #elif itemdict["avgyield"] <= 90:
            #    rowstate = togglestate(rowstate, STATE_INFO)
        else:
            itemdict["avgyield"] = 0.0
            itemdict["minyield"] = 0.0
            #rowstate = togglestate(rowstate, STATE_ERROR)

        itemdict["rowstate"] = statetotext(rowstate)
        activehouses.append(itemdict)

    # yieldtime = now - datetime.timedelta(days=7)
    # nodeyields = []
    # for nid in [327,]:
    #     log.debug("Calcualte Yield for {0} From {1}".format(nid, yieldtime))
    #     values = yields.calcyield(nid, yieldtime)
    #     log.debug(values)
    #     nodeyields.append(values[1])


    outdict["activehouses"] = activehouses

    return outdict



@view_config(route_name='housedetail',
             renderer='cogentviewer:templates/housedetail.mak',
             permission="view")
def housedetails(request):
    """Status screen for an individual house"""
    log = logging.getLogger(__name__)
    outdict = {}
    outdict["headLinks"] = homepage.genHeadUrls(request)
    outdict["sideLinks"] = homepage.genSideUrls(request)
    theUser = homepage.getUser(request)
    outdict["user"] = theUser.username

    outdict["nodeDropdowns"] = homepage.getNodeDropdowns()

    #Empty Dictionary
    outdict["pgTitle"] = "House Status"
    outdict["thehouse"] = "No Such House"
    outdict["servername"] = None
    outdict["lastpush"] = None
    outdict["skew"] = None

    theId = request.matchdict.get("id", None)
    log.debug("----- Status for House Id {0} -----".format(theId))


    qry = DBSession.query(models.House).filter_by(id=theId)
    thishouse = qry.first()
    if thishouse:
        outdict["pgTitle"] = "Status of House {0}".format(thishouse.address)
        outdict["thehouse"] = thishouse
    else:
        outdict["thehouse"] = models.House(address="No Such House")
        return outdict

    #So First find the server that is associated
    #qry = DBSession.query(models.Server).filter_by(houseid = theId)
    theserver = thishouse.server
    if theserver:
        outdict["servername"] = theserver.hostname
        #And Last Push
        qry = DBSession.query(models.PushStatus)
        qry = qry.filter_by(hostname=theserver.hostname)
        qry = qry.order_by(models.PushStatus.time)
        lastpush = qry.first()
        if lastpush:
            outdict["lastpush"] = lastpush.time
            outdict["skew"] = lastpush.time - lastpush.localtime

    else:
        outdict["server"] = None
        outdict["lastpush"] = None
        outdict["skew"] = None

    #Details for individual Nodes

    #locationIds = [x.id for x in thishouse.locations]
    #log.debug("Locations for House {0}".format(locationIds))
    nodedetails = []
    checkednodes = []
    nodepairs = [] #Pair of node / locations
    now = datetime.datetime.utcnow()
    yieldtime = now - datetime.timedelta(days=7)

    for location in thishouse.locations:
        log.debug("--> Getting Details for Location {0}".format(location))
        nodeqry = DBSession.query(models.Node).filter_by(locationId=location.id)
        for node in nodeqry:
            log.debug("--> --> Getting Details for Node {0}".format(node))
            itemdict = {"id": node.id,
                        "location": "{0} ({1})".format(location.room.name,
                                                       location.id),
                        "lastreading":None,
                        "laststate":None,
                        "yield":None,
                        "compression":None,
                        "resets":None,
                        "voltage":0.0,
                        }
            #Work out the last reading
            qry = DBSession.query(models.Reading)
            qry = qry.filter_by(nodeId=node.id,
                                locationId=location.id,
                                typeId=6)
            qry = qry.order_by(models.Reading.time.desc())
            lastreading = qry.first()
            if lastreading is None:
                qry = DBSession.query(models.Reading)
                qry = qry.filter_by(nodeId=node.id,
                                    locationId=location.id,
                                    typeId=0)
                qry = qry.order_by(models.Reading.time.desc())
                lastreading = qry.first()

                if lastreading:
                    itemdict["lastreading"] = lastreading.time
            else:
                itemdict["lastreading"] = lastreading.time
                log.debug("VOLTAGE:".format(lastreading.value))
                itemdict["voltage"] = lastreading.value

            #Last Nodestate
            qry = DBSession.query(models.NodeState).filter_by(nodeId=node.id)
            qry = qry.order_by(models.NodeState.time.desc())
            laststate = qry.first()
            if laststate:
                itemdict["laststate"] = laststate.time

            #Finally Yield
            values = yields.calcyieldNew(node.id, yieldtime)
            itemdict["yield"] = values[1]
            itemdict["compression"] = values[2]
            itemdict["resets"] = values[3]


            checkednodes.append(node.id)
            nodedetails.append(itemdict)
            nodepairs.append([node.id, location.id])

    outdict["nodecount"] = len(checkednodes)
    outdict["nodedetails"] = nodedetails
    outdict["nodepairs"] = json.dumps(nodepairs)

    return outdict
