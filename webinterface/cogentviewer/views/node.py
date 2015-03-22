"""
==============
Display Details of a node
==============

@author: dan Goldsmith
@version: 0.3
@since: March 2013
"""

from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import view_config

#Allow errors to raise a 404
import pyramid.httpexceptions as httpexp

import logging
log = logging.getLogger(__name__)

import homepage

from ..models import meta
from ..models.meta import DBSession
import cogentviewer.models as models

import os.path

@view_config(route_name='node', renderer='cogentviewer:templates/node.mak',permission="view")
def node(request):
    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)
    theUser = homepage.getUser(request)
    outDict["user"] = theUser.username

    outDict["nodeDropdowns"] = homepage.getNodeDropdowns()
    outDict["pgTitle"] = "Node Data"
    #outDict["deployments"] =deps

    
    nid = request.matchdict.get("id",None)
    outDict["nid"] = nid

    #So we want to get the sensors attachd to this node.
    theNode = DBSession.query(models.Node).filter_by(id=nid).first()
    if theNode is None: #So if we have a node that doesnt exist
        raise httpexp.HTTPNotFound

    #Next we want the nodes location information
    theLocation = theNode.location
    locDetails = "No Current Location"
    if theLocation is not None:
        #Update
        locDetails = "{0} ({1})".format(theLocation.house.address,theLocation.room.name)

    
    outDict["locDetails"] = locDetails
    
    #Fetch the last transmission
    lastNodeState = DBSession.query(models.NodeState).filter_by(nodeId = nid).order_by(models.NodeState.time.desc()).first()
    
    outDict["lastState"] = lastNodeState.time

    #And the latest sensor readings
    allReadings = DBSession.query(models.Reading).filter_by(nodeId=nid,time=lastNodeState.time)

    #Length of time our graphs are up for

#    buttonList = ["<a href='?duration=week' class='btn'>Last Week</a>",
#                  "<a href='?duration=day' class='btn'>Last Day</a>",
#                  "<a href='?duration=hour' class='btn'>Last Hour</a>"]
    buttonList = [["year", "Last Year", "btn"],
                  ["month", "Last Month", "btn"],
                  ["week", "Last Week", 'btn'],
                  ["day", "Last Day", 'btn'],
                  ["hour", "Last Hour", 'btn'],
                  ]

    getLength = request.GET.get("duration",None)
    if getLength == "year":
        buttonList[0][2] = "btn btn-primary"
        glength = "-1y"
    elif getLength == "month":
        buttonList[1][2] = "btn btn-primary"
        glength = "-1m"
    elif getLength == "week":
        buttonList[2][2] = "btn btn-primary"
        glength = "-1w"
    elif getLength == "day":
        buttonList[3][2] = "btn btn-primary"
        glength = "-1d"
    else:
        buttonList[4][2] = "btn btn-primary"
        glength = "-1h"
    
    outDict["btnList"] = buttonList

    outReadings = []
    sensorIds = []
    #Have an empyty battery Level
    outDict["batLevel"] = None
    for item in allReadings:
        log.debug("Graph for type {0}".format(item.typeId))
        sensorIds.append(item.typeId)
        if item.typeId == 6:
            outDict["batLevel"] = item.value

            sType = item.sensorType.name
            sUnits = item.sensorType.units

            theURL = None
            outReadings.append([sType, item.value,theURL])

    outDict["allReadings"] = outReadings


        
    
    
    
    
        
    

    

    

    return outDict
