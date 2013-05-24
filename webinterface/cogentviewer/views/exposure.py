"""
Deal with Exposure Data
"""

from pyramid.response import Response
from pyramid.renderers import render_to_response
import pyramid.url

import logging
log = logging.getLogger(__name__)

import homepage

def exposure(request):
    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)

    outDict["pgTitle"] = "Exposure Data"
    #outDict["deployments"] =deps

    outDict["nodeDropdowns"] = homepage.getNodeDropdowns()

    return render_to_response('cogentviewer:templates/exposure.mak',
                              outDict,
                              request=request)
