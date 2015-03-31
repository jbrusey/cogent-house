"""
Class to deal with REST Requests
"""

from pyramid.response import Response
from pyramid.renderers import render_to_response
import pyramid.url

import pandas

import cogentviewer.models.meta as meta
from ..models.meta import DBSession
import cogentviewer.models as models
import homepage

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

#import sqlalchemy.orm.mapper
import sqlalchemy
import dateutil.parser
import transaction

import datetime
import time
import zlib
import json

GAS_TO_METERS = 2.83 #Convert to cubic meters
GAS_PULSE_TO_METERS = GAS_TO_METERS / 100.0  #As gas is in 100's of cubic feet
GAS_VOLUME = 1.022640 #Correction Value
GAS_COLORIFIC = 39.3  #Calorific Value
GAS_CONVERSION = 3.6  #kWh conversion factor

def _getDeploymentTree(request):
    """Fetch a tree to be used for navigation"""

    #Fetch a list of deployments

    params = request.params
    log.debug("Query Parameters {0}".format(params))
    if params:
        parent = params.get("parent", None)
        limit = params.get("limit", None)
        log.debug("Looking for parent {0}".format(parent))
        log.debug("Tree has limit {0}".format(limit))
        #Do we have a query

        if parent:
            #Everything should have a parent (even if it is root)
            depSplit = parent.split("_")
            if parent == "root":
                #Root of tree, return all deployments
                theQry = DBSession.query(models.Deployment)
                outList = []
                for item in theQry:
                    log.debug("Processing {0} ".format(item))
                    outList.append({"id":"d_{0}".format(item.id),
                                    "name":item.name,
                                    "parent":"root",
                                    "type":"deployment"
                                    })
                #And we also want houses without a deployment
                log.debug("Adding houses without deployment")
                outList.append({"id":"d_None",
                                "name": "Houses without deployment",
                                "parent":"root",
                                "type":"deployment"})
                return outList

            elif depSplit[0] == "d":
                log.debug("Parent is a Deployment")
                if depSplit[1] == "None":
                    #Fetch all houses without a deployment
                    theQry = DBSession.query(models.House).filter_by(deploymentId=None)
                else:
                    #Fetch for this particular deployment
                    theQry = DBSession.query(models.House).filter_by(deploymentId=depSplit[1])

                outList = []
                log.debug("--> Children Are:")
                for item in theQry:
                    log.debug("--> {0}".format(item))
                    outList.append({"id":"h_{0}".format(item.id),
                                    "name":item.address,
                                    "parent":"d_{0}".format(depSplit[1]),
                                    "type":"house",
                                    }
                                   )
                return outList
            elif depSplit[0] == "h":
                log.debug("Parent is a House")
                theQry = DBSession.query(models.Location).filter_by(houseId=depSplit[1])
                log.debug("--- {0} {1}".format(theQry, theQry.count()))
                outList = []
                for item in theQry:
                    log.debug("----> {0}".format(item))
                    #if len(item.readings) > 0:
                    if item:
                        rname = "NA"
                        if item.room:
                            rname = item.room.name
                        outList.append({"id":"l_{0}".format(item.id),
                                        "name":"({0}) {1}".format(item.id, rname),
                                        "parent":"h_{0}".format(depSplit[1]),
                                        "type":"location",
                                        }
                                       )
                return outList

            elif depSplit[0] == "l":
                log.debug("Parent is a Location")
                if limit == "exposure":
                    return None
                outList = []
                #Use the Node Location Table to find Nodes associated with this Location
                theqry = DBSession.query(models.Location).filter_by(id=depSplit[1])
                theitem = theqry.first()
                log.debug("The Qry {0}".format(theitem))
                log.debug("--> {0}".format(theitem.allnodes))
                allNodes = theitem.allnodes

                #And a fallback if the server doesnt accept node / locations
                if len(allNodes) == 0:
                    log.debug("No Nodes Detected")
                    theQry = DBSession.query(models.Reading.nodeId).filter_by(locationId=depSplit[1]).distinct().all()
                    log.debug("Node Ids {0}".format(theQry))
                    nids = [x[0] for x in theQry]
                    log.debug("Nids {0}".format(nids))
                    nodeQry = DBSession.query(models.Node).filter(models.Node.id.in_(nids))
                    log.debug("Node Qry {0}".format(nodeQry.all()))
                    allNodes = nodeQry.all()

                #Fetch all Nodes
                #for node in theitem.allnodes:
                for node in allNodes:
                    log.debug("--> --> Processing Node {0}".format(node))
                    log.debug("--> --> Sensors Are {0}".format(node.sensors))

                    theQry = DBSession.query(models.Sensor).filter_by(nodeId=node.id)
                    log.debug("--> --> QRY SENSORS {0}".format(theQry.all()))

                    theSensors = node.sensors
                    if len(theSensors) is 0:
                        theQry = DBSession.query(models.Reading.typeId).filter_by(nodeId=node.id).distinct()
                        #log.debug("--> --> QRY Types {0}".format(theQry.all()))
                        sids = [x[0] for x in theQry]
                        sensorQry = DBSession.query(models.SensorType).filter(models.SensorType.id.in_(sids))
                        for sensortype in sensorQry:
                            log.debug("==> ==> {0}".format(sensortype))
                            theItem = {"id":"t_{0}_{1}".format(depSplit[1], sensortype.id),
                                       "name":sensortype.name,
                                       "type":"sensorType",
                                       "parent":"l:{0}".format(depSplit[1]),
                                       }
                            if not theItem in outList:
                                outList.append(theItem)

                    else:
                        for sensor in theSensors:
                            log.debug("--> ==> Sensor are {0}".format(sensor))
                            sensortype = sensor.sensorType
                            log.debug("==> ==> {0}".format(sensortype))
                            theItem = {"id":"t_{0}_{1}".format(depSplit[1], sensor.sensorTypeId),
                                       "name":sensortype.name,
                                       "type":"sensorType",
                                       "parent":"l:{0}".format(depSplit[1]),
                                       }
                            outList.append(theItem)

                return outList
        return []
    else:
        log.debug("Returning All Objects")
        outList = [
            {"id":"root",
             "name":"All Deployments"},
            ]
        return outList


    log.debug("Query Returns {0}".format(outList))
    return outList


def genericRest(request):
    #Handle a call to all rest services
    return _wrappedRest(request)

def getHouseRooms(request):
    """Get rooms associated with the house.

    Given an house Id return the rooms associated with this house
    For example, /rest/houserooms/1  will return all rooms associated with
    HouseId 1 as Id, name pairs

    :return: List of {Location id, name} pairs for all rooms in this house

    """

    params = request.params
    houseid = request.params.get("id", None)
    log.debug("getHouseRooms called with Id parameter {0}".format(houseid))
    if houseid is None:
        log.debug("--> No Id Parameter supplied")
        return []

    thehouse = DBSession.query(models.House).filter_by(id=int(houseid)).first()
    if thehouse is None:
        log.warning("--> No such houseId in table")
        return []

    locations = thehouse.locations
    roomlist = []
    #Iterate through all locations for this house and append to list
    for item in thehouse.locations:
        log.debug(item)
        if item.room:
            roomname = item.room.name
        else:
            #If for some reason we have an invalid room type
            log.warning("Bad room type for location: {0}".format(item))
            roomname = "noRoom"

        roomlist.append({"id":item.id,
                         "name":roomname})

    return roomlist


#@models.timings.timedtext("Generic Rest Query")
#Wrapped in-case we wish to valuate the time taken
def _wrappedRest(request):


    log.debug("="*80)
    #Fetch all the deployments
    #theQuery = DBSession.query(models.Deployment)
    #deployments = [x.toREST() for x in theQuery]


    #Get the Method
    reqType = request.method

    theId = request.matchdict.get("id", None)
    theType = request.matchdict.get("theType")
    log.info("Request Type {0} Request Id: {1}".format(reqType, theId))
    log.debug("Object Type {0}".format(theType))

    #For Version Numbers
    if theType.lower() == "version":
        return homepage.version

    if theType.lower() == "lastsync":
        return lastSync(request)

    if theType.lower() == "lastnodesync":
        return lastnodesync(request)

    if theType.lower() == "houserooms":
        return getHouseRooms(request)

    if theType.lower() == "counts":
        return getcounts(request)

    if theType.lower() == "heatmap":
        return getheatmap(request)

    #Stuff for Pavel / JH
    if theType.lower() == "summary":
        return getsummary(request)
    if theType.lower() == "energysummary":
        return getenergy(request)

    if theType.lower() == "schema":
        return getschema(request)

    if theType.lower() == "rpc":
        qry = DBSession.query(models.Server)
        outlist = []
        for item in qry:
            if item.rpc == 1:
                outlist.append((item.hostname, "tunnel"))
        #return [("salford21", "tunnel")]
        return outlist
        #return [("salford21", "tunnel"),

    if theType.lower() == "network":
        return getnetwork(request)

    if theType.lower() == "topology":
        return gettopology(request)

    #Deal with "BULK" uploads
    if theType.lower() == "bulk":
        log.debug("BULK UPLOAD")
        #parameters = request.json_body

        parameters = request.body
        #log.debug(parameters)

        try:
            unZip = zlib.decompress(parameters)
        except zlib.error, e:
            log.warning("Bulk Upload Error (ZLIB) {0}".format(e))
            unZip = parameters

        log.debug("==== Bulk Upload Unzipped ====")
        jsonBody = json.loads(unZip)
        log.debug("--> Converted from JSON")
        #log.debug(jsonBody)
        #jsonBody = jsonh.loads(unZip)
        #print jsonBody

        objGen = models.clsFromJSON(jsonBody)
        log.debug("--> Generator Created")
        t1 = time.time()
        sp = transaction.savepoint()
        for item in objGen:
            #pass
            #print "----> New Item to be Added {0}".format(item)
            #DBSession.merge(item)
            DBSession.add(item)

        try:
            DBSession.flush()
        #except sqlalchemy.IntegrityError, e:
        except Exception, e:
            log.warning("Bulk Upload Error")
            log.warning(e)
            sp.rollback()
            #Try doing as a merge instead
            objGen = models.clsFromJSON(jsonBody)
            for item in objGen:
                DBSession.merge(item)

                try:
                    DBSession.flush()
                except Exception, e:
                    log.warning("Bulk Upload Error on Merge")
                    log.warning(e)
                    request.response.status = 500
                    return ["Error: {0}".format(e)]

        t2 = time.time()
        log.debug("========= TIME {0}".format(t2-t1))
        #print "="*70
        #print [x.id for x in objGen]
        #print "="*70
        request.response.status = 201
        log.debug("Bulk Upload Success")
        #DBSession.commit()
        #DBSession.close()
        return []
        #return [x.id for x in objGen]
    elif theType.lower() == "deploymenttree":
        log.debug("Deployment Tree")
        return _getDeploymentTree(request)
        #return []

    #Mapping between types and classes. (We may be able to infer this from the mapper)
    typeMap = {"deployment":models.Deployment,
               "house":models.House,
               "reading":models.Reading,
               "node":models.Node,
               "room":models.Room,
               "roomtype":models.RoomType,
               "location":models.Location,
               "sensortype":models.SensorType,
               "nodestate":models.NodeState,
               "nodetype": models.NodeType,
               "pushstatus": models.pushstatus.PushStatus,
               }
    theModel = typeMap[theType.lower()]

    if reqType == "GET":
        #Create Query
        theQuery = DBSession.query(theModel)
        #If we have an Id filter by that
        log.debug("Get Query")
        if theId:
            log.debug("Filter by Id {0}".format(theId))
            theQuery = theQuery.filter_by(id=theId)

        #If there are no items
        totalCount = theQuery.count()
        if totalCount == 0:
            #request.response.status = 404
            log.debug("No Items in Query {0}".format(theQuery))
            return []

        #We could also do with processing parameters
        params = request.params
        if params:
            log.debug("Query parameters {0}".format(params))
            theQuery = filterQuery(theModel, theQuery, params)

        #Deal with ranges
        reqRange = request.headers.get("Range", None)
        log.debug("STD Range {0}".format(request.range))
        log.debug("Range ? {0}".format(reqRange))
        if reqRange:
            try:
                reqRange = [int(x) for x in reqRange.split("=")[-1].split("-")]
            except:
                log.warning("Error Parsing supplied range {0}".format(reqRange))
                reqRange = None

        if reqRange:
            """If a range of the query is specified"""
            log.debug("===== RANGE SPECIFIED:")
            theQuery = theQuery.offset(reqRange[0])
            theLimit = reqRange[1] - reqRange[0]
            log.debug("Limit {0}".format(theLimit))
            #theQuery = theQuery.filter(theModel.id >= reqRange[0],
            #                           theModel.id <= reqRange[1])
            secondCount = theQuery.count()
            theQuery = theQuery.limit(theLimit)
            #And set a response type
            request.response.content_range = "items {0}-{1}/{2}".format(reqRange[0],
                                                                        reqRange[0]+secondCount,
                                                                        totalCount)


        #return theModel.__table__


        retItems = [x.dict() for x in theQuery]
        if retItems:
            log.debug("--> ITEMS --> {0}".format(retItems[0]))
        #DBSession.close()
        return retItems

    elif reqType == "POST":
        #POST is used for new items
        parameters = request.json_body
        log.debug(parameters)

        newObj = theModel()
        newObj.from_json(parameters)
        log.debug("-----> NEW OBJECT {0}".format(newObj))
        DBSession.flush()
        DBSession.add(newObj)
        DBSession.flush()
        #DBSession.commit()
        #newObj.id = 5001
        log.debug("New Object {0} added".format(newObj))

        #Set the Response "Location" field to the item URL (REST GET)
        #request.response.location = "http://127.0.0.1:6543/rest/deployment{0}/".format(newObject.Id)
        #Deal with corner case for readings
        if theType.lower() == "reading":
            log.debug("Generating READING Response")
            #responseUrl = request.route_url("genericRest", theType=theType, id=None)
        else:

            responseUrl = request.route_url("genericRest", theType=theType, id=newObj.id)
            request.response.location = responseUrl
        #And Set the Response status to 201 Created
        request.response.status = 201

        #If we have updated a pushstatus make sure the server is logged in our db
        if theType.lower() == "pushstatus":
            log.debug("Push Status Sent from Server {0}".format(newObj.hostname))

            qry = DBSession.query(models.Server).filter_by(hostname=newObj.hostname).first()
            if qry is None:
                log.info("Update from New Server {0}".format(newObj))
                newserver = models.Server(hostname=newObj.hostname)
                DBSession.add(newserver)
                DBSession.flush()

        #And Return the new object

        retObj =  newObj.dict()
        DBSession.flush()
        #DBSession.close()
        return retObj

    elif reqType == "PUT":
        #Add (or modify) an item based on parameters encoded in request body

        #PUT is used to update
        log.setLevel(logging.DEBUG)
        log.debug("PUT: {0}".format(reqType))
        log.debug("QUERY STRING {0}".format(request.query_string))
        log.debug("BODY {0}".format(request.body))


        queryParams = request.params
        log.debug("PARAMS --> {0}".format(queryParams))
        #If we have an Id, Assume we want to try to update an existing object
        theQuery = DBSession.query(theModel)
        if theId:
            theQuery = theQuery.filter_by(id=theId)#.first()
            log.debug("--> Query Results on search for {0}".format(theId))
        elif queryParams:
            log.debug("--> Attempt to add new object based on search")
            #print queryParams
            theQuery = filterQuery(theModel, theQuery, queryParams)
        else:
            #Try to force the search based on the query params method
            log.debug("--> Attempt to seach based on query params method")
            queryParams = theModel().queryparams(request.json_body)
            log.debug("--> New Parameters: {0}".format(queryParams))
            theQuery  = filterQuery(theModel, theQuery, queryParams)
            
        #log.debug(theQuery)
        log.debug("COUNT {0}".format(theQuery.count()))
        log.debug(theQuery.all())

        if theQuery.count() > 1:
            log.warning("Attempt to update more than one object")
            return []
        else:
            theQuery = theQuery.first()

        if theQuery is None:
            log.warning("Attempt to update non existant object")
            theQuery = theModel()
            #newObj.from_json(parameters)
            DBSession.add(theQuery)
            DBSession.flush()
            #return []
            #DBSession.add(theQuery)

        parameters = request.json_body
        log.debug("JSON PARAMS {0}".format(parameters))


        log.debug("--> Orig {0}".format(theQuery))
        #And then Update
        theQuery.from_json(parameters)

        DBSession.flush()

        log.debug("--> New {0}".format(theQuery))


        #Set the Response "Location" field to the item URL (REST GET)
        #request.response.location = "http://127.0.0.1:6543/rest/deployment{0}/".format(newObject.Id)
        #Deal with corner case for readings
        if theType.lower() == "reading":
            responseUrl = request.route_url("genericRest",
                                            theType=theType,
                                            id=None)
        else:
            responseUrl = request.route_url("genericRest",
                                            theType=theType,
                                            id=theQuery.id)

        request.response.location = responseUrl
        #And Set the Response status to 201 Created
        request.response.status = 201


        #And Return the new object
        retObj =  theQuery.dict()
        log.setLevel(logging.INFO)
        #DBSession.close()
        return retObj


    #    pass
    elif reqType == "DELETE":
        #Return a response of 204 indicating item deleted.
        log.debug("Deleting Item with Id of {0}".format(theId))

        #We need to do some special processing to remove certain types of items
        log.debug("---- ITEM TYPE {0}".format(theType))
        if theType == "house":
            #Do some special house removing

            #Find all locations attached to this houses
            theHouse = DBSession.query(theModel).filter_by(id=theId).first()
            if theHouse is None:
                return

            locQry = DBSession.query(models.Location).filter_by(houseId=theHouse.id)

            log.debug("House is {0}  Locations are {1}".format(theHouse, theHouse.locations))

            #Reset the readings to have a null location
            for loc in locQry:
                theQry = DBSession.query(models.Reading).filter_by(locationId=loc.id)
                #loc.oldNodes = []
                log.debug("Processing Location {0}: {1} Readings Found".format(loc,
                                                                               theQry.count()))
                theQry.update({"locationId": None})

                #And Reset the other associated stuff
                #log.debug("Old Nodes {0}".format(loc.OldNodes))
                #del(loc.OldNodes)
                #loc.Node.locationId = None
                for item in loc.nodes:
                    item.locationId = None

            #Then we can remove the locations
            locQry = DBSession.query(models.Location).filter_by(houseId=theHouse.id)
            locQry.delete()

            theHouse = DBSession.query(theModel).filter_by(id=theId)
            theHouse.delete()
        elif theType in ["reading", "nodestate"]:
            request.response.status = 404
            return

        deleteCount = 0
        if theId:
            theQuery = DBSession.query(theModel).filter_by(id=theId)
            if theQuery.count() > 0:
                deleteCount = theQuery.delete()

        log.debug("{0} Items deleted".format(deleteCount))
        if deleteCount > 0:
            request.response.status = 204
    else:
        #Panic and throw an error.
        pass

        #DBSession.close()

def getheatmap(request):
    """
    Return the nodestates to be used as a heatmap
    """
    log.debug("Heatmap data requested")
    nodeid = request.matchdict.get("id", None)
    log.debug("Node Id >{0}< {1}".format(nodeid, type(nodeid)))
    if nodeid == "":
        log.debug("No Node Id Supplied")
        #nodeid = None
        nodeid = 28931

    qry = DBSession.query(models.NodeState.nodeId,
                        sqlalchemy.func.date(models.NodeState.time),
                        sqlalchemy.func.count(models.NodeState.nodeId),
                        )
    #Possibly add dates etc.
    qry = qry.group_by(models.NodeState.nodeId,
                       sqlalchemy.func.date(models.NodeState.time))

    import pandas
    df = pandas.DataFrame(qry.all(),
                          columns=["nodeid", "date", "count"],
                          )

    df = df.convert_objects(convert_dates='coerce', convert_numeric=True)
    #print df
    #print df.head()

    #Reindex
    multidf = df.set_index(["date", "nodeid"])
    wide = multidf.unstack(0) #Date runs across the top
    wide.fillna(0, inplace=True)

    outdict = {}
    
    #Now we know the dates
    datelist = [x[1].isoformat() for x in wide.columns]
    outdict["datelist"] = datelist
    #print datelist

    #And Nodes
    nodelist = [int(x) for x in wide.index.tolist()]
    outdict["nodelist"] = nodelist

    #And Data
    datalist = wide.values.tolist()
    outdict["data"] = datalist

    #Finally 
    outdict["min"] = int(df["count"].min())
    outdict["max"] = int(df["count"].max())




    #Far to Complex :)
    # #Work out a multiple index
    # multidf = df.set_index(["date", "nodeid"])
    # #Then a panel 
    # thepanel = multidf.to_panel()

    # #Work out which nodes we are dealing with
    # nodelist = [int(x) for x in thepanel.minor_axis.tolist()]
    # datelist = [x.isoformat() for x in thepanel.major_axis.tolist()]

    # #df.to_pickle("data.pkl")
    # #Manually convert JSON 
    # #outlist = [[x[0], x[1].isoformat(), x[2]] for x in qry]
    # outdict = {"nodes":nodelist,
    #            "dates":datelist,
    #            }



    return outdict

    


def getcounts(request):
    """Get a count of the readings for a given node id

    This function will count the number of samples for a given node on each day
    returning these values as a list of [<date> : <count>] pairs

    The function will take an additional parameter (typeid)
    that will filter the response to a specific type of data
    """
    log.debug("{0} Counts Requested {0}".format("-"*20))
    nodeid = request.matchdict.get("id", None)
    log.debug("Node Id is {0}".format(nodeid))

    parameters = request.params
    log.debug("Parameters are {0}".format(parameters))
    typeid = parameters.get("typeid", None)

    qry = DBSession.query(models.Reading,
                        sqlalchemy.func.date(models.Reading.time),
                        sqlalchemy.func.count(models.Reading),
                        ).filter_by(nodeId=nodeid)

    if typeid:
        log.debug("Filter by type id {0}".format(typeid))
        qry = qry.filter_by(typeId=typeid)

    qry = qry.filter(models.Reading.locationId != None)
    qry = qry.group_by(sqlalchemy.func.date(models.Reading.time))
    qry = qry.order_by(sqlalchemy.func.date(models.Reading.time))

    outdata = [[x[1].isoformat(), x[2]] for x in qry]
    #print outdata
    return outdata


 # def getcounts(self, nodeid,
 #                  thesession=MERGE,
 #                  startdate=None,
 #                  enddate=None,
 #                  typeid = None):
 #        """Get daily counts of the number of samples for a given
 #        node.

 #        This function summarises the number of samples each day for a given node
 #        and returns the values as a list of {<date> : <count>} pairs.


 #        :param nodeId: Node Id to get counts for
 #        :param thesession: Which session (MEREGE / MAIN) to get data for
 #        :param startdate: Optional startdate
 #        :param enddate: Optional enddate
 #        :param typeid: Limit to a specific sensor type
 #        :return: List of (<date>, <count>) pairs
 #        """

 #        log = self.log
 #        if thesession == MAIN:
 #            DBSession = self.mainsession()
 #        elif thesession == MERGE:
 #            DBSession = self.mergesession()
 #        else:
 #            log.warning("No Such Session")
 #            return False

 #        #Work out the query
 #        qry = DBSession.query(models.Reading,
 #                            sqlalchemy.func.date(models.Reading.time),
 #                            sqlalchemy.func.count(models.Reading),
 #                            ).filter_by(nodeId=nodeid)
 #        #qry = qry.filter_by(typeId=0) #All nodes have temperature
 #        if startdate:
 #            qry = qry.filter(models.Reading.time >= startdate)
 #        if enddate:
 #            qry = qry.filter(models.Reading.time <= enddate)
 #        if typeid:
 #            qry = qry.filter_by(typeid=typeid)

 #        qry = qry.filter(models.Reading.locationId != None)
 #        qry = qry.group_by(sqlalchemy.func.date(models.Reading.time))
 #        qry = qry.order_by(sqlalchemy.func.date(models.Reading.time))

 #        outdata = [[x[1], x[2]] for x in qry]
 #        return outdata

def filterQuery(theModel, theQuery, params):
    """
    Filter a query object based on user specified parameters

    :var theModel: model object we are mapping this query against
    :var theQuery: sqlalchemy.query object we want to filter_by
    :var parameters: A list of query paramters specified via query string

    :return: Modified sqlalchmey query for these parameters
    """

    log.debug("{0} Params {0}".format("-"*20))
    #log.debug("Query String {0}".format(request.query_string))
    log.debug("{0}".format(params))
    for key, value in params.iteritems():
        log.info("~~~~~~~~ Filter: {0} <{1}> ~~~~~~~~".format(key, value))

        #if theType.lower() == "reading" and key == "typeId"
        if key == "callback":
            continue

        if key.startswith("sort"):
            log.debug("====== SORTED ==========")
            #The Sort string is sort(+<N1>,-<N2>)
            sortKeys = key[5:-1].split(",")
            log.debug("Keys to sort by {0}".format(sortKeys))
            for item in sortKeys:
                item = item.strip()
                sortdesc = False
                if item[0] == "-":
                    item = item[1:]
                    sortdesc = True
                    log.debug("----> Sort Descending {0}".format(item))
                elif item[0] == "+":
                    item = item[1:]
                    log.debug("----> Sort Ascending {0}".format(item))
                else:
                    log.warning("Invalid sort parameter given")

                theColumn = theModel.__table__.columns.get(item)
                log.debug("--> Column Object {0}".format(theColumn))
                if sortdesc:
                    theQuery = theQuery.order_by(theColumn.desc())
                else:
                    theQuery = theQuery.order_by(theColumn)

            return theQuery

        theColumn = theModel.__table__.columns.get(key)
        log.debug("--> Column Object {0}".format(theColumn))
        #theQuery = theQuery.filter(theColumn > value)

        castValue = None

        #Cast datetimes if we need to
        if isinstance(theColumn.type, sqlalchemy.DateTime):
            log.debug("--> Casting Date Times")
            castValue = dateutil.parser.parse(value.split("_")[-1])
            log.debug("--> {0}".format(value))

        if not castValue:
            castValue = value.split("_")[-1]
            if castValue == "None":
                log.debug("Setting None Value")
                #castValue = None
                continue
                #return theQuery

        if value.startswith("le_"):
            #Do Less than or Equal
            #if not castValue:
            #    castValue = value.split("_")[-1]
            log.debug("Filter by {0}<={1}".format(key, castValue))
            theQuery = theQuery.filter(theColumn <= castValue)
            #theQuery = theQuery.filter("{0}<={1}".format(key, castValue))
        elif value.startswith("lt_"):
            #Do Less than or Equal
            #if not castValue:
            #    castValue = value.split("_")[-1]
            log.debug("Filter by {0}<={1}".format(key, castValue))
            theQuery = theQuery.filter(theColumn < castValue)
            #theQuery = theQuery.filter("{0}<={1}".format(key, castValue))
        elif value.startswith("ge_"):
            #Greater than
            #if not castValue:
            #    castValue = value.split("_")[-1]
            log.debug("Filter by {0}>={1}".format(key, castValue))
            theQuery = theQuery.filter(theColumn >= castValue)
            #theQuery = theQuery.filter("{0}>={1}".format(key, castValue))
            pass
        elif value.startswith("gt_"):
            #Greater than
            #if not castValue:
            #    castValue = value.split("_")[-1]
            log.debug("Filter by {0}>={1}".format(key, castValue))
            theQuery = theQuery.filter(theColumn > castValue)
            #theQuery = theQuery.filter("{0}>={1}".format(key, castValue))
            pass
        else:
            #Assume Equality
            #if not castValue:
            #    castValue = value.split("_")[-1]
            log.debug("Filter by {0}={1}".format(key, value))
            #theQuery = theQuery.filter("{0}={1}".format(key, value))
            #Deal with wildcard querys
            if value.count("*") > 0:
                log.debug("--> Wildcard Query !!!")
                if value == "*":
                    #Return Everything
                    log.debug("--> --> Return All")
                    return theQuery
                else:
                    log.debug("--> --> Filter with like {0}".format(value))
                    #Switch * for %
                    value = value.replace("*", "%")
                    theQuery = theQuery.filter(theColumn.like(value))
                    out = theQuery.all()
                    log.debug("--> --> {0}".format(out))
            else:
                theQuery = theQuery.filter(theColumn == castValue)

    return theQuery


#Functionality to return some generic / Sumary information
def summaryRest(request):
    """Deal with fetching generic / suymmary information
    This acts as a focus point to call the _get* functions below
    """
    log.setLevel(logging.DEBUG)
    theId = request.matchdict.get("id", None)
    theType = request.matchdict.get("theType")
    parameters = request.params
    #Get the Method
    reqType = request.method
    #parameters = request.json_body
    log.debug("REST Summary called with params ID: {0} Type: {1} Parameters:{2} Method: {3}".format(theId,
                                                                                                    theType,
                                                                                                    parameters,
                                                                                                    reqType))

    if theType == "register":
        return _getRegistered(theId, parameters, reqType, request)
    elif theType == "status":
        return _getStatus(theId, parameters, reqType, request)
    elif theType == "updateTimes":
        return _updateTimes(theId, parameters, request)
    elif theType == "electric":
        return _getElectric(theId, parameters, reqType, request)
    return []

def _updateTimes(theId, parameters, request):
    log.debug("{0}".format("*"*40))
    log.debug("{0} TIMES {0}".format("-="*15))
    log.debug("{0}".format("*"*40))
    log.debug(parameters)
    #log.debug(request.json_body)


    hId = parameters.get("houseId")
    nId = parameters.get("nodeId")
    lId = parameters.get("locationId")

    log.debug("H: {0}  N: {1} L: {2}".format(hId, nId, lId))

    #Get the House from the database
    theHouse = DBSession.query(models.House).filter_by(id=hId).first()
    log.debug("House {0}".format(theHouse))

    #Then update all samples
    theQry = DBSession.query(models.Reading).filter_by(nodeId=nId)
    theQry = theQry.filter(models.Reading.time >= theHouse.startDate)
    if theHouse.endDate:
        theQry = theQry.filter(models.Reading.time <= theHouse.endDate)

    #unLoc = theQry.filter_by(location=None)

    #newCount = float(unLoc.count())
    oldCount = float(theQry.count())
    #try:
    #    newPc = oldCount / newCount
    #except:
    #    if newCount == 0.0:
    #        newPc = 100.0

    #log.debug("--> Update a total of {0} Readings {1} Without Location ({2})\%".format(oldCount, newCount, newPc))
    log.debug("--> Total Readings to update {0}".format(oldCount))
    #ipt = raw_input("--> IS THIS OK")
    #if ipt == "y":
    log.debug("Updating readings to location id {0}".format(lId))
    theQry.update({"locationId": lId})
    DBSession.flush()
    log.debug("Done")
    #else:
    #    log.debug("Pass")
    #DBSession.commit()
    #log.debug(theQry)


def getStatsGasHour(theQry, daily=False, events=None):
    """Work out hourly / daily electricity use.

    NOTE:  For imperial (ft3) meters only

    :param theQry: SQLA query holding the data
    :param daily:  Generate a daily summary if true, hourly if false
    :param events:  List of events occurring during the monitoring period

    :return: List of dictionary objects referring the the data
    """
    outlist = []

    # to support testing, start by assuming it's a list
    try:
        if len(theQry) == 0:
            return []
    except TypeError:
        if theQry.count() == 0:
            return []

    #Export to Pandas
    df = pandas.DataFrame([{"time":x.time, "value":x.value} for x in theQry])
    #Convert index (as time)
    df.index = df.time

    #Reasample
    resampled = df.resample("5min")
    #And Fill in any gaps
    resampled = resampled.fillna(method="pad")  # removed limit
    #resampled["kW"] = resampled["value"] / 1000.0
    #With gas we convert using the following formula
    #VALUE (in 100's) * M3_conversion * volume_correction * calorific * kWh_conversion
    
    #So first we want the delta between the two
    resampled["delta"] = (resampled["value"] - resampled["value"].shift())

    resampled["kWh"] = resampled["delta"] * GAS_PULSE_TO_METERS * GAS_VOLUME * GAS_COLORIFIC / GAS_CONVERSION
    #We know there is a 5 minute sample period (due to interp)
    #Also as the fomula does conversion the kWh we can ignore time
    #resampled["kWh"] = resampled["kW"] * (5.0/60.0)

    #And Remove Zero Values
    resampled[resampled["kWh"] <= 0] = None


    #print resampled.head()

    #Then do the final resample
    if daily:
        output = resampled.resample("1d", how="sum")
    else:
        output = resampled.resample("1h", how="sum")

    #Prep output for output
    outlist = []
    for item in output.dropna().iterrows():
        outlist.append([item[0], item[1]["kWh"], None])
        #outlist.append([item[0], item[1]["delta"], None])

    return outlist


def getStatsElectricHour(theQry, daily=False, events=None):
    """Work out hourly / Daily electricity use.

    :param theQry: SQLA Query holding the data
    :param daily:  Generate a daily summary if true, hourly if false
    :param events:  List of events occouring during the monitoring period

    :return: List of dictionarry objects refering the the data
    """
    outList = []
    lastHour = None
    lastSample = None
    cumWatts = 0.0

    switchTime = None
    log.debug("Event List {0}".format(events))
    #TODO Fix this to work with other types of event
    if events:
        switchTime = events[0].time
        log.debug("Switch Time {0}".format(switchTime))
    log.debug("Daily Summary Required {0}".format(daily))


    NA = "NA"

    if daily:
        timeCutOff = (60*60)*24
    else:
        timeCutOff = 60*60

    cnt = 0
    #theQry = theQry.limit(500)

    if theQry.count() == 0:
        return []

    #theQry = theQry.limit(5)

    lastitem = None
    cumwatts = 0.0

    #Export to Pandas
    df = pandas.DataFrame([{"time":x.time, "value":x.value} for x in theQry])
    #Convert index (as time)
    df.index = df.time

    #Reasample
    resampled = df.resample("5min")
    #And Fill in any gaps
    resampled = resampled.fillna(method="pad", limit=288)
    resampled["kW"] = resampled["value"] / 1000.0
    #We know there is a 5 minute sample period (due to interp)
    resampled["kWh"] = resampled["kW"] * (5.0/60.0)

    #Then do the final resample
    if daily:
        output = resampled.resample("1d", how="sum")
    else:
        output = resampled.resample("1h", how="sum")

    #Prep output for output
    outlist = []
    for item in output.dropna().iterrows():
        outlist.append([item[0], item[1]["kWh"], None])

    return outlist

def _getElectric(theId, parameters, reqType, request):
    log.setLevel(logging.DEBUG)
    log.debug("==== GETTING ELECTRICITY NODES ====")
    log.debug("Id {0}".format(theId))
    if not theId:
        theId = parameters.get("id", False)
    if not theId:
        return []
    log.debug("Parameters {0}".format(parameters))
    #log.debug("JSON {0}".format(request.json_body))
    daily = parameters.get("daily", False)

    asCsv = parameters.get("csv", False)

    if daily == 'true':
        daily = True
    #elif daily == 'false':
    else:
        daily == False

    log.debug("Daily ?? {0}".format(daily))
    log.debug("CSV {0}".format(asCsv))

    #Id is the house Id

    #Fetch the Electricity data
    elecSensor = DBSession.query(models.SensorType).filter_by(name="Power").first()
    log.debug("Electrity Sensor is {0}".format(elecSensor))

    theHouse = DBSession.query(models.House).filter_by(id=theId).first()
    log.debug("House is {0}".format(theHouse))

    #Location Ids
    locationIds = DBSession.query(models.Location).filter_by(houseId=theHouse.id)
    lIds = []
    for item in locationIds:
        log.debug("Location {0}".format(item))
        lIds.append(item.id)

    theData = DBSession.query(models.Reading).filter_by(typeId=elecSensor.id)
    theData = theData.filter(models.Reading.locationId.in_(lIds))
    log.debug("Number of Samples {0}".format(theData.count()))

    eventQuery = DBSession.query(models.Event).filter_by(houseId=theHouse.id).all()

    hourReadings = getStatsElectricHour(theData, daily, eventQuery)



    if hourReadings is None:
        return []
    if not hourReadings:
        return []

    if asCsv:
        request.override_renderer = "csv"
        dStr = "Hourly"
        if daily:
            dStr = "Daily"

        addStr = theHouse.address.replace(" ", "_")
        fileName = "{0}-{1}.csv".format(addStr, dStr)
        log.debug("Filename: {0}".format(fileName))

        return {"header":["Date", "Reading", "Events"],
                #"rows":[[1, 2], [3, 4]],
                "rows":hourReadings,
                "fName":fileName,
                }


    outReadings = [{"time":time.mktime(x[0].timetuple())*1000,
                    "date":x[0].isoformat(),
                    "kWh":x[1],
                    "event":x[2]} for x in hourReadings]


    log.debug("Done")
    return outReadings


def _getRegistered(theId, parameters, reqType, request):
    log.setLevel(logging.DEBUG)
    log.debug("==== GETTING REGISTERED NODES ====")

    log.debug("--> Paramters {0}".format(parameters))

    houseId = parameters.get("houseId", None)
    #Get Locations associated with this houses
    theHouse = DBSession.query(models.House).filter_by(id=houseId).first()
    log.debug("House Id {0} => {1}".format(houseId, theHouse))

    currenttime = datetime.datetime.utcnow()
    cuttime = currenttime - datetime.timedelta(hours=1)

    #Otherwise Fetch the Base Items
    houseLoc = theHouse.locations
    log.debug("Locations are {0}".format(houseLoc))

    #And the Nodes associated with these locations
    outList = []

    for loc in houseLoc:
        #locNodes = loc.OldNodes
        #locNodes = loc.allnodes
        locNodes = loc.nodes
        #log.debug("Location {0} Nodes {1}".format(loc, locNodes))
        #if locNodes is None:
          #Hunt for locations manually (this should only happen on update)

        for nd in locNodes:
            theItem = {"id": "{0}_{1}".format(nd.id, loc.id),
                       "node":nd.id,
                       "room":loc.room.name,
                       "type":"location",
                       }

            #Status can wait
            readingQry = DBSession.query(models.Reading)
            readingQry = readingQry.filter_by(nodeId=nd.id,
                                              locationId=loc.id)
            readingQry = readingQry.order_by(models.Reading.time)
            count = readingQry.count()
            theItem["totalSamples"] = readingQry.count()
            if count:
                firsttx = readingQry[0].time
                lasttx = readingQry[-1].time
                theItem["firstTx"] = firsttx.isoformat()
                theItem["lastTx"] = lasttx.isoformat()
                if lasttx > cuttime:
                    status = "Good"
                else:
                    status = "Not Reporting"

            else:
                status = "No Data"
            theItem["status"] = status

            #And Battery Levels
            batteryQry = DBSession.query(models.Reading)
            batteryQry = batteryQry.filter_by(nodeId=nd.id,
                                              locationId=loc.id)
            batteryQry = batteryQry.filter_by(typeId=6)
            batteryQry = batteryQry.order_by(models.Reading.time.desc())

            batteryQry = batteryQry.first()
            log.debug("---> BTRY {0}".format(batteryQry))

            if batteryQry is None:
                batLevel = "N/A"
            else:
                batLevel = batteryQry.value
                if batLevel < 2.4:
                    theItem["status"] = "Low Battery"


            theItem["voltage"] = batLevel


            outList.append(theItem)

    return outList



def _getStatus(nodeId, parameters, reqType, request):
    """Get Node Status

    :var parameters: Request.parameters for this query
    :return: List of node Statuses
    """
    log.setLevel(logging.INFO)

    if reqType == "PUT":
        #Add / Update the Item
        log.debug("PUT Request")
        log.debug(parameters)
        log.debug(request.json_body)

        jsonBody = request.json_body

        #The only thing we can do is update the Location
        nid = jsonBody["node"]
        rName = jsonBody["newRoom"]
        hid = jsonBody["houseId"]

        theNode = DBSession.query(models.Node).filter_by(id=nid).first()
        log.debug("--> Node {0}".format(theNode))

        theRoom = DBSession.query(models.Room).filter_by(name=rName).first()
        log.debug("Room from Query {0}".format(theRoom))
        if theRoom is None:
            theRoom = models.Room(name=rName)
            DBSession.add(theRoom)
            DBSession.flush()
        log.debug("--> Final Room {0}".format(theRoom))

        #Then Get the Location
        theLoc = DBSession.query(models.Location).filter_by(houseId=hid,
                                                          roomId=theRoom.id).first()
        if theLoc is None:
            log.info("== Adding Location")
            theLoc = models.Location(houseId=hid,
                                     roomId=theRoom.id)
            DBSession.add(theLoc)
            DBSession.flush()

        log.debug("--> Final Location {0}".format(theLoc))

        theNode.locationId = theLoc.id
        DBSession.flush()

        jsonBody["newRoom"] = None
        jsonBody["currentRoom"] = rName
        jsonBody["currentHouse"] = theLoc.house.address
        return jsonBody

        pass

    elif reqType == "GET":
        #log.setLevel(logging.WARNING)
        outList = []

        log.debug("Nodes we have heard from")

        houseId = parameters.get("houseId", None)
        cutTime = parameters.get("cutTime", None)


        heardQuery = DBSession.query(sqlalchemy.distinct(models.NodeState.nodeId))

        if cutTime:
            cutTime = datetime.datetime.utcnow() - datetime.timedelta(days=int(cutTime))
            log.info("== Processing Cuttof Time {0}".format(cutTime))
            heardQuery = heardQuery.filter(models.NodeState.time >= cutTime)

        heardNodes = [x[0] for x in heardQuery]

        #if houseId:
        #    theQry = theQry.filter_by(houseId=houseId)
        #    log.debug("Search for locations associated with House {0}".format(houseId))

        #Get Type Id for Battery
        batteryType = DBSession.query(models.SensorType).filter_by(name="Battery Voltage").first()
        log.debug("==== Battry Type {0}".format(batteryType))

        for node in heardNodes:
            log.debug("Deal with Node: {0}".format(node))
            #lastTime = DBSession.query(models.NodeState).filter_by(nodeId=node)
            lastTime = DBSession.query(models.NodeState)#.join(models.Node)
            lastTime = lastTime.filter(models.NodeState.nodeId==node)

            lastTime = lastTime.order_by(models.NodeState.time.desc()).first()



            #out=lastTime.first()
            #log.debug("--> {0}".format(out))
            #I can now add those to a list
            #log.info("---- ITEM {0}, {1}, Node {2}".format(lastTime, lastTime.nodeId, lastTime.node))

            #We want to check if the node exists
            if lastTime.node is None:
                log.warning("Node {0} doesn't exist but has a location".format(lastTime.nodeId))
                #It may be a good idea to create item
                theNode = models.Node(id=lastTime.nodeId,
                                      location=None,
                                      nodeTypeId=None)
                DBSession.merge(theNode)
                DBSession.flush()
                theLoc = None
            else:
                theLoc = lastTime.node.location

            if houseId:
                if not theLoc:
                    continue
                log.debug("Filter by House Id {0}, theLoc {1}".format(houseId,
                                                                      theLoc.house.id))
                if theLoc.house.id != int(houseId):
                    log.debug("Ignoring")
                    continue




            theItem = {"id":lastTime.nodeId,
                       "node":lastTime.nodeId,
                       "lastTx":lastTime.time.isoformat(),
                       }

            #And Get the most Recent Battry Level
            lastBattery = DBSession.query(models.Reading).filter_by(time=lastTime.time,
                                                                  nodeId=node,
                                                                  typeId=batteryType.id)
            lastBattery = lastBattery.first()
            #log.debug("--- Last Batt {0}".format(lastBattery))


            if lastBattery:
                theItem["voltage"] = lastBattery.value
            else:
                theItem["voltage"] = None

            if theLoc:
                theItem["currentHouse"] = theLoc.house.address
                theItem["houseId"] = theLoc.house.id
                theItem["currentRoom"] = theLoc.room.name
            log.debug("--> Item {0}".format(theItem))

            #Finally work out the Status
            timeDiff = datetime.datetime.utcnow() - lastTime.time
            #log.debug("--> {0}".format(timeDiff))

            if theLoc:
                theItem["status"] = "Good"
                if timeDiff.days > 0:
                    theItem["status"] = "Not Reporting"
            else:
                theItem["status"] = "Unregistered"
                #if timeDiff.days > 0:
                #    theItem["status"] = "Not
                #continue
            outList.append(theItem)

        for item in outList:
            log.debug("--> {0}".format(item))

        return outList
    else:
        log.warning("REQUEST TYPE NOT CATERED FOR {0}".format(reqType))
        return


    #return outList

def restTest2(request):
    """Function to count samples gathered by a node"""
    import time
    log.debug(request.matchdict)
    log.debug("Params {0}".format(request.params))
    nodeId = request.matchdict.get("id", None)


    if nodeId == "":
        #Or we can fetch the item from the parameters
        nodeId = request.params.get("id", None)
        if not nodeId:
            nodeId = 133
    log.debug("Id is {0}".format(nodeId))





    #Run the Query
    theQry = DBSession.query(models.NodeState, sqlalchemy.func.count(models.NodeState)).filter_by(nodeId=nodeId)
    theQry = theQry.group_by(sqlalchemy.func.date(models.NodeState.time))
    dataCount = theQry.count()
    #theQry = theQry.limit(5)
    outList = [{"x":time.mktime(item[0].time.date().timetuple()),
                "value":item[1]} for item in theQry]

    return outList

def _getReadingCount(locationId):
    theQry = DBSession.query(models.Reading,
                           sqlalchemy.func.count(models.Reading)).filter_by(locationId=locationId)
    theQry = theQry.group_by(models.Reading.typeId)

    outItems = []
    for item in theQry:

        theItem = {"name":item[0].sensorType.name,
                   "size":item[1]}
        outItems.append(theItem)
    return outItems

def restTest(request):

    baseItem = {"name":"Database"}
    baseChildren = []


    deployments = DBSession.query(models.Deployment)

    for deployment in deployments:
        thisDeployment = {"name":deployment.name}

        houses = []
        #Houses
        for house in deployment.houses:
            thisHouse = {"name":house.address,
                           "children":[]}


            for location in house.locations:
                thisLocation = {"name":location.room.name,
                                "children":[]}

                readCount = _getReadingCount(location.id)
                thisLocation["children"].extend(readCount)

                thisHouse["children"].append(thisLocation)

            houses.append(thisHouse)

        thisDeployment["children"] = houses

        baseChildren.append(thisDeployment)

    #And houses without a deployment



    noDeployments = {"name":"No Deployment",
                     "children":[]}


    houseQry = DBSession.query(models.House).filter_by(deploymentId=None)
    houses = []
    for house in houseQry:
        thisHouse = {"name":house.address,
                     "children":[]}

        for location in house.locations:
            thisLocation = {"name":location.room.name,
                            "children":[]}

            readCount = _getReadingCount(location.id)
            thisLocation["children"].extend(readCount)
            thisHouse["children"].append(thisLocation)

        houses.append(thisHouse)

    noDeployments["children"] = houses

    #Readings without a Location
    noLocation = {"name":"No Location",
                  "children":[]}

    readCount = _getReadingCount(None)
    noLocation["children"].extend(readCount)


    noHouse = {"name":"No House",
               "children":[noLocation]}

    noDeployments["children"].append(noHouse)



    baseChildren.append(noDeployments)

    baseItem["children"] = baseChildren
    # #And houses without deployment
    # noDeployments = {"name":"No Deployment"}

    # outList.append(noDeployments)

    #import pprint
    #pprint.pprint(baseItem)
    return baseItem

def lastnodesync(request):
    """Fetch the last sample in the database for a given node

    :return: either the date of the last sample or None
    """

    nodeid = request.matchdict.get("id", None)
    log.debug("---- NODE ID >{0}< {1} {2}".format(nodeid,
                                                  type(nodeid),
                                                  nodeid == ""))
    if (nodeid == u'') or (nodeid is None):
        log.debug("Trying Parameters")
        nodeid = request.params.get("node", None)

    log.debug("---- NODE ID >{0}< {1} {2}".format(nodeid,
                                                  type(nodeid),
                                                  nodeid == ""))

    if not nodeid:
        log.debug("Exiting")
        return None

    qry = DBSession.query(sqlalchemy.func.max(models.Reading.time))
    qry = qry.filter_by(nodeId=nodeid).first()[0]
    #print "{0} {1} {0}".format("="*30, qry)
    if qry is not None:
        return qry.isoformat()
    return None




def lastSync(request):
    """
    Fetch the last sample in the database for a given house

    This will search the database for the last sample associated with
    a given house address and return its date as an isoformatted json object.

    The house address is expected to be encoded as part of the
    request parameters

    :return: Either the date of the last sample or None
    """

    housename = request.params.get("house", None)

    log.info("Fetching last Sample for house >{0}<".format(housename))

    if housename is None:
        return None

    thishouse = DBSession.query(models.House).filter_by(address=housename).first()
    log.debug("House is: {0}".format(thishouse))

    if thishouse is None:
        return None

    #Not Optimal Query But what the Hell
    loc_query = thishouse.locations
    locIds = [x.id for x in thishouse.locations]

    reading_query = DBSession.query(sqlalchemy.func.max(models.Reading.time))
    reading_query = reading_query.filter(models.Reading.locationId.in_(locIds))

    reading_query = reading_query.first()[0]
    log.debug("Result is {0}".format(reading_query))
    if reading_query is not None:
        return reading_query.isoformat()
    else:
        return reading_query


def getnetwork(request):
    """Return a simple network map"""

    """Data structure should be something like
    { "nodes" : [ {"name":x, ...},]
      "links" : [ {"source": "id_1" , "target" : "id_2"}]
    }
    """

    #Get our nodelist
    nodeqry = DBSession.query(models.Node)

    nodelist = [{"name":"Base",
                 "count":0,
                 "id":0,
                 "depth":0}
                ]
    linklist = []

    graphtype = "current"

    #For Every node in the simulation
    for node in nodeqry:


        
        #Work out the links between each node (FOR ALLL)
        if graphtype == "all":
            qry = DBSession.query(models.NodeState,
                                sqlalchemy.func.count(models.NodeState.nodeId))
            qry = qry.filter_by(nodeId=node.id)
            qry = qry.group_by(models.NodeState.parent)
        #TODO (Add filters by time here)

        if graphtype == "current":
            qry = DBSession.query(models.NodeState,
                                sqlalchemy.func.count(models.NodeState.nodeId))
            qry = qry.filter_by(nodeId=node.id)
            qry = qry.filter(models.NodeState.time >= (datetime.datetime.utcnow() - datetime.timedelta(minutes=7)))
            qry = qry.order_by(models.NodeState.time.desc())

            qry = qry.limit(1)

        statecount = 0

        for state in qry:
            if state[0] is None:
                log.debug("No Nodestate for Id {0}".format(node.id))
                continue
            statecount += state[1]
            #We need to stick a guard in here for 4252
            if state[0].parent == 4252:
                continue

            linklist.append({"source":node.id,
                             "target":state[0].parent,
                             "type": "path",
                             "count":state[1]}
                            )

            #And any visable neigbors
            qry = DBSession.query(models.Reading).filter_by(nodeId=node.id,
                                                          time=state[0].time)
            #And show neigbors
            qry = qry.filter(models.Reading.typeId >= 2000)
            qry = qry.filter(models.Reading.typeId <= 2006)
            for neighbor in qry:
                log.debug("Neighbor is {0}".format(neighbor))
                # linklist.append({"source":node.id,
                #                  "target":neighbor.value,
                #                  "type": "neighbor",
                #                  "count": 0})
            
            #I also want the average depth of the node
            qry = DBSession.query(sqlalchemy.func.avg(models.Reading.value)).filter_by(nodeId=node.id)
            qry = qry.filter_by(typeId=1001) #MAGIC No

            avgdepth = qry.first()
            if avgdepth[0] is None:
                avgdepth = 0
            else:
                avgdepth = avgdepth[0] + 1

    
            nodelist.append({"name": "{0}".format(node.id, state[0].time),
                             "count":statecount,
                             "id":node.id,
                             "depth":avgdepth})

    return {"nodes":nodelist,
            "links":linklist}


def getschema(request):
    """Get schema information for a given server"""

    theserver = request.params.get("server", None)
    log.debug("Requesting schema for server {0}".format(theserver))
    
    theschema = {}
    qry = DBSession.query(models.Server).filter_by(hostname = theserver)
    theserver = qry.first()
    if theserver is None:
        return []
    log.debug("Database server is {0}".format(theserver))

    now = datetime.datetime.utcnow()
    qry = DBSession.query(models.House).filter_by(serverid=theserver.id)
    qry = qry.filter(sqlalchemy.or_(models.House.endDate==None,
                                    models.House.endDate<=now))
    houses = qry.all()
    theschema["houses"] = [x.json() for x in houses]

    locations = []
    for item in houses:
        locations.extend(item.locations)
    theschema["locations"] = [x.json() for x in locations]

    nodes = []
    for item in locations:
        nodes.extend(item.nodes)
    theschema["nodes"] = [x.json() for x in nodes]
        

    return theschema


def getenergy(request):
    """Get energy use information for a given node"""

    #Stuff needed for Query
    nodeid = request.params.get("nodeId", None)
    typeid = request.params.get("type", "electric")
    startdate = request.params.get("startdate", None)
    if startdate:
        startdate = dateutil.parser.parse(startdate)
    enddate = request.params.get("enddate", None)
    if enddate:
        enddate = dateutil.parser.parse(enddate)
        enddate = enddate + datetime.timedelta(days = 1)

    #Stuff for processing (ie hourly data) default to daily if this is none
    daily = request.params.get("daily", False)

    log.debug("Getting Energy Summary for Node {0} ({1})".format(nodeid, daily))

    if typeid == "electric":
        #Process electric data
        #Electricity sensor
        qry = DBSession.query(models.SensorType).filter_by(name="Power")
        thesensor = qry.first()
        log.debug("Electricty Sensor {0}".format(thesensor))
    elif typeid == "gas":
        qry = DBSession.query(models.SensorType).filter_by(name="Gas Pulse Count")
        thesensor = qry.first()
        log.debug("Gas Sensor {0}".format(thesensor))


    #Fetch the readings
    qry = DBSession.query(models.Reading).filter_by(typeId=thesensor.id)
    qry = qry.filter_by(nodeId=nodeid)
    if startdate:
        qry = qry.filter(models.Reading.time >= startdate)
    if enddate:
        qry = qry.filter(models.Reading.time <= enddate)
    log.debug("Number of samples {0}".format(qry.count()))


    qry = qry.order_by(models.Reading.time)

    #Process the reading by type
    if typeid == "electric":
        processed = getStatsElectricHour(qry, daily, None)
    elif typeid == "gas":
        processed = getStatsGasHour(qry, daily, None)
    else:
        processed = []

        #Convert for output
    outreadings = [{"time":x[0].isoformat(),
                    "kWh": x[1]}
                   for x in processed]
    return outreadings

def getsummary(request):
    """Get summary information for a given node

    Return daily [min, max, avg] for a given
    * nodeId
    * sensorTypeId (ie 0 for temperature)
    * start / end date.
    """

    nodeid = request.params.get("nodeId", None)
    typeid = request.params.get("typeId", 0)
    startdate = request.params.get("startdate", None)
    if startdate:
        startdate = dateutil.parser.parse(startdate)
    enddate = request.params.get("enddate", None)
    if enddate:
        enddate = dateutil.parser.parse(enddate)
        enddate = enddate + datetime.timedelta(days = 1)

    log.debug("Getting Summary Information for node {0}".format(nodeid))

    if nodeid is None:
        log.debug("No Node Id supplied")
        return []
    
    qry = DBSession.query(sqlalchemy.func.date(models.Reading.time),
                        sqlalchemy.func.min(models.Reading.value),
                        sqlalchemy.func.max(models.Reading.value),
                        sqlalchemy.func.avg(models.Reading.value)
                    ).filter_by(nodeId=nodeid,
                                typeId=typeid)
    if startdate:
        qry = qry.filter(models.Reading.time >= startdate)
    if enddate:
        qry = qry.filter(models.Reading.time <= enddate)

    qry = qry.group_by(sqlalchemy.func.date(models.Reading.time))

    if qry.count > 0:
        return [{"date":x[0].isoformat(),
                 "dom": x[0].strftime("%d"),
                 "min": x[1], 
                 "max": x[2],
                 "avg": x[3]} for x in qry]

    return []

def gettopology(request):
    """Work out network topology changes"""

    #All Nodes
    nodeqry = DBSession.query(models.Node)
    
    startdate = None
    enddate = None

    nodelist = []
    changedict = {} #Dictionary object to hold all changes
    log.debug("--- Node List ---")
    for node in nodeqry[:2]:
        log.debug(node)


        #Check for dates with more than one parent
        parentqry = DBSession.query(models.NodeState,
                                  sqlalchemy.func.count(models.NodeState.nodeId),
                                  sqlalchemy.func.count(sqlalchemy.func.distinct(models.NodeState.parent)),
                                  ).filter_by(nodeId=node.id)
        parentqry = parentqry.group_by(sqlalchemy.func.date(models.NodeState.time))

        changes = []

        
        lastparent = None
        for item in parentqry:
            if item[2] == 1:
                if startdate is None:
                    startdate = item[0].time
                    enddate = item[0].time
                elif item[0].time < startdate:
                    startdate = item[0].time
                elif item[0].time > enddate:
                    enddate = item[0].time
                    
                currentparent = item[0].parent
                if (lastparent is None) or (lastparent != currentparent):
                    lastparent = currentparent
                    log.info("Change Triggered {0}".format(item))
                    changes.append([str(item[0].time.date()), item[0].parent])

                    ditem = changedict.get(item[0].time.date().isoformat(), [])
                    #print "-->", ditem
                    #ditem.append({"id":item[0].nodeId, "parent":item[0].parent, "date":item[0].time.date().isoformat()})
                    ditem = {"id":item[0].nodeId, "parent":item[0].parent, "date":item[0].time.date().isoformat()}
                    changedict[item[0].time.date().isoformat()] = ditem
                # elif lastparent != currentparent:
                #     lastparent = currentparent
                #     log.info("Toplology change")
                #     changes.append([str(item[0].time.date()), item[0].parent])
            else:
                #We have multiple parents
                subquery = DBSession.query(models.NodeState).filter_by(nodeId=node.id)
                subquery = subquery.filter(sqlalchemy.func.date(models.NodeState.time) == item[0].time.date())
                #print subquery.all()
                for subitem in subquery:
                    currentparent = subitem.parent
                    if (lastparent is None) or (lastparent != currentparent):
                        lastparent = currentparent
                        log.info("Sub Data change triggered ")
                        changes.append([str(subitem.time), subitem.parent])
                        ditem = changedict.get(item[0].time.isoformat(), [])
                        #ditem.append({"id":item[0].nodeId, "parent":item[0].parent, "date":item[0].time.isoformat()})
                        ditem = {"id":item[0].nodeId, "parent":item[0].parent, "date":item[0].time.isoformat()}
                        changedict[item[0].time.isoformat()] = ditem

                    #or (lastparent != currentparent):
                    
                    #lastparent = currentparent
                #changes.append([str(item[0].time.date()), item[0].parent])


                
        #changes = [(str(x[0].time), x[1], x[2]) for x in parentqry]

        #changes = [(str(x[0].time),x[1], x[2]) for x in parentqry]

        nodelist.append({"node":node.id, "changes":changes})

    return {"startdate": (startdate - datetime.timedelta(days=7)).isoformat(),
            "enddate": enddate.isoformat(),
            "nodes":nodelist,
            "topolo": changedict}
