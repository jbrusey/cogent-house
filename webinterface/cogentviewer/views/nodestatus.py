import logging
log = logging.getLogger(__name__)

import datetime
import subprocess
import urllib

import sqlalchemy

from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import view_config

import homepage
from ..models import meta
from ..models.meta import DBSession
import cogentviewer.models as models



@view_config(route_name='nodestatus',
             renderer='cogentviewer:templates/nodestatus.mak',permission="view")
def nodestatus(request):
    log = logging.getLogger(__name__)
    outdict = {}
    outdict["headLinks"] = homepage.genHeadUrls(request)
    outdict["sideLinks"] = homepage.genSideUrls(request)
    theUser = homepage.getUser(request)
    outdict["user"] = theUser.username

    outdict["nodeDropdowns"] = homepage.getNodeDropdowns()
    outdict["pgTitle"] = "House Status"

    #So we want a list of active houses
    
    nodeqry = DBSession.query(models.Node)
    nodeqry = nodeqry.order_by(models.Node.id)
    

    nodelist = []
    for node in nodeqry:
        thisnode = {"nid": node.id,
                    "locationId":node.locationId,
                    "house":None,
                    "room":None,
                    "datalocs" : None,
                    "datatimes" : None,
                    "datacount" : None,
                    "datahouse" : None,
                    }

        if node.location:
            thisnode["house"] = node.location.house.address
            thisnode["room"] = node.location.room.name

        #Check what locations we have data for
        rdgqry = DBSession.query(models.Reading.locationId, 
                               sqlalchemy.func.max(models.Reading.time),
                               sqlalchemy.func.count(models.Reading.time),
                               ).filter_by(nodeId = node.id)
        rdgqry = rdgqry.group_by(models.Reading.locationId)

        
        #log.debug("Locations are {0}".format(rdgqry.all()))
        if rdgqry.count() == 0:
            pass #Hacky but needs fixing
        elif rdgqry.count() == 1:
            thisnode["datalocs"] = rdgqry.first()[0]
            thisnode["datatimes"] = rdgqry.first()[1]
            thisnode["datacount"] = rdgqry.first()[2]
            hseqry = DBSession.query(models.Location).filter_by(id = rdgqry.first()[0]).first()
            thisnode["datahouse"] = hseqry.house.address
        else:
            thisnode["datalocs"] = [x[0] for x in rdgqry]
            thisnode["datatimes"] = [x[1] for x in rdgqry]
            thisnode["datacount"] = [x[2] for x in rdgqry]


        nodelist.append(thisnode)


    outdict["nodelist"] = nodelist
    

    return outdict
