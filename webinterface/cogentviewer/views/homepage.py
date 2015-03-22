"""
==============
Display the Homepage
==============

@author: dan Goldsmith
@version: 0.3
@since: March 2013
"""

import logging
LOG = logging.getLogger(__name__)

import datetime

import sqlalchemy

from dateutil import tz

import pyramid.url
from pyramid.renderers import render_to_response
from pyramid.view import notfound_view_config
from pyramid.view import view_config
from pyramid.view import forbidden_view_config
from pyramid.security import authenticated_userid
from pyramid.security import forget
from pyramid.httpexceptions import HTTPFound


from ..models.meta import DBSession
import cogentviewer.models as models

#Try getting version number
import pkg_resources
VERSION = pkg_resources.require("cogent-viewer")[0].version


NAVBAR = [("Home", "home", "Homepage"),
            ("Time Series", "timeseries", "Show Time Series Data"),
            ("Exposure", "exposure", "Show Exposure Graphs"),
            ("Export", "export", "Export Data"),
            ("Server", "server", "Show Server Status"),
            ("housestatus", "housestatus", "Show House Status"),
            ]

ADMIN_NAVBAR = [("Admin", "admin", "Admin"),
                ("PushStatus", "pushdebug", "PushStatus"),

               ]

def genHeadUrls(request, user=None):
    """Generate the urls for the homepage"""
    head_links = []

    for item in NAVBAR:
        head_links.append([item[0],
                          pyramid.url.route_url(item[1], request),
                          item[2]])

    if user:
        if user.level == "root":
            for item in ADMIN_NAVBAR:
                head_links.append([item[0],
                                   pyramid.url.route_url(item[1], request),
                                   item[2]])
    return head_links

def genSideUrls(request):
    """Generate the urls for the sidebar"""
    sideLinks = []
    for item in NAVBAR:
        sideLinks.append([item[0],
                          pyramid.url.route_url(item[1], request),
                          item[2]])

    return sideLinks

def getUser(request):
    """Helper function to get the user when authenticated"""
    userId = authenticated_userid(request)
    #if userId is None:
    #    return

    thisUser = DBSession.query(models.User).filter_by(id=userId).first()
    if thisUser is None:
        headers = forget(request)
        return HTTPFound(location=request.route_url("home"),
                         headers=headers)
    return thisUser


def _procNodeQuery(theQry):
    #What sensor is the node battery Level
    # TODO missing test case
    battsensor = (DBSession.query(models.SensorType)
                  .filter_by(name="Battery Voltage")
                  .first())

    #Sort the Table
    outItems = []
    currentTime = datetime.datetime.utcnow()

    #Work out timezones
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    for item, maxtime in theQry:
        # Flag according to time
        state = "success"
        tdelt = currentTime - maxtime
        td = ((tdelt.microseconds +
               (tdelt.seconds + tdelt.days * 24 * 3600) * 10**6)
              / 10**6)
        if td > 60*60*2: # One day
            state = "error"
        elif td > 60*60: #One hour
            state = "warning"
        elif td > 60*10: #Ten mins
            state = "info"

        # Adjust the time so it fits to local TZ
        localtime = maxtime.replace(tzinfo=from_zone)
        # default Tz is naive
        localtime = localtime.astimezone(to_zone)

        localprint = localtime.strftime("%c")

        #Get the readings associated with this sensor
        readingQry = (DBSession.query(models.Reading)
                      .filter_by(nodeId=item.nodeId,
                                 time=maxtime,
                                 typeId=battsensor.id)
                      .first())
        if readingQry is None:
            battLevel = "No Battery"
            battVolts = 0.0
        else:
            battLevel = "text-success"
            battVolts = readingQry.value
            if readingQry.value < 2.6:
                battLevel = "text-errort"
            elif readingQry.value < 2.8:
                battLevel = "text-warning"

        #And get the node details
        thisNode = (DBSession.query(models.Node)
                    .filter_by(id=item.nodeId)
                    .first())
        if thisNode is None:
            continue
        locDetails = None
        if thisNode.location is not None:
            theLocation = thisNode.location
            LOG.debug("--> Location is {0}".format(theLocation))
            locDetails = ("{0} ({1})"
                          .format(theLocation.house.address,
                                  theLocation.room.name))

        outItems.append([state,
                         item.nodeId,
                         localprint,
                         battLevel,
                         battVolts,
                         locDetails])
    return outItems


@view_config(route_name='home',
             renderer='cogentviewer:templates/home.mak',
             permission="view")
def homepage(request):
    """
    View to show the homepage.
    Currently just lists all known deployments
    """

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

    activeHouses = (DBSession.query(models.House)
                    .order_by(models.House.startDate.desc())
                    .filter(sqlalchemy.or_(models.House.endDate >= now,
                                           models.House.endDate == None)))

    houseUrls = [[x, request.route_url("house", id=x.id)]
                 for x in activeHouses]

    outDict["activeHouses"] = houseUrls
    outDict["newLink"] = request.route_url("house", id="")
    return outDict


def getNodeDropdowns():
    """This should return a structured list of nodes etc"""

    # Get deployments we know about
    out_dict = {}

    deployments = DBSession.query(models.deployment.Deployment).all()
    for item in deployments:
        out_dict[item.name] = item
    return out_dict


def chartTest(request):
    # TODO missing test case
    out_dict = {}

    out_dict["pgTitle"] = "Test of Charting"
    out_dict["headLinks"] = genHeadUrls(request)
    out_dict["sideLinks"] = genSideUrls(request)

    return render_to_response('cogentviewer:templates/chartTest.mak',
                              out_dict,
                              request=request)

#Add a 404
@notfound_view_config(renderer="cogentviewer:templates/404.mak")
def notfound(request):
    return {}


@forbidden_view_config(renderer="cogentviewer:templates/forbidden.mak")
def forbiddenview(request):
    return {}
