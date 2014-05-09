"""
==============
Display the Homepage
==============

@author: dan Goldsmith
@version: 0.3
@since: March 2013
"""

import logging
log = logging.getLogger(__name__)

import datetime
import time 

import sqlalchemy
from sqlalchemy import func

from dateutil import tz

import pyramid.url
from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import notfound_view_config
from pyramid.view import view_config
from pyramid.view import forbidden_view_config
from pyramid.security import authenticated_userid
from pyramid.security import forget
from pyramid.httpexceptions import HTTPFound

#import cogentviewer.models.meta as meta

from ..models import meta
import cogentviewer.models as models
#import .models import as models
#from ..models import *

#Try getting version number
import pkg_resources
version = pkg_resources.require("cogent-viewer")[0].version


NAVBAR = [("Home","home","Homepage"),
            ("Time Series","timeseries","Show Time Series Data"),
            ("Exposure","exposure","Show Exposure Graphs"),
            ("Export","export","Export Data"),
            #("Report","report","Generate Reports"),
            #("Electricity","electricity","Electricity Use"),
            #("Status","status","Deployment Status"),
            #("Admin","admin","Admin"),
            #("Browser","databrowser","Examine Data"),
            #("Upload","upload","Upload Data"),
            ("Server","server","Show Server Status"),
            ("housestatus","housestatus","Show House Status"),
            ]

ADMIN_NAVBAR = [("Admin","admin","Admin"),
                ("PushStatus","pushdebug","PushStatus"),
                
               ]

def genHeadUrls(request, user=None):
    """Generate the Urls for the Homepage"""
    headLinks = []

    #log.debug("User {0}".format(request.root))
    for item in NAVBAR:
        headLinks.append([item[0],pyramid.url.route_url(item[1],request),item[2]])  

    if user:
        if user.level == "root":
            for item in ADMIN_NAVBAR:
                headLinks.append([item[0],pyramid.url.route_url(item[1],request),item[2]])  
    return headLinks
    
def genSideUrls(request):
    """Generate the Urls for the Sidebar"""
    sideLinks = []
    for item in NAVBAR:
        sideLinks.append([item[0],pyramid.url.route_url(item[1],request),item[2]])  

    return sideLinks

def getUser(request):
    """Helper Function to get the user when authenticated"""
    userId = authenticated_userid(request)
    #if userId is None:
    #    return

    session = meta.Session()
    thisUser = session.query(models.User).filter_by(id=userId).first()
    #log.debug("User from homepage.getUser {0}".format(thisUser))
    if thisUser is None:
        headers = forget(request)
        return HTTPFound(location=request.route_url("home"),
                         headers=headers)
    return thisUser


def _procNodeQuery(theQry):
    session = meta.Session()

    #What sensor is the node Battery Level
    battsensor = session.query(models.SensorType).filter_by(name="Battery Voltage").first()

    #Sort the Table
    outItems = []
    currentTime = datetime.datetime.utcnow()

    #Work out Timezones
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    for item,maxtime in theQry:        
        #Flag According to time
        #log.debug("Deal with node {0}".format(item.nodeId))
        state= "success"
        #td = (currentTime - maxtime).total_seconds()  #Py 2.7 only
        tdelt = currentTime - maxtime
        td = (tdelt.microseconds + (tdelt.seconds + tdelt.days * 24 * 3600) * 10**6) / 10**6
        if td > 60*60*2: # One Day
            state="error"
        elif td > 60*60: #One Hour
            state="warning"
        elif td > 60*10: #Ten Mins
            state = "info"
        
        #Adjust the time so it fits to local TZ
        localtime = maxtime.replace(tzinfo=from_zone) #As default Tz is Naive
        localtime = localtime.astimezone(to_zone)

        localprint = localtime.strftime("%c")

        #Get the Readings associated with this sensor
        readingQry = session.query(models.Reading).filter_by(nodeId=item.nodeId,
                                                             time=maxtime,
                                                             typeId=battsensor.id).first()
        #log.debug("-->Battery Reading {0}".format(readingQry))
        if readingQry is None:
            #log.debug("--> No Battery")
            battLevel = "No Battery"
            battVolts = 0.0
        else:
            battLevel = "text-success"
            battVolts = readingQry.value
            if readingQry.value < 2.6:
                battLevel = "text-errort"
            elif readingQry.value < 2.8:
                battLevel = "text-warning"
        
        #And get the node Details
        thisNode = session.query(models.Node).filter_by(id=item.nodeId).first()
        if thisNode is None:
            continue
        locDetails = None
        if thisNode.location is not None:
            theLocation = thisNode.location
            log.debug("--> Location is {0}".format(theLocation))
            locDetails = "{0} ({1})".format(theLocation.house.address,theLocation.room.name)

        #outItems.append(item)
        outItems.append([state,
                         item.nodeId,
                         localprint,
                         battLevel,
                         #readingQry.value,
                         battVolts,
                         locDetails])
    return outItems

@view_config(route_name='home', renderer='cogentviewer:templates/home.mak',permission="view")
def homepage(request):
    """
    View to show the Homepage Currently just lists all known deployments
    """

    #session = meta.Session)
    #deployments = session.query(models.deployment.Deployment).all()

    outDict = {}

    #Get authenticated user
    user = getUser(request)
    if type(user) == HTTPFound:
        return user
    else:
        outDict["user"] = user.username

    outDict["showadmin"] = user.level == "root"
    outDict["headLinks"] = genHeadUrls(request, user)
    outDict["sideLinks"] = genSideUrls(request)
    outDict["pgTitle"] = "Homepage"





    now = datetime.datetime.utcnow()

    session = meta.Session()
    activeHouses = session.query(models.House).order_by(models.House.startDate.desc())
    activeHouses = activeHouses.filter(sqlalchemy.or_(models.House.endDate >= now,models.House.endDate==None))
    houseUrls = [[x,request.route_url("house",id=x.id)] for x in activeHouses]
       
    outDict["activeHouses"] = houseUrls
    outDict["newLink"] = request.route_url("house",id="")


    # #I Want A List of all recently heard nodes (Last Day)
    # #7 Hours is Rosses
    # t1 = time.time()
    # #Distinct is a bit of a bugger but we can use group by as a cheat
    # theQry = session.query(models.NodeState, func.max(models.NodeState.time)).group_by(models.NodeState.nodeId)
    # theQry = theQry.filter(models.NodeState.time > datetime.datetime.utcnow() - datetime.timedelta(hours=8))
    # theQry = theQry.order_by(func.max(models.NodeState.time).desc())
    
    # outDict["nodeStates"] = _procNodeQuery(theQry)
    # t2 = time.time()
    # log.info("------> Time Taken to fetch recent node states {0}".format(t2-t1))
    # #Lets try to get the registered nodes that havent reported in a time
    # #Houses that are required
    # now = datetime.datetime.utcnow()


    # t1 = time.time()
    # theQry = session.query(models.House).filter(sqlalchemy.or_(models.House.endDate == None,
    #                                                            models.House.endDate > now))

    # missingNodes = []
    # for item in theQry:
    #     for loc in item.locations:
    #         missingNodes.extend(x.id for x in loc.nodes)

    # if missingNodes:
    #     theQry = session.query(models.NodeState, func.max(models.NodeState.time)).group_by(models.NodeState.nodeId)
    #     theQry = theQry.filter(models.NodeState.nodeId.in_(missingNodes))
    #     theQry = theQry.having(func.max(models.NodeState.time) <= datetime.datetime.utcnow() - datetime.timedelta(hours=8))
    #     theQry = theQry.order_by(func.max(models.NodeState.time).desc())

    #     outDict["missingNodes"] = _procNodeQuery(theQry)
    # else:
    #     outDict["missingNodes"] = []
    # t2 = time.time()
    # log.info("------> Time Taken to fetch missing node states {0}".format(t2-t1))

    return outDict


def getNodeDropdowns():
    """This should return a strucutred list of nodes etc"""

    session = meta.Session()

    #Get Deployments we know about
    outDict = {}    

    deployments = session.query(models.deployment.Deployment).all()
    for item in deployments:
        outDict[item.name] = item
    return outDict
        
    
    
def chartTest(request):
    outDict = {}

    outDict["pgTitle"] = "Test of Charting"
    outDict["headLinks"] = genHeadUrls(request)
    outDict["sideLinks"] = genSideUrls(request)

    return render_to_response('cogentviewer:templates/chartTest.mak',
                              outDict,
                              request=request)

#Add a 404
@notfound_view_config(renderer="cogentviewer:templates/404.mak")
def notfound(request):
    return {}


@forbidden_view_config(renderer="cogentviewer:templates/forbidden.mak")
def forbiddenview(request):
    return {}
