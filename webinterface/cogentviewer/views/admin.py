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

import subprocess

from pygments import highlight
from pygments.lexers import BashLexer, TextLexer
from pygments.formatters import HtmlFormatter

import logging
LOG = logging.getLogger(__name__)

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


@view_config(route_name="serverstatus", renderer="cogentviewer:templates/serverstatus.mak", permission="view")
def serverstatus(request):
    """Server Status Page"""
    outDict = {}
    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)
    theUser = homepage.getUser(request)
    outDict["user"] = theUser.username

    outDict["pgTitle"] = "Server Status"

    #I want to check the server status
    #out = subprocess.call(["service", "ch-sf", "status"]) #Just returns 0 regardless of status
    out = subprocess.Popen(["service", "ch-sf", "status"], 
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE).communicate()

    #If running 
    running = "start" in out[0]
    if running:
        outDict["chsf"] = 0
    else:
        if out[1]:
            outDict["chsf"] = out[1]
        else:
            outDict["chsf"] = out[0]

    #And the Base Server

    out = subprocess.Popen(["service", "ch-base", "status"], 
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE).communicate()

    LOG.debug(out)
    #If running 
    running = "start" in out[0]
    LOG.debug("base running{0}".format(running))
    if running:
        outDict["chbase"] = 0
    else:
        if out[1]:
            outDict["chbase"] = out[1]
        else:
            outDict["chbase"] = out[0]

    #ut = subprocess.call(["service", "ch-base", "status"])
    #utDict["chbase"] = out


    try:
        #check_output only in 2.7
        #out = subprocess.check_output(["tail","/var/log/ch/BaseLogger.log"])
        out = subprocess.Popen(["tail", "/var/log/ch/BaseLogger.log"], stdout=subprocess.PIPE).communicate()[0]
        outDict["logpass"] = True
        outDict["logtail"] = highlight(out,BashLexer(),HtmlFormatter())
    except subprocess.CalledProcessError:
        outDict["logpass"] = False

    out = subprocess.call(["ping","cogentee.coventry.ac.uk","-c","4"])
    outDict["ping"] = out

    #out = subprocess.check_output(["ifconfig"])
    
    #out = subprocess.Popen(["ifconfig"], stdout=subprocess.PIPE).communicate()[0]
    #outDict["ifconfig"] = highlight(out,BashLexer(),HtmlFormatter())
    outDict["ifconfig"] = "None"
    


    return outDict
