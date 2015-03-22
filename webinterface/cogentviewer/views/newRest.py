from pyramid.view import view_defaults
from pyramid.view import view_config
from pyramid.response import Response

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


import cogentviewer.models.meta as meta
from ..models.meta import DBSession
import cogentviewer.models as models

import datetime

from sqlalchemy.orm import mapperlib

TABLEMAP = {}


def findClass(tableName):
    """Helper method that attempts to find a SQLA class given a tablename
    :var tablename: Name of table to find
    """

    tableName = tableName.lower()
    mappedTable = TABLEMAP.get(tableName,None)
    if mappedTable:
        return mappedTable


    for x in mapperlib._mapper_registry.items():
        #mapped table
        checkTable = x[0].mapped_table
        theClass = x[0].class_
        checkName = checkTable.name.lower()
        TABLEMAP[checkName] = theClass
        if checkName == tableName:
            mappedTable = theClass
            
    return mappedTable

class RESTBase(object):
    def __init__(self,request):
        """Here we can deal with all the service specific stuff, such as unpacking parameters and json objects"""
        log.debug("===== Main Rest Called =====")
        self.request = request

        theId = request.matchdict.get("id",None)
        log.debug("Request Id {0}".format(theId))
        self.theId = theId

        parameters = request.params
        log.debug("Paramters {0}".format(parameters))
        self.parameters = parameters

        textClass = "House"
        self.requestClass = findClass(textClass)

        #Convert Text class to a proper Class

        #Search Parameters
        self.offset = None
        self.limit = None

        #theType = request.matchdict.get("theType",None)
        #log.debug("Object Type {0}".format(theType))
        theRange = request.headers.get("Range",None)
        if theRange:
            log.debug("Range Specified {0}".format(theRange))
            #pluck out the relitive numbers
            theRange = [int(x) for x in theRange.split("=")[-1].split("-")]
            log.debug(theRange)
            #self.offset = theRange[0]
            #self.limit = theRange[1] - theRange[0]
        self.theRange = theRange

    def processQuery(self):
        pass

    @view_config(request_method="GET")
    def processGET(self):
        """Deal with GET Requests"""
        log.debug("Rest Service Called with GET")
        
        #Start the Query
        items = DBSession.query(self.requestClass)
        if self.theId:
            items = items.filter_by(id=self.theId)

        totalItems = items.count()
        log.debug("Total of {0} items returned by Query".format(totalItems))

        #Convert to something that JSON likes
        #Deal with Ranges
        if self.theRange:
            #Offset 
            items = items.offset(self.theRange[0])
            items = items.limit(self.theRange[1] - self.theRange[0])
            #Count 
            itemCount = items.count()
            #Return the following range STRING
            rangeStr = "items {0}-{1}/{2}".format(self.theRange[0],self.theRange[0]+itemCount,totalItems)
            log.debug(rangeStr)
        #if self.offset:
        #    items = items.offset(self.offset)
            
        #if self.limit:
        #    items = items.limit(self.limit)
        #    retu
        #Sod it and return a "Range" header with the count
        
        # if self.theRange:
        #     #Ranges should be <start> - <end>
        #     items = items.offset(self.theRange[0])
        #     items = items.limit(self.theRange[1] - self.theRange[0])

        outItems = [x.toDict() for x in items]
        return outItems

    @view_config(request_method="POST")
    def processPOST(self):
        """Deal with POST REquests"""
        log.debug("Rest Service Called with POST")
        return ["POST",self.theId]

    @view_config(request_method="PUT")
    def processPUT(self):
        """Deal with PUT Requests"""
        log.debug("Rest Service PUT")
        return ["PUT",self.theId]

    @view_config(request_method="DELETE")
    def processDELETE(self):
        """Deal with DELETE Requests"""
        log.debug("Rest Service DELETE")
        return ["DELETE",self.theId]


@view_defaults(route_name="newRest",renderer="json")
class RESTService(RESTBase):
    def __init__(self,request):
        log.debug("Sub Class Called")
        RESTBase.__init__(self,request)
    pass
