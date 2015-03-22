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
from ..models.meta import DBSession
import cogentviewer.models as models
#import cogentviewer.views.homepage
import homepage


import logging
log = logging.getLogger(__name__)

@view_config(route_name='user', renderer='cogentviewer:templates/user.mak', permission="view")
def user(request):
    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)
    thisUser = homepage.getUser(request)
    outDict["user"] = thisUser.username
    outDict["formalert"] = None
    outDict["pgTitle"] = "Add / Edit User"

    
    uid = request.matchdict.get("id",None)
    log.debug("User Page Called.  User Id >{0}<".format(uid))

    if uid is None or uid == "":
        log.debug("--> No User specified")
        theUser = None
    else:
        theUser =DBSession.query(models.User).filter_by(id=uid).first()
        

    #Deal with form 
    if "submit" in request.POST:
        log.debug("Form Submitted")
        username = request.POST.get("username")
        usermail = request.POST.get("email")
        userpass = request.POST.get("password")
        log.debug("Form Details Name {0} Mail {1} Pass {2}".format(username,usermail,userpass))
        if theUser is None:
            theUser = models.User(username = username)
            DBSession.add(theUser)
        #And update everything else
        theUser.email = usermail
        
        #Encode and store password
        theUser.password = meta.pwdContext.encrypt(userpass)
        theUser.level = "root"
        
        DBSession.flush()

        outDict["formalert"] = "User Details updated"
        #Update 
  
    log.debug("User Requred by Query {0}".format(theUser))
    if theUser is None:
        log.debug("No Such User")
        outDict["userName"] = None
        outDict["userMail"] = None

    else:
        outDict["userName"] = theUser.username
        outDict["userMail"] = theUser.email


        
    


        
        

    return outDict
