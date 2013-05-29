"""
Node Status and Admin
"""

import time
import datetime
from itertools import groupby

from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import view_config
import pyramid.url

import sqlalchemy

#import logging
#log = logging.getLogger(__name__)

import cogentviewer.models.meta as meta
import cogentviewer.models as models
#import cogentviewer.views.homepage
import homepage


def _groupDate(item):
    """ Extract the date from a Readings datetime object
    @var item:  Reading object to take date from

    @return:  A datetime object for this reading
    """
    return item.time.date()

@view_config(route_name='status', renderer='cogentviewer:templates/status.mak', permission="view")
def status(request):
    """Show Status page"""
    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)
    theUser = homepage.getUser(request)
    outDict["user"] = theUser.username

    outDict["pgTitle"] = "Node Status"
    #outDict["deployments"] =deps

    outDict["nodeDropdowns"] = homepage.getNodeDropdowns()



    return render_to_response('cogentviewer:templates/status.mak',
                              outDict,
                              request=request)


@view_config(route_name='admin', renderer='cogentviewer:templates/admin.mak', permission="view")
def admin(request):
    """
    Show Admin Page
    """
    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)
    theUser = homepage.getUser(request)
    outDict["user"] = theUser.username

    outDict["pgTitle"] = "Admin Interface"

    
    session = meta.Session()
    #I Want users
    theQry = session.query(models.User)
    userList = []
    for item in theQry:
        print item
        print "{0} {1} {2}".format(item.id,item.username,item.password)
        userList.append([item.username,item.email,request.route_url("user",id=item.id)])

    outDict["userList"] = userList
    

    return render_to_response('cogentviewer:templates/admin.mak',
                              outDict,
                              request=request)
