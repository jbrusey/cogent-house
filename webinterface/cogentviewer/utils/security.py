"""
Functions to deal with security and user level permissions
:author: Dan Goldsmith <djgoldsmith@googlemail.com
"""

import logging
LOG = logging.getLogger(__name__)

from pyramid.security import Allow
from pyramid.security import Everyone

from passlib.context import CryptContext

#Global Pasword Hashing Algorithm
pwdContext = CryptContext(
    #Schemes to Support
    schemes=["sha256_crypt", "md5_crypt"],
    default="sha256_crypt"
    )


import cogentviewer.models.user as user
import cogentviewer.models.meta as meta

class RootFactory(object):
    """New Root Factory Object to assign permissions
    And control the ACL
    """

    __acl__ = [(Allow, Everyone, "logout"),
               (Allow, "group:user", "view"),
               (Allow, "group:root", "view"),
               (Allow, "group:root", "admin"),
               ]

    def __init__(self, request):
        pass

def groupfinder(userid, request):
    """Method to discover which group a given user belongs to
    this can be used to allow group based permissions for page
    access

    :param userid: Id of user to check permissions for
    :return:  The group tis user belongs to

    """
    LOG.debug("-----> Group Finder Called {0}".format(userid))
    session = meta.Session()
    theUser = session.query(user.User).filter_by(id=userid).first()

    thegroup = ["group:none"]
    if theUser is None:
        return thegroup


    if theUser.level == "root":
        thegroup = ["group:root"]
    elif theUser.level == "user":
        thegroup =  ["group:user"]

    LOG.debug("User Level is {0}".format(thegroup))
    return thegroup
