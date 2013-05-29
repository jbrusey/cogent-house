"""
Deal with Time Series Data
"""

from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import view_config

#import pyramid.url

import logging
log = logging.getLogger(__name__)

import homepage

@view_config(route_name='timeseries', renderer='cogentviewer:templates/timeseries.mak',permission="view")
def timeseries(request):
    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)
    theUser = homepage.getUser(request)
    outDict["user"] = theUser.username


    outDict["pgTitle"] = "Time Series Data"
    #outDict["deployments"] =deps
    outDict["nodeDropdowns"] = homepage.getNodeDropdowns()


    return outDict
#    return render_to_response('cogentviewer:templates/timeseries.mak',
#                              outDict,
#                              request=request)
