"""
Deal with Exposure Data
"""

from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import view_config


import logging
log = logging.getLogger(__name__)

import homepage

@view_config(route_name='exposure', renderer='cogentviewer:templates/exposure.mak',permission="view")
def exposure(request):
    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)
    theUser = homepage.getUser(request)
    outDict["user"] = theUser.username


    outDict["pgTitle"] = "Exposure Data"
    #outDict["deployments"] =deps

    outDict["nodeDropdowns"] = homepage.getNodeDropdowns()

    return outDict
