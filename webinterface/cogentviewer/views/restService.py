"""
Class to deal with REST Requests


"""

from pyramid.response import Response
from pyramid.renderers import render_to_response
import pyramid.url

import cogentviewer.models.meta as meta
import cogentviewer.models as models

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

#import sqlalchemy.orm.mapper
import sqlalchemy
import dateutil.parser

import datetime
import time


def _getDeploymentTree(request):
    """Fetch a tree to be used for navigation"""
    session = meta.Session()

    #Fetch a list of deployments

    params = request.params

    if params:
        log.debug("Query parameters {0}".format(params))
        parent = params.get("parent",None)
        log.debug("Looking for parent {0}".format(parent))
        if parent:
            depSplit = parent.split("_")

            if parent == "root":
                theQry = session.query(models.Deployment)
                outList = []
                for item in theQry:
                    log.debug("Processing {0} ".format(item))
                    outList.append({"id":"d_{0}".format(item.id),
                                    "name":item.name,
                                    "parent":"root",
                                    "type":"deployment"
                                    })
                return outList
            elif depSplit[0] == "d":
                log.debug("Parent is a Deployment")
                theQry = session.query(models.House).filter_by(deploymentId = depSplit[1])
                outList = []
                for item in theQry:
                    outList.append({"id":"h_{0}".format(item.id),
                                    "name":item.address,
                                    "parent":"d_{0}".format(depSplit[1]),
                                    "type":"house",
                                    }
                                   )
                return outList
            elif depSplit[0] == "h":
                log.debug("Parent is a House")
                theQry = session.query(models.Location).filter_by(houseId = depSplit[1])
                log.debug("--- {0} {1}".format(theQry,theQry.count()))
                outList = []
                for item in theQry:
                    log.debug("----> {0}".format(item))
                    #if len(item.readings) > 0:
                    if item:
                        outList.append({"id":"l_{0}".format(item.id),
                                        "name":"({0}) {1}".format(item.id,item.room.name),
                                        "parent":"h_{0}".format(depSplit[1]),
                                        "type":"location",
                                        }
                                       )
                return outList

            elif depSplit[0] == "l":
                log.debug("Parent is a Location")
                outList = []
                
                theQry = session.query(sqlalchemy.distinct(models.Reading.typeId)).filter_by(locationId = depSplit[1])
                for item in theQry:
                    log.info("Distinct Sensor Type {0}".format(item))
                    sType = session.query(models.SensorType).filter_by(id=item[0]).first()
                    if sType is None:
                        log.warning("Sensor Type {0} Doesnt Exist".format(item))
                        theItem = {"id":"t_{0}_{1}".format(depSplit[1],item[0]),
                                   "name":"Unknown Type ({0})".format(item[0]),
                                   "type":"sensorType",
                                   "parent":"l_{0}".format(depSplit[1]),
                                   }
                    else:
                        theItem = {"id":"t_{0}_{1}".format(depSplit[1],item[0]),
                                   "name":sType.name,
                                   "type":"sensorType",
                                   "parent":"l_{0}".format(depSplit[1]),
                                   }
                    outList.append(theItem)
                    log.debug(theItem)

                #By Node (But I dont need to do that)
                # locQry = session.query(models.Location).filter_by(id = depSplit[1])
                # for item in locQry:
                #     log.debug("Location is {0} -> {1}".format(item,item.OldNodes))
                    
                    #for node in item.OldNodes:
                    #    outList.append({"id":"n_{0}".format(node.id),
                    #                    "name":node.id,
                    #                    "parent":"l_{0}".format(depSplit[1]),
                    #                    "type":"node"})

                return outList
            # return [
            #     {"id":"withdep","name":"Deployments","parent":"root"},
            #     {"id":"nodep","name":"dep 2","parent":"root"},
            #     ]
        #else:
        return []
    else:
        log.debug("Returning All Object")
        outList = [
            {"id":"root","name":"All Deployments"},
            #{"id":"d1","name":"dep 1","parent":"root"},
            #{"id":"d2","name":"dep 2","parent":"root"},
            ]
        return outList


    log.debug("Query Returns {0}".format(outList))
    return outList

def genericRest(request):
    #Create a session
    session = meta.Session()
    
    log.debug("="*80)
    #Fetch all the deployments
    #theQuery = session.query(models.Deployment)
    #deployments = [x.toREST() for x in theQuery]
   

    #Get the Method
    reqType = request.method

    theId = request.matchdict.get("id",None)
    theType = request.matchdict.get("theType")
    log.debug("Request Type {0} Request Id: {1}".format(reqType,theId))
    log.debug("Object Type {0}".format(theType))

    if theType.lower() == "lastsync":
        return lastSync(request)

    #Deal with "BULK" uploads
    if theType.lower() == "bulk":
        log.debug("BULK UPLOAD")
        parameters = request.json_body
        #log.debug(parameters)
        objGen = models.clsFromJSON(parameters)
        import time
        t1 = time.time()
        for item in objGen:
            session.add(item)
            #session.merge(item)
        #session.flush()
        log.debug("Items Added")
        try:
            session.flush()
        #except sqlalchemy.IntegrityError,e:
        except Exception,e:
            log.warning("Bulk Upload Error")
            log.warning(e)
            request.response.status = 404
            return ["Error: {0}".format(e)]
        
        t2 = time.time()
        log.debug("========= TIME {0}".format(t2-t1))
        #print "="*70
        #print [x.id for x in objGen]
        #print "="*70
        request.response.status = 201 
        log.debug("Bulk Upload Success")
        #session.commit()
        #session.close()
        return []
        #return [x.id for x in objGen]
    elif theType.lower() == "deploymenttree":
        log.debug("Deployment Tree")
        return _getDeploymentTree(request)
        #return []




    #Deal with ranges
    reqRange = request.headers.get("Range",None)
    log.debug("STD Range {0}".format(request.range))
    log.debug("Range ? {0}".format(reqRange))
    if reqRange:
        try:
            reqRange = [int(x) for x in reqRange.split("=")[-1].split("-")]
        except:
            log.warning("Error Parsing supplied range {0}".format(reqRange))
            reqRange = None
    #log.debug(reqRange)
    #print request
              

    #Mapping between types and classes. (We may be able to infer this from the mapper)
    typeMap = {"deployment":models.Deployment,
               "house":models.House,
               "reading":models.Reading,
               "node":models.Node,
               "room":models.Room,
               "roomtype":models.RoomType,
               "location":models.Location,
               "sensortype":models.SensorType}
    theModel = typeMap[theType.lower()]

    if reqType == "GET":
        #Create Query
        theQuery = session.query(theModel)
        #If we have an Id filter by that
        log.debug("Get Query")
        if theId:
            log.debug("Filter by Id {0}".format(theId))
            theQuery = theQuery.filter_by(id = theId)

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
            theQuery = filterQuery(theModel,theQuery,params)


        if reqRange:
            log.debug("===== RANGE SPECIFIED:")
            theQuery = theQuery.offset(reqRange[0])#.limit(reqRange[1]-reqRange[0])
            theLimit = reqRange[1] - reqRange[0]
            log.debug("Limit {0}".format(theLimit))
            #theQuery = theQuery.filter(theModel.id >= reqRange[0],
            #                           theModel.id <= reqRange[1])
            secondCount = theQuery.count()
            theQuery = theQuery.limit(theLimit)
            #And set a response type
            request.response.content_range = "items {0}-{1}/{2}".format(reqRange[0],reqRange[0]+secondCount,totalCount)


        #return theModel.__table__


        retItems = [x.toDict() for x in theQuery]
        if retItems:
            log.debug("--> ITEMS --> {0}".format(retItems[0]))
        #session.close()
        return retItems

    elif reqType == "POST":
        #POST is used for new items
        parameters = request.json_body
        log.debug(parameters)

        newObj = theModel()
        newObj.fromJSON(parameters)
        
        session = meta.Session()
        session.add(newObj)
        session.flush()
        #session.commit()
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

        #And Return the new object

        retObj =  newObj.toDict()
        session.flush()
        #session.close()        
        return retObj

    elif reqType == "PUT":
        #Add (or modify) an item based on parameters encoded in request body

        #PUT is used to update
        log.setLevel(logging.DEBUG)
        log.debug("PUT: {0}".format(reqType))
        log.debug("QUERY STRING {0}".format(request.query_string))
        log.debug("BODY {0}".format(request.body))
                  
        #session = meta.Session()

        queryParams = request.params
        log.debug("PARAMS --> {0}".format(queryParams))
        #If we have an Id, Assume we want to try to update an existing object
        theQuery = session.query(theModel)
        if theId:
            theQuery = theQuery.filter_by(id=theId)#.first()
            log.debug("--> Query Results on search for {0}".format(theId))
        elif queryParams:
            log.debug("--> Attempt to add new object based on search")
            print queryParams
            theQuery = filterQuery(theModel,theQuery,queryParams)

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
            #newObj.fromJSON(parameters)
            session.add(theQuery)
            session.flush()
            #return []
            #session.add(theQuery)
            
        parameters = request.json_body
        log.debug("JSON PARAMS {0}".format(parameters))
        
        
        log.debug("--> Orig {0}".format(theQuery))
        #And then Update
        theQuery.fromJSON(parameters)
        
        session.flush()
                 
        log.debug("--> New {0}".format(theQuery))


        #Set the Response "Location" field to the item URL (REST GET)
        #request.response.location = "http://127.0.0.1:6543/rest/deployment{0}/".format(newObject.Id)
        #Deal with corner case for readings
        if theType.lower() == "reading": 
            responseUrl = request.route_url("genericRest",theType=theType,id=None)
        else:
            responseUrl = request.route_url("genericRest",theType=theType,id=theQuery.id)

        request.response.location = responseUrl
        #And Set the Response status to 201 Created
        request.response.status = 201


        #And Return the new object
        retObj =  theQuery.toDict()
        log.setLevel(logging.INFO)
        #session.close()
        return retObj


    #    pass
    elif reqType == "DELETE":
        #Return a response of 204 indicating item deleted.
        log.debug("Deleting Item with Id of {0}".format(theId))
        #session = meta.Session()

        #We need to do some special processing to remove certain types of items
        log.debug("---- ITEM TYPE {0}".format(theType))
        if theType == "house":
            #Do some special house removing
            
            #Find all locations attached to this houses
            theHouse = session.query(theModel).filter_by(id=theId).first()
            if theHouse is None:
                return

            locQry = session.query(models.Location).filter_by(houseId = theHouse.id)
            
            log.debug("House is {0}  Locations are {1}".format(theHouse,theHouse.locations))
            
            #Reset the readings to have a null location
            for loc in locQry:
                theQry = session.query(models.Reading).filter_by(locationId = loc.id)
                #loc.oldNodes = []
                log.debug("Processing Location {0}: {1} Readings Found".format(loc,theQry.count()))
                theQry.update({"locationId": None})
                
                #And Reset the other associated stuff
                log.debug("Old Nodes {0}".format(loc.OldNodes))
                del(loc.OldNodes)
                #loc.Node.locationId = None
                for item in loc.nodes:
                    item.locationId = None

            #Then we can remove the locations
            locQry = session.query(models.Location).filter_by(houseId=theHouse.id)
            locQry.delete()

            theHouse = session.query(theModel).filter_by(id=theId)
            theHouse.delete()


        if theId:
            theQuery = session.query(theModel).filter_by(id=theId)
            deleteCount = 0
            if theQuery.count() > 0:
                deleteCount = theQuery.delete()

        log.debug("{0} Items deleted".format(deleteCount))
        if deleteCount > 0:
            request.response.status = 204
        #Otherwise I expect there should be an error somewhere
        pass
    else:
        #Panic and throw an error.
        pass

        #session.close()


def filterQuery(theModel,theQuery,params):
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
    for key,value in params.iteritems():
        log.info("~~~~~~~~ Filter: {0} <{1}> ~~~~~~~~".format(key,value))

        #if theType.lower() == "reading" and key == "typeId"

        if key.startswith("sort"):
            log.debug("====== SORTED ==========")
            #The Sort string is sort(+<N1>,-<N2>)
            sortKeys = key[5:-1].split(",")
            log.debug("Keys to sort by {0}".format(sortKeys))
            for item in sortKeys:
                item = item.strip()
                sortdesc = False
                if item[0]=="-":
                    item = item[1:]
                    sortdesc = True
                    log.debug("----> Sort Descending {0}".format(item))
                else:
                    log.debug("----> Sort Ascending {0}".format(item))
            
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
        if isinstance(theColumn.type,sqlalchemy.DateTime):
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
            log.debug("Filter by {0}<={1}".format(key,castValue))
            theQuery = theQuery.filter(theColumn <= castValue)
            #theQuery = theQuery.filter("{0}<={1}".format(key,castValue))
        elif value.startswith("lt_"):
            #Do Less than or Equal
            #if not castValue:
            #    castValue = value.split("_")[-1]
            log.debug("Filter by {0}<={1}".format(key,castValue))
            theQuery = theQuery.filter(theColumn < castValue)
            #theQuery = theQuery.filter("{0}<={1}".format(key,castValue))
        elif value.startswith("ge_"):
            #Greater than
            #if not castValue:
            #    castValue = value.split("_")[-1]
            log.debug("Filter by {0}>={1}".format(key,castValue))
            theQuery = theQuery.filter(theColumn >= castValue)
            #theQuery = theQuery.filter("{0}>={1}".format(key,castValue))
            pass
        elif value.startswith("gt_"):
            #Greater than
            #if not castValue:
            #    castValue = value.split("_")[-1]
            log.debug("Filter by {0}>={1}".format(key,castValue))
            theQuery = theQuery.filter(theColumn > castValue)
            #theQuery = theQuery.filter("{0}>={1}".format(key,castValue))
            pass
        else:
            #Assume Equality
            #if not castValue:
            #    castValue = value.split("_")[-1]
            log.debug("Filter by {0}={1}".format(key,value))
            #theQuery = theQuery.filter("{0}={1}".format(key,value))
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
                    value = value.replace("*","%")
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
    theId = request.matchdict.get("id",None)
    theType = request.matchdict.get("theType")
    parameters = request.params
    #Get the Method
    reqType = request.method
    #parameters = request.json_body
    log.debug("REST Summary called with params ID: {0} Type: {1} Parameters:{2} Method: {3}".format(theId,theType,parameters,reqType))



    if theType == "register":
        return _getRegistered(theId,parameters,reqType,request)
    elif theType == "status":
        return _getStatus(theId,parameters,reqType,request)
    elif theType == "updateTimes":
        return _updateTimes(theId,parameters,request)
    elif theType == "electric":
        return _getElectric(theId,parameters,reqType,request)
    return []

def _updateTimes(theId,parameters,request):
    log.debug("{0}".format("*"*40))
    log.debug("{0} TIMES {0}".format("-="*15))
    log.debug("{0}".format("*"*40))
    log.debug(parameters)
    #log.debug(request.json_body)

    session = meta.Session()

    hId = parameters.get("houseId")
    nId = parameters.get("nodeId")
    lId = parameters.get("locationId")

    log.debug("H: {0}  N: {1} L: {2}".format(hId,nId,lId))

    #Get the House from the database
    theHouse = session.query(models.House).filter_by(id=hId).first()
    log.debug("House {0}".format(theHouse))

    #Then update all samples
    theQry = session.query(models.Reading).filter_by(nodeId=nId)
    theQry = theQry.filter(models.Reading.time >= theHouse.startDate)
    if theHouse.endDate:
        theQry = theQry.filter(models.Reading.time <= theHouse.endDate)

    #unLoc = theQry.filter_by(location = None)
    
    #newCount = float(unLoc.count())
    oldCount = float(theQry.count())
    #try:
    #    newPc = oldCount / newCount
    #except:
    #    if newCount == 0.0:
    #        newPc = 100.0
    
    #log.debug("--> Update a total of {0} Readings {1} Without Location ({2})\%".format(oldCount,newCount,newPc))
    log.debug("--> Total Readings to update {0}".format(oldCount))
    #ipt = raw_input("--> IS THIS OK")
    #if ipt == "y":
    log.debug("Updating readings to location id {0}".format(lId))
    theQry.update({"locationId": lId})
    session.flush()
    log.debug("Done")
    #else:
    #    log.debug("Pass")
    #session.commit()
    #log.debug(theQry)
    #session.close()


def getStatsElectricHour(theQry,daily=False,events = None):
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
        return False

    for item in theQry:
        #log.debug(item)
        theTime = item.time
        value = item.value

        #TODO: FIX THIS TOO
        descrip = "PRE"
        if switchTime:
            if theTime > switchTime:
                descrip = "POST"
            
        if daily:
            thisHour = theTime.replace(hour=0,minute = 0,second=0,microsecond = 0)
        else:
            thisHour = theTime.replace(minute = 0,second=0,microsecond = 0)
        #log.debug("Time is {0}  Hour is {1}".format(theTime,thisHour))

        #If we are looking at the first Sample
        if not lastSample:
            log.debug("---> First Run")
            lastHour = thisHour
            lastSample = item
            continue

        timeDiff = item.time - lastHour

        #log.debug("Compare {0} to {1} = {2}".format(lastSample,item,timeDiff))


        #Check the time difference
        if timeDiff.total_seconds() >= timeCutOff :
            #log.debug("--> Hourly Change")
            outItem = [lastHour,cumWatts,descrip]
            outList.append(outItem)
            lastHour = thisHour
            cumWatts = 0.0

        #Any Additions
        tDiff = (theTime-lastSample.time).total_seconds()
        #lastDiff = (theTime-lastHour).total_seconds()
        tHours = tDiff / 3600 #Turn this into Hours
        #lastTime = theTime
        wH = value * tHours #/ 1000.0
        #log.debug("Diff {0} Hours {1} Sample {2} wH {3}".format(tDiff,tHours,value,wH))
        cumWatts += wH
        lastTime = theTime
        lastSample = item

        #else:
    #And the Final Reading
    outList.append([lastHour,cumWatts,descrip])
         
    return outList



def _getElectric(theId,parameters,reqType,request):
    log.setLevel(logging.DEBUG)
    log.debug("==== GETTING ELECTRICITY NODES ====")
    log.debug("Id {0}".format(theId))
    if not theId:
        theId = parameters.get("id",False)
    if not theId:
        return []
    log.debug("Parameters {0}".format(parameters))
    #log.debug("JSON {0}".format(request.json_body))
    daily = parameters.get("daily",False)

    asCsv = parameters.get("csv",False)

    if daily == 'true':
        daily = True
    #elif daily == 'false':
    else:
        daily == False
    
    log.debug("Daily ?? {0}".format(daily))
    log.debug("CSV {0}".format(asCsv))

    #Id is the house Id
    session = meta.Session()
    
    #Fetch the Electricity data
    elecSensor = session.query(models.SensorType).filter_by(name="Power").first()
    log.debug("Electrity Sensor is {0}".format(elecSensor))

    theHouse = session.query(models.House).filter_by(id = theId).first()
    log.debug("House is {0}".format(theHouse))

    #Location Ids 
    locationIds = session.query(models.Location).filter_by(houseId = theHouse.id)
    lIds = []
    for item in locationIds:
        log.debug("Location {0}".format(item))
        lIds.append(item.id)

    theData = session.query(models.Reading).filter_by(typeId = elecSensor.id)
    theData = theData.filter(models.Reading.locationId.in_(lIds))
    log.debug("Number of Samples {0}".format(theData.count()))
    
    eventQuery = session.query(models.Event).filter_by(houseId = theHouse.id).all()

    hourReadings =  getStatsElectricHour(theData,daily,eventQuery)



    if hourReadings is None:
        return []
    if not hourReadings:
        return []

    if asCsv:
        request.override_renderer = "csv"
        dStr = "Hourly"
        if daily:
            dStr = "Daily"
            
        addStr = theHouse.address.replace(" ","_")
        fileName = "{0}-{1}.csv".format(addStr,dStr)
        log.debug("Filename: {0}".format(fileName))

        return {"header":["Date","Reading","Events"],
                #"rows":[[1,2],[3,4]],
                "rows":hourReadings,
                "fName":fileName,
                }


    outReadings = [{"time":time.mktime(x[0].timetuple())*1000,
                    "date":x[0].isoformat(),
                    "kWh":x[1]/1000.0,
                    "event":x[2]} for x in hourReadings]
    
    #outReadings = [{"time":x[0].isoformat(),"kWh":x[1]/1000.0,"event":x[2]} for x in hourReadings]
    log.debug("Done")
    return outReadings


def _getRegistered(theId,parameters,reqType,request):
    log.setLevel(logging.DEBUG)
    log.debug("==== GETTING REGISTERED NODES ====")
    session = meta.Session()


    log.debug("--> Paramters {0}".format(parameters))

    houseId = parameters.get("houseId",None)
    #Get Locations associated with this houses
    theHouse = session.query(models.House).filter_by(id=houseId).first()
    log.debug("House Id {0} => {1}".format(houseId,theHouse))

    parentId = parameters.get("parent",None)
    if parentId:
        log.debug("PARENT IS GIVEN {0}".format(parentId))
        #Debumge out Parent to get the Node and Location
        spt = parentId.split("_")
        if len(spt) != 2:
            return []
        nodeId,locationId = spt
        theNode = session.query(models.Node).filter_by(id=nodeId).first()
        theLocation = session.query(models.Location).filter_by(id=locationId).first()

        log.debug("Node {0}".format(theNode))
        log.debug("Location {0}".format(theLocation))
                  
        #Sensors "Attached" to this Node
        
        outList = []
        sIds = []
        tIds = []
        log.debug("Attached Sensors {0}".format(theNode.sensors))

        for sensor in theNode.sensors:
            sIds.append(sensor.id)
            tIds.append(sensor.sensorTypeId)
            log.debug("Sensor is {0}".format(sensor))

            theSensor = {"id":"{0}_{1}".format(parentId,sensor.sensorType.id),
                         "node":sensor.sensorType.name,
                         "parent":parentId,
                         "status":"SENSOR",
                         "type":"sensor",
                         }

            dataQry = session.query(models.Reading).filter_by(nodeId=theNode.id,
                                                              typeId=sensor.sensorType.id,
                                                              locationId=theLocation.id)
            print dataQry.first()
            count =dataQry.count()
            log.debug("Total Samples {0}".format(count))
            theSensor["totalSamples"] = count
                                  
            if count:
                theSensor["firstTx"] = dataQry[0].time.isoformat()
                theSensor["lastTx"] = dataQry[-1].time.isoformat()
                            

            outList.append(theSensor)

        #Then Fetch the Details from the Sensors that are Not Attached
        extraSensors = session.query(sqlalchemy.distinct(models.Reading.typeId)).filter_by(nodeId=theNode.id,
                                                                                           locationId=theLocation.id)
        extraSensors = extraSensors.filter(~models.Reading.typeId.in_(tIds))
        log.debug("Extra Sensors {0}".format(extraSensors.all()))
        log.debug("Attached Ids {0}".format(sIds))
        log.debug("Attached T Ids {0}".format(tIds))
        for extraSensor in extraSensors:
            sId = extraSensor[0]
            if not sId in sIds:
                log.debug("Extra Sensor {0}".format(sId))
                #sensor = session.query(models.Sensor).filter_by(nodeId=theNode.id,
                #                                                sensorTypeId=sId).first()
                sType = session.query(models.SensorType).filter_by(id=sId).first()

                log.debug("--> {0}".format(sType))
                #log.debug("--> {0}".format(sensor.sensorType))
                theSensor = {"id":"{0}_{1}".format(parentId,sId),
                             "node":sType.name,
                             "parent":parentId,
                             "status":"EXTRA",
                             "type":"sensor",
                             }
                log.debug(theSensor)
                dataQry = session.query(models.Reading).filter_by(nodeId=theNode.id,
                                                                  typeId=sType.id,
                                                                  locationId=theLocation.id)
                count =dataQry.count()
                theSensor["totalSamples"] = count

                if count:
                    theSensor["firstTx"] = dataQry[0].time.isoformat()
                    theSensor["lastTx"] = dataQry[-1].time.isoformat()

                outList.append(theSensor)

        return outList


    #Otherwise Fetch the Base Items

    houseLoc = theHouse.locations
    log.debug("Locations are {0}".format(houseLoc))

    #And the Nodes associated with these locations
    outList = []
   

    for loc in houseLoc:
        locNodes = loc.OldNodes
        log.debug("Location {0} Nodes {1}".format(loc,locNodes))
        #if locNodes is None:
            #Hunt for locations manually (this should only happen on update)
            
            
        for nd in locNodes:
            theItem = {"id": "{0}_{1}".format(nd.id,loc.id),
                       "node":nd.id,
                       "room":loc.room.name,
                       "type":"location",
                       }

            #Status can wait
            readingQry = session.query(models.Reading)
            readingQry = readingQry.filter_by(nodeId = nd.id,
                                              locationId = loc.id)
            readingQry = readingQry.order_by(models.Reading.time)
            
            count = readingQry.count()
            theItem["totalSamples"] = readingQry.count()

            outList.append(theItem)

    log.debug("outList ")
    log.debug(outList)
    return outList

                                

def _getRegisteredNew(theId,parameters,reqType,request):
    """Get all locations that are registered with a particualar House
    
    :var dict parameters: Request.parameters for this query
    :return: A List of Nodes and Locations assocatited with this House
    """
    log.setLevel(logging.DEBUG)
    
    session = meta.Session()

    houseId = parameters.get("houseId",None)
    #Get Locations associated with this houses
    theHouse = session.query(models.House).filter_by(id=houseId).first()

    log.debug("House Id {0} => {1}".format(houseId,theHouse))
    log.debug("--> Paramters {0}".format(parameters))

    houseLoc = theHouse.locations
    log.debug("Locations are {0}".format(houseLoc))

    #And the Nodes associated with these locations
    outList = []
    
    for loc in houseLoc:
        locNodes = loc.OldNodes
        log.debug("Location {0} Nodes {1}".format(loc,locNodes))
        
        for nd in locNodes:
            theItem = {"id": "{0}_{1}".format(nd.id,loc.id),
                       "node":nd.id,
                       "room":loc.room.name}

            #Status can wait
            readingQry = session.query(models.Reading)
            readingQry = readingQry.filter_by(nodeId = nd.id,
                                              locationId = loc.id)
            readingQry = readingQry.order_by(models.Reading.time)
            
            count = readingQry.count()
            theItem["totalSamples"] = readingQry.count()





            if count >0 :
                sensorList = []
                firstTime = None
                lastTime = None

                #lets look at the sensors for that particular Node
                
                #Sensor Types 
                sensors = nd.sensors
                log.debug("----Sensors Attached to {0}-----".format(nd))
                #log.debug("Sensors Attached to Node {0}".format(sensors))
               

                for item in sensors:
                    log.debug("--> {0}".format(item))

                    subQry = readingQry.filter_by(typeId = item.sensorTypeId)
                    #print subQry
                    subSamples = subQry.count()
                    firstTx = None
                    if subSamples:
                        firstTx = subQry[0].time
                        lastTx = subQry[-1].time
                        if not firstTime or firstTime > firstTx:
                            firstTime = firstTx
                        if not lastTime or lastTime < lastTx:
                            lastTime = lastTx
                            
                    theSensor = {"node":item.sensorType.name,
                                 "parent":"{0}_{1}".format(nd.id,loc.id),
                                 "status":"SENSOR",
                                 "totalSamples":subSamples,
                                 }

                    if firstTx:
                        theSensor["firstTx"] = firstTx.isoformat()
                        theSensor["lastTx"] = lastTx.isoformat()

                    sensorList.append(theSensor)
                          
                    print theSensor

                #And Lets Fish out the sensor types from the readings
                sReading = session.query(sqlalchemy.distinct(models.Reading.typeId)).filter_by(nodeId = nd.id)
                log.debug("---- DISTINCT SENSOR TYPES ----")
                senTypes = [x.sensorTypeId for x in sensors]
                #readTypes = [x[0] for x in sReading]

                
                for item in sReading:
                    theType = item[0]
                    log.debug("--> {0}".format(theType))
                    if not theType in senTypes:
                        log.warning("Additional Sensor Type {0} found for Node".format(theType))
                        subQry = readingQry.filter_by(typeId = theType)
                        subSamples = subQry.count()

                        if subSamples:
                            firstTx = subQry[0].time
                            lastTx = subQry[-1].time
                            if not firstTime or firstTime > firstTx:
                                firstTime = firstTx
                                if not lastTime or lastTime < lastTx:
                                    lastTime = lastTx
                    
                            theSensorType = session.query(models.SensorType).filter_by(id=theType).first()

                            theSensor = {"node": "{0} {1}".format(theSensorType.name,theSensorType.id),
                                         "parent":"{0}_{1}".format(nd.id,loc.id),
                                         "status":"READING SENSOR",
                                         "totalSamples":subSamples,
                                         "firstTx":firstTx.isoformat(),
                                         "lastTx":lastTx.isoformat()
                                         }
                            sensorList.append(theSensor)                        

                    
            theItem["firstTx"] = firstTx.isoformat()
            theItem["lastTx"] = lastTx.isoformat()
            #print sqlalchemy.func.min(readingQry.time)
                
            
            

            outList.append(theItem)
            outList.extend(sensorList)
        

    return outList

def _getStatus(nodeId,parameters,reqType,request):
    """Get Node Status

    :var parameters: Request.parameters for this query
    :return: List of node Statuses
    """
    log.setLevel(logging.INFO)
    session = meta.Session()

    if reqType == "PUT":
        #Add / Update the Item
        log.debug("PUT Request")
        log.debug(parameters)
        log.debug(request.json_body)

        #jsonBody = {u'node': 70, u'status': u'Good', u'lastTx': u'2012-07-27T10:47:49', u'newRoom': u'Test Room', u'currentRoom': u'Test Room', u'id': 70, u'currentHouse': u'14 Gifford Walk'}
        jsonBody = request.json_body
        
        #The only thing we can do is update the Location
        nid = jsonBody["node"]
        rName = jsonBody["newRoom"]
        hid = jsonBody["houseId"]

        theNode = session.query(models.Node).filter_by(id=nid).first()
        log.debug("--> Node {0}".format(theNode))

        theRoom = session.query(models.Room).filter_by(name=rName).first()
        log.debug("Room from Query {0}".format(theRoom))
        if theRoom is None:
            theRoom = models.Room(name=rName)
            session.add(theRoom)
            session.flush()
        log.debug("--> Final Room {0}".format(theRoom))
            
        #Then Get the Location
        theLoc = session.query(models.Location).filter_by(houseId=hid,
                                                          roomId=theRoom.id).first()
        if theLoc is None:
            log.info("== Adding Location")
            theLoc = models.Location(houseId=hid,
                                     roomId=theRoom.id)
            session.add(theLoc)
            session.flush()

        log.debug("--> Final Location {0}".format(theLoc))
        
        theNode.locationId = theLoc.id
        session.flush()

        jsonBody["newRoom"] = None
        jsonBody["currentRoom"] = rName
        jsonBody["currentHouse"] = theLoc.house.address
        return jsonBody

        pass

    elif reqType == "GET":
        #log.setLevel(logging.WARNING)
        outList = []
    
        log.debug("Nodes we have heard from")

        houseId = parameters.get("houseId",None)
        cutTime = parameters.get("cutTime",None)


        heardQuery = session.query(sqlalchemy.distinct(models.NodeState.nodeId))

        
        # if cutTime:
        #     cutTime = datetime.datetime.now() - datetime.timedelta(days=int(cutTime))
        #     log.info("== Processing Cuttof Time {0}".format(cutTime))
        #     heardQuery = heardQuery.filter(models.NodeState.time >= cutTime)

        heardNodes = [x[0] for x in heardQuery]

        #if houseId:
        #    theQry = theQry.filter_by(houseId = houseId)
        #    log.debug("Search for locations associated with House {0}".format(houseId))   

        #Get Type Id for Battery
        batteryType = session.query(models.SensorType).filter_by(name="Battery Voltage").first()
        log.debug("==== Battry Type {0}".format(batteryType))

        for node in heardNodes:
            log.debug("Deal with Node: {0}".format(node))
            #lastTime = session.query(models.NodeState).filter_by(nodeId=node)
            lastTime = session.query(models.NodeState)#.join(models.Node)
            lastTime = lastTime.filter(models.NodeState.nodeId==node)

            lastTime = lastTime.order_by(models.NodeState.time.desc()).first()



            #out=lastTime.first()
            #log.debug("--> {0}".format(out))
            #I can now add those to a list
            #log.info("---- ITEM {0}, {1}, Node {2}".format(lastTime,lastTime.nodeId,lastTime.node))

            #We want to check if the node exists
            if lastTime.node is None:
                log.warning("Node {0} doesn't exist but has a location".format(lastTime.nodeId))
                #It may be a good idea to create item
                theNode = models.Node(id=lastTime.nodeId,
                                      location=None,
                                      nodeTypeId=None)
                session.merge(theNode)
                session.flush()
                theLoc = None
            else:
                theLoc = lastTime.node.location            

            if houseId:
                if not theLoc:
                    continue
                log.debug("Filter by House Id {0}, theLoc {1}".format(houseId,theLoc.house.id))
                if theLoc.house.id != int(houseId):
                    log.debug("Ignoring")
                    continue
                



            theItem = {"id":lastTime.nodeId,
                       "node":lastTime.nodeId,
                       "lastTx":lastTime.time.isoformat(),
                       }

            #And Get the most Recent Battry Level
            lastBattery = session.query(models.Reading).filter_by(time = lastTime.time,
                                                                  nodeId = node,
                                                                  typeId = batteryType.id)
            lastBattery= lastBattery.first()
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
            timeDiff = datetime.datetime.now() - lastTime.time
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
    session = meta.Session()
    log.debug(request.matchdict)
    log.debug("Params {0}".format(request.params))
    nodeId = request.matchdict.get("id",None)


    if nodeId == "":
        #Or we can fetch the item from the parameters
        nodeId = request.params.get("id",None)
        if not nodeId:
            nodeId = 133
    log.debug("Id is {0}".format(nodeId))



        

    #Run the Query
    theQry = session.query(models.NodeState,sqlalchemy.func.count(models.NodeState)).filter_by(nodeId = nodeId)
    theQry = theQry.group_by(sqlalchemy.func.date(models.NodeState.time))
    dataCount = theQry.count()
    #theQry = theQry.limit(5)
    outList = [{"x":time.mktime(item[0].time.date().timetuple()),"value":item[1]} for item in theQry]
    #outList = [{"x":item[0].time.date().isoformat(),"value":item[1]} for item in theQry]
    #outList = [[time.mktime(item[0].time.date().timetuple()),item[1]] for item in theQry]
    #outList = [[item[0].time.isoformat(),item[1]] for item in theQry]
    #outList = [{"date":item[0].time.date().isoformat(),"value":item[1]} for item in theQry]
    #outList = []
    #for item in theQry:
    #    #Work out the output of the item
    #    outList.append([item[0].time.date().isoformat(),item[1]])
    #    log.debug(item)
    return outList

def _getReadingCount(locationId):
    session = meta.Session()
    theQry = session.query(models.Reading,
                           sqlalchemy.func.count(models.Reading)).filter_by(locationId = locationId)
    theQry = theQry.group_by(models.Reading.typeId)

    outItems = []
    for item in theQry:

        theItem = {"name":item[0].sensorType.name,
                   "size":item[1]}
        outItems.append(theItem)
    return outItems

def restTest(request):
    session = meta.Session()
    #return 



    baseItem = {"name":"Database"}
    baseChildren = []
                
    
    deployments = session.query(models.Deployment)

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


    houseQry = session.query(models.House).filter_by(deploymentId = None)
    houses = []
    for house in houseQry:
        thisHouse = {"name":house.address,
                     "children":[]}

        for location in house.locations:
                thisLocation = {"name":location.room.name,
                                "children":[]}

                readCount = _getReadingCount(location.id)
                thisLocation["children"].extend(readCount)

                #theQry = session.query(models.Reading).filter_by(locationId = location.id)
                #theCount = theQry.count()
                #if theCount == 0:
                #    theCount = 1
                
                #thisLocation["children"].append({"name":"Readings",
                #                                 "size": theCount})
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


def lastSync(request):
    """Fetch the last sample for a given house / deployment.
    To be used with the Push Script

    This should take the house address as a URL encoded string
    """
    houseName = request.params.get("house",None)
    log.info("Fetching last Sample for house >{0}<".format(houseName))
    
    if houseName is None:
        return None

    session = meta.Session()
    theHouse = session.query(models.House).filter_by(address=houseName).first()
    #theHouse = session.query(models.House).filter_by(address="5 Elm Road").first()
    log.debug("House is: {0}".format(theHouse))

    if theHouse is None:
        return None
    
    #Not Optimal Query But what the Hell
    locQry = theHouse.locations
    locIds = [x.id for x in theHouse.locations]
    log.debug("Location Ids: {0}".format(locIds))

    #readingQry = session.query(models.Reading, sqlalchemy.func.max(models.Reading.time)).filter(models.Reading.locationId.in_(locIds)).group_by(models.Reading.locationId).limit(20)
    

    readingQry = session.query(sqlalchemy.func.max(models.Reading.time)).filter(models.Reading.locationId.in_(locIds)).first()
    #for line in readingQry:
    #   #print line[0],line[1]
    #    print line


    log.debug("Result is {0}".format(readingQry))
    readingQry = readingQry[0]
    log.debug("Stripped Result is {0}".format(readingQry))
    if readingQry is not None:
        return readingQry.isoformat()
    else:
        return readingQry

    #theDate = datetime.datetime.now().isoformat()
    #return theDate
