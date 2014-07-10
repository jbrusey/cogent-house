"""
Look Through The Current Dataset
"""

#import sqlalchemy

from pyramid.view import view_config

import cogentviewer.views.homepage as homepage

@view_config(route_name='databrowser',
             renderer='browser.mak', 
             permission="view")
def main(request):
    """
    Get details for and display the databrowser page
    """
    outdict = {}
    outdict["headLinks"] = homepage.genHeadUrls(request)
    outdict["sideLinks"] = homepage.genSideUrls(request)

    theuser = homepage.getUser(request)
    outdict["user"] = theuser.username

    outdict["pgTitle"] = "Data Browser"
    return outdict
    
