"""Class / View for Login / Logout"""

import logging
log = logging.getLogger(__name__)

from pyramid.view import view_config

from pyramid.security import (
    remember,
    forget,
    )

from pyramid.httpexceptions import (
    HTTPFound,
    )

import cogentviewer.views.homepage as homepage
import cogentviewer.models.meta as meta
from ..models.meta import DBSession
import cogentviewer.models.user as user
import cogentviewer.utils.security as security



def checkLogin(request):
    """Helper Function that allows us to check login status

    return (status,outDict) for this login
    """

    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = request.route_url("home")
    #came_from = request.params.get('came_from', referrer)

    log.debug("Checking Request")

    #No empty fields as Bootstrap deals with em.
    username = request.POST.get("username")
    password = request.POST.get("password")

    #Fetch the user from the database:
    theUser = DBSession.query(user.User).filter_by(username=username).first()
    if theUser is None:
        return False, {"loginMsg" : "No Such User"}

    log.debug(theUser.password)
    passOk = security.pwdContext.verify(password,
                                        theUser.password)

    if passOk:
        log.debug("Passwords match")
        headers = remember(request, theUser.id)
        return True, HTTPFound(location=referrer,
                               headers=headers)
    else:
        log.debug("Passwords Failiure")
        return False, {"loginMsg" : "Invalid Login Details"}


@view_config(route_name="login", renderer="cogentviewer:templates/login.mak")
#@forbidden_view_config(renderer="cogentviewer:templates/login.mak")
def loginView(request):
    """Show the login view"""
    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)

    outDict["pgTitle"] = "Login"
    #outDict["deployments"] =deps

    log.debug(request.POST)

    if "submit" in request.POST:
        status, msg = checkLogin(request)
        if status:
            return msg
        else:
            outDict.update(msg)

    return outDict

@view_config(route_name="logout")
def logout(request):
    """Show the Logout View"""
    headers = forget(request)

    return HTTPFound(location=request.route_url("home"),
                     headers=headers)



def checkRegister(request):
    """Check the status of registration"""

    username = request.POST.get("username")
    email = request.POST.get("email")
    password = request.POST.get("password")


    #Check that that username is not taken
    checkUser = DBSession.query(user.User).filter_by(username=username).first()
    if checkUser:
        log.debug("User Exists {0}".format(checkUser))
        return False, {"loginMsg" : "Username already used"}


    #Otherwise add a new User
    #Encode the password

    newUser = user.User(username=username,
                        email=email,
                        password=security.pwdContext.encrypt(password))
    DBSession.add(newUser)
    DBSession.flush()
    return True, HTTPFound(location=request.route_url("home"))



@view_config(route_name="register",
             renderer="cogentviewer:templates/register.mak")
def registerView(request):
    """Register a user"""
    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)

    outDict["pgTitle"] = "Register"
    #outDict["deployments"] =deps

    if "submit" in request.POST:
        status, msg = checkRegister(request)
        if status:
            return outDict
        else:
            outDict.update(msg)

    return outDict
