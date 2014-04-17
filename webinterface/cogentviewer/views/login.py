from pyramid.response import Response
from pyramid.view import view_config

import logging
log = logging.getLogger(__name__)

import homepage

import cogentviewer.models.meta as meta
#import cogentviewer.models as models
import cogentviewer.models.user as user

#For Security

from pyramid.view import (
    view_config,
    forbidden_view_config,
    )

from pyramid.security import (
    remember,
    forget,
    authenticated_userid,
    )

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )


def checkLogin(request):
    """Helper Function that allows us to check login status

    return (status,outDict) for this login
    """

    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = request.route_url("home")
    came_from = request.params.get('came_from', referrer)

    log.debug("Checking Request")

    #No empty fields as Bootstrap deals with em.
    username = request.POST.get("username")
    password = request.POST.get("password")

    #Fetch the user from the database:
    session = meta.Session()
    theUser = session.query(user.User).filter_by(username=username).first()
    if theUser is None:
        return False,{"loginMsg":"No Such User"}

    log.debug(theUser.password)
    passOk = meta.pwdContext.verify(password,theUser.password)

    if passOk:
        log.debug("Passwords match")
        headers = remember(request,theUser.id)
        return True,HTTPFound(location = referrer,
                              headers=headers)
    else:
        log.debug("Passwords Failiure")
        return False,{"loginMsg":"Invalid Login Details"}
    

    # email = request.POST.get("email",None)
    # password = request.POST.get("password",None)
    # log.debug("Uname {0} Password {1}".format(email,password))

    # #Fetch the user from the database:
    # session = meta.DBSession()
    # theUser = session.query(user.User).filter_by(email=email).first()
    # if theUser is None:
    #     return False,{"loginMsg":"No Such User"}
    
    # #username = theUser.name
    # userId = theUser.id
    # #Otherwise check the password
    # passOk = meta.pwdContext.verify(password,theUser.password)

    # #if username == password:
    # if passOk:
    #     log.debug("Login Ok")
    #     #headers = remember(request,username)
    #     headers = remember(request,userId)
    #     return True,HTTPFound(location = referrer,
    #                           headers=headers)
    # else:
    #     return False,{"loginMsg":"Invalid Login Details"}


@view_config(route_name="login",renderer="cogentviewer:templates/login.mak")
@forbidden_view_config(renderer="cogentviewer:templates/login.mak")
def loginView(request):

    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)

    outDict["pgTitle"] = "Login"
    #outDict["deployments"] =deps

    log.debug(request.POST)

    if "submit" in request.POST:
        status,msg = checkLogin(request)
        if status:
            return msg
        else:
            outDict.update(msg)

    return outDict
   

@view_config(route_name="logout")
def logout(request):
    headers = forget(request)

    return HTTPFound(location=request.route_url("home"),
                     headers=headers)
    


def checkRegister(request):
    """Check the status of registration"""

    username = request.POST.get("username")
    email = request.POST.get("email")
    password = request.POST.get("password")

    session = meta.Session()
    
    #Check that that username is not taken
    checkUser = session.query(user.User).filter_by(username= username).first()
    if checkUser:
        log.debug("User Exists {0}".format(checkUser))
        return False,{"loginMsg":"Username already used"}
    
    
    #Otherwise add a new User
    #Encode the password
    
    newUser = user.User(username=username,
                        email=email,
                        password= meta.pwdContext.encrypt(password))
    session.add(newUser)
    session.flush()
    return True,HTTPFound(location = request.route_url("home"))
    pass
    

@view_config(route_name="register",renderer="cogentviewer:templates/register.mak")
def registerView(request):

    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)

    outDict["pgTitle"] = "Register"
    #outDict["deployments"] =deps

    if "submit" in request.POST:
        status,msg = checkRegister(request)
        if status:
            return outDict
        else:
            outDict.update(msg)

    return outDict
