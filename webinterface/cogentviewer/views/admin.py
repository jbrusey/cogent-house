"""
Node Status and Admin
"""

from pyramid.renderers import render_to_response
from pyramid.view import view_config

import subprocess

from pygments import highlight
from pygments.lexers import BashLexer, TextLexer
from pygments.formatters import HtmlFormatter

import logging
LOG = logging.getLogger(__name__)

from cogentviewer.models.meta import DBSession
import cogentviewer.models as models
#import cogentviewer.views.homepage
import homepage


def _groupDate(item):
    """ Extract the date from a Readings datetime object
    @var item:  Reading object to take date from

    @return:  A datetime object for this reading
    """
    return item.time.date()

@view_config(route_name='status',
             renderer='cogentviewer:templates/status.mak',
             permission="view")
def status(request):
    """Show Status page"""
    out_dict = {}
    out_dict["headLinks"] = homepage.genHeadUrls(request)
    out_dict["sideLinks"] = homepage.genSideUrls(request)
    the_user = homepage.getUser(request)
    out_dict["user"] = the_user.username

    out_dict["pgTitle"] = "Node Status"
    #out_dict["deployments"] =deps

    out_dict["nodeDropdowns"] = homepage.getNodeDropdowns()



    return render_to_response('cogentviewer:templates/status.mak',
                              out_dict,
                              request=request)


@view_config(route_name='admin',
             renderer='cogentviewer:templates/admin.mak',
             permission="admin")
def admin(request):
    """
    Show Admin Page
    """
    out_dict = {}
    out_dict["headLinks"] = homepage.genHeadUrls(request)
    out_dict["sideLinks"] = homepage.genSideUrls(request)
    the_user = homepage.getUser(request)
    out_dict["user"] = the_user.username

    out_dict["pgTitle"] = "Admin Interface"

    # get list of users
    the_qry = DBSession.query(models.User)
    user_list = []
    for item in the_qry:
        user_list.append([item.username,
                         item.email,
                         request.route_url("user", id=item.id)])

    out_dict["userList"] = user_list


    return render_to_response('cogentviewer:templates/admin.mak',
                              out_dict,
                              request=request)


@view_config(route_name="serverstatus",
             renderer="cogentviewer:templates/serverstatus.mak",
             permission="view")
def serverstatus(request):
    """Server Status Page"""
    out_dict = {}
    out_dict = {}
    out_dict["headLinks"] = homepage.genHeadUrls(request)
    out_dict["sideLinks"] = homepage.genSideUrls(request)
    the_user = homepage.getUser(request)
    out_dict["user"] = the_user.username

    out_dict["pgTitle"] = "Server Status"

    #I want to check the server status
    out = subprocess.Popen(["service", "ch-sf", "status"],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE).communicate()

    #If running
    running = "start" in out[0]
    if running:
        out_dict["chsf"] = 0
    else:
        if out[1]:
            out_dict["chsf"] = out[1]
        else:
            out_dict["chsf"] = out[0]

    #And the Base Server

    out = subprocess.Popen(["service", "ch-base", "status"],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE).communicate()

    LOG.debug(out)
    # If running
    running = "start" in out[0]
    LOG.debug("base running{0}".format(running))
    if running:
        out_dict["chbase"] = 0
    else:
        if out[1]:
            out_dict["chbase"] = out[1]
        else:
            out_dict["chbase"] = out[0]


    try:
        #check_output only in 2.7
        out = subprocess.Popen(["tail", "/var/log/ch/BaseLogger.log"],
                               stdout=subprocess.PIPE).communicate()[0]
        out_dict["logpass"] = True
        out_dict["logtail"] = highlight(out, BashLexer(), HtmlFormatter())
    except subprocess.CalledProcessError:
        out_dict["logpass"] = False

    out = subprocess.call(["ping", "cogentee.coventry.ac.uk", "-c", "4"])
    out_dict["ping"] = out

    out_dict["ifconfig"] = "None"

    return out_dict
