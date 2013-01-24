"""
Look Through The Current Dataset
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


def main(request):
    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)

    outDict["pgTitle"] = "Data Browser"
    #outDict["deployments"] =deps
    return render_to_response('cogentviewer:templates/browser.mak',
                              outDict,
                              request=request)
