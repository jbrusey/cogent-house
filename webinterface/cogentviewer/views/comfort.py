"""
Fetch Comfort informtaion from a House
"""



from pyramid.response import Response
from pyramid.renderers import render_to_response
import pyramid.url

from cogentviewer.models.meta import DBSession
import cogentviewer.models as models


from pyramid.view import view_config

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@view_config(route_name='comfort', renderer='json')
def getHouseComfort(request):

    houseId = request.matchdict.get("hid")
    typeId = request.matchdict.get("tid")

    theHouse = DBSession.query(models.House).filter_by(id = houseId).first()
    #if theHouse is None:
    #    log.debug("No Such House")
    #    #Return a 404 if no such house is found
    #    request.response.status = 404
    #    return

    #Run Whatever Query we need to....
    theQry = DBSession.query(models.Reading).filter_by(typeId = typeId)
    theQry = theQry.limit(10)
    print theQry

    #And Turn Into Comfort Stuff

    #....

    #If you can get the data like this we are onto a winner...

    roomData =[{"name":"a Room",
                "data":{"hot":10,
                        "warm":20,
                        "cold":30,
                        }
                },
               {"name":"aother Room",
                "data":{"hot":100,
                        "warm":200,
                        "cold":300,
                        }
                }
               ]

    return roomData
