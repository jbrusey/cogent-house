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

import sqlalchemy

import pyramid.url
from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import notfound_view_config
from pyramid.view import view_config
from pyramid.security import authenticated_userid

#import cogentviewer.models.meta as meta

from ..models import meta
import cogentviewer.models as models
#import .models import as models
#from ..models import *

SIDEBARS = [("Time Series","timeseries","Show Time Series Data"),
            ("Exposure","exposure","Show Exposure Graphs"),
            ("Electricity","electricity","Electricity Use"),
            #("Status","status","Deployment Status"),
            ("Admin","admin","Admin"),
            ("Browser","databrowser","Examine Data"),
            #("Upload","upload","Upload Data"),
            ]
#SIDEBARS = [("Home","home","Homepage")]
# SIDEBARS = [
#     ("Temperature", "allGraphs?typ=0", "Show temperature graphs for all nodes"),
#     ("Humidity", "allGraphs?typ=2", "Show humidity graphs for all nodes"),
#     ("CO<sub>2</sub>", "allGraphs?typ=8", "Show CO2 graphs for all nodes"),
#     ("AQ", "allGraphs?typ=9", "Show air quality graphs for all nodes"),
#     ("VOC", "allGraphs?typ=10", "Show volatile organic compound (VOC) graphs for all nodes"),
#     ("Electricity", "allGraphs?typ=11", "Show electricity usage for all nodes"),
#     ("Battery", "allGraphs?typ=6", "Show node battery voltage"),
#     ("Duty cycle", "allGraphs?typ=13", "Show transmission delay graphs"),
#     ("Bathroom v. Elec.", "bathElec", "Show bathroom versus electricity"),

#     ("Network tree", "treePage", "Show a network tree diagram"),
#     ("Missing and extra nodes", "missing", "Show unregistered nodes and missing nodes"),
#     ("Packet yield", "yield24", "Show network performance"),
#     ("Low batteries", "lowbat", "Report any low batteries"),
#     ("View log", "viewLog", "View a detailed log"),
#     ("Export data", "exportDataForm", "Export data to CSV"),

#      ]

def genHeadUrls(request):
    """Generate the Urls for the Homepage"""
    #headLinks = [("Home",pyramid.url.route_url("home",request))]
    headLinks = [("Home",request.route_url("home"))]

    for item in SIDEBARS:
        headLinks.append([item[0],pyramid.url.route_url(item[1],request),item[2]])  

    return headLinks
    
def genSideUrls(request):
    """Generate the Urls for the Sidebar"""
    sideLinks = []
    for item in SIDEBARS:
        sideLinks.append([item[0],pyramid.url.route_url(item[1],request),item[2]])  

    return sideLinks

def getUser(request):
    """Helper Function to get the user when authenticated"""
    userId = authenticated_userid(request)
    session = meta.Session()
    thisUser = session.query(models.User).filter_by(id=userId).first()
    log.debug("User from homepage.getUser {0}".format(thisUser))
    return thisUser

@view_config(route_name='home', renderer='home.mak',permission="view")
def homepage(request):
    """
    View to show the Homepage Currently just lists all known deployments
    """

    #session = meta.Session)
    #deployments = session.query(models.deployment.Deployment).all()

    outDict = {}
    outDict["headLinks"] = genHeadUrls(request)
    outDict["sideLinks"] = genSideUrls(request)
    outDict["pgTitle"] = "Homepage"

    #Get authenticated user
    theUser = getUser(request)
    outDict["user"] = theUser.username

    now = datetime.datetime.now()

    session = meta.Session()
    activeHouses = session.query(models.House).order_by(models.House.endDate.desc())
    #activeHouses = activeHouses.filter(sqlalchemy.or_(models.House.endDate >= now,models.House.endDate==None))
    houseUrls = [[x,request.route_url("house",id=x.id)] for x in activeHouses]
       
    outDict["activeHouses"] = houseUrls
    outDict["newLink"] = request.route_url("house",id="")

    return outDict
    return render_to_response('cogentviewer:templates/home.mak',
                              outDict,
                              request=request)


def getNodeDropdowns():
    """This should return a strucutred list of nodes etc"""

    session = meta.Session()

    #Get Deployments we know about
    outDict = {}    


    deployments = session.query(models.deployment.Deployment).all()
    for item in deployments:
        outDict[item.name] = item

    import pprint
    pprint.pprint(outDict)
    
    
def chartTest(request):
    outDict = {}

    outDict["pgTitle"] = "Test of Charting"
    outDict["headLinks"] = genHeadUrls(request)
    outDict["sideLinks"] = genSideUrls(request)

    return render_to_response('cogentviewer:templates/chartTest.mak',
                              outDict,
                              request=request)

#Add a 404
@notfound_view_config(renderer="404.mak")
def notfound(request):
    return {}
