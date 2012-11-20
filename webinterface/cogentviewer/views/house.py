from pyramid.response import Response
from pyramid.renderers import render_to_response
import pyramid.url

import logging
log = logging.getLogger(__name__)

import homepage

import cogentviewer.models.meta as meta
import cogentviewer.models as models

def editHouse(request):
    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)

    theId = request.matchdict.get("id",None)

    session = meta.Session()

    if theId:
        outDict["pgTitle"] = "Add / Edit House"
        theHouse = session.query(models.House).filter_by(id=theId).first()
        #print "-#"*30
        #print theHouse
        #print theHouse.toDict()
        #outDict["theHouse"] = theHouse.toDict()
        outDict["theHouse"] = theId
    else:
        outDict["pgTitle"] = "Add New House"
        



    return render_to_response('cogentviewer:templates/house.mak',
                              outDict,
                              request=request)
