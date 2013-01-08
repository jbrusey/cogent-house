"""
Node Status and Admin
"""

from pyramid.response import Response
from pyramid.renderers import render_to_response
import pyramid.url

import sqlalchemy

import logging
log = logging.getLogger(__name__)

import homepage

import cogentviewer.models.meta as meta
import cogentviewer.models as models

import time
import datetime
from itertools import groupby

def _groupDate(item):
    """ Extract the date from a Readings datetime object"""
    return item.time.date()

def status(request):
    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)

    outDict["pgTitle"] = "Node Status"
    #outDict["deployments"] =deps

    outDict["nodeDropdowns"] = homepage.getNodeDropdowns()



    return render_to_response('cogentviewer:templates/status.mak',
                              outDict,
                              request=request)


def _getStatus(request):
    pass


def admin(request):
    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)

    outDict["pgTitle"] = "Admin Interface"

    session = meta.Session()
    

    return render_to_response('cogentviewer:templates/admin.mak',
                              outDict,
                              request=request)
