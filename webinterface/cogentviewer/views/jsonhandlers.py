"""
==========
JSON.py 
==========

This class contains methods for fetching infomration from the database,
and returning it to a web page through a JSON interface.

@author:  Dan Goldsmith
@date: December 2012
"""

from pyramid.response import Response
from pyramid.renderers import render_to_response
import pyramid.url

import sqlalchemy

import logging

import cogentviewer.models.meta as meta
import cogentviewer.models as models

import time
import datetime
import json
#import numpy
#For JS Dates
import dateutil.parser


log = logging.getLogger(__name__)
#log.setLevel(logging.INFO)

def exposeTemp(theQry):
    #Process temperature readings
    session = meta.Session()
    sensorParams = {}

    outList = [0,0,0,0,0]
    for reading in theQry:

        theSensor = sensorParams.get((reading.nodeId,reading.typeId),None)
        #log.debug("Original Reading {0} Sensor is {1}".format(reading,theSensor))
        if not theSensor:
            theSensor = session.query(models.Sensor).filter_by(nodeId = reading.nodeId,sensorTypeId = reading.typeId).first()
            if theSensor is None:
                theSensor = models.Sensor(calibrationSlope = 1.0,calibrationOffset = 0.0)
            sensorParams[(reading.nodeId,reading.typeId)] = theSensor


        value = theSensor.calibrationOffset + (theSensor.calibrationSlope * reading.value)
        #log.debug("Orig -> {0} - New {1}".format(reading,value))
        if value <16:
            outList[0] += 1
        elif value <= 18:
            outList[1] += 1
        elif value <= 22:
            outList[2] += 1
        elif value <= 27:
            outList[3] += 1
        else:
            outList[4] += 1

    #log.debug("Out List {0}".format(outList))
    session.close()
    return outList

def exposeHum(theQry):
    #Process temperature readings
    session = meta.Session()
    sensorParams = {}

    outList = [0,0,0,0]
    for reading in theQry:

        theSensor = sensorParams.get((reading.nodeId,reading.typeId),None)
        #log.debug("Original Reading {0} Sensor is {1}".format(reading,theSensor))
        if not theSensor:
            theSensor = session.query(models.Sensor).filter_by(nodeId = reading.nodeId,sensorTypeId = reading.typeId).first()
            if theSensor is None:
                theSensor = models.Sensor(calibrationSlope = 1.0,calibrationOffset = 0.0)
            sensorParams[(reading.nodeId,reading.typeId)] = theSensor


        value = theSensor.calibrationOffset + (theSensor.calibrationSlope * reading.value)
        #log.debug("Orig -> {0} - New {1}".format(reading,value))

        if value <45:
            outList[0] += 1
        elif value <= 65:
            outList[1] += 1
        elif value <= 85:
            outList[2] += 1
        else:
            outList[3] += 1

    #log.debug("Out List {0}".format(outList))
    session.close()
    return outList

def fetchExposeData(sensorType,startDate,endDate,locationId,sensorTypeId):
    """Fetch data for a specific location

    :var list parameterList: List of parameters (sensorType,startDate,stopDate,locationId)
    """
    
    session = meta.Session()

    log.debug("{0} EXPOSURE {0}".format("-"*25))
    log.debug("--> Type\t\t {0}".format(sensorType))
    log.debug("--> TypeID\t\t {0}".format(sensorTypeId))

    #Unlike Temperature (We Dont need to fecth Distinct Nodes)
    outList = []

    theLocation = session.query(models.Location).filter_by(id=locationId).first()
    log.debug("Location is {0} ({1}".format(theLocation,locationId))


    theQry = session.query(models.Reading).filter_by(locationId = locationId)
    theQry = theQry.filter_by(typeId = sensorTypeId)
    if startDate:
        theQry = theQry.filter_by(models.Reading.time >= startDate)
    if endDate:
        theQry = theQry.filter_by(models.Reading.time <= endDate)
    #theQry = theQry.limit(10)
    # theQry = theQry.filter_by(nodeId = nodeId[0])
    samples = theQry.count()
    log.debug("Total Count of Samples {0}".format(samples))    
    if samples == 0:
        return
    
    #Now we need to parse, calibrate and classify the data 

    #Get the Headers
    if sensorType.name == "Temperature":
        #Then go through the database
        theData = exposeTemp(theQry)
        
    elif sensorType.name == "Humidity":
        theData = exposeHum(theQry)
        

    else:
        #return
        return

    seriesName = "{0}<br>{1}".format(theLocation.house.address,theLocation.room.name)
    return seriesName, theData


    #log.debug("Headers {0}".format(headerList))

    # uniqueNodes = session.query(sqlalchemy.distinct(models.Reading.nodeId)).filter_by(locationId = locationId)
    # log.debug("Unique Nodes {0}".format(uniqueNodes.all()))
    
    # #log.debug("Location {0} {1} Initial Query Records {2}".format(locationId,sensorType,recordCount))
    # outList = []
    # for nodeId in uniqueNodes:
    #     #print "Sorting Node {0}".format(nodeId)
    #     theQry = session.query(models.Reading).filter_by(locationId = locationId)
    #     theQry = theQry.filter_by(typeId = sensorTypeId)

    #     theQry = theQry.filter_by(nodeId = nodeId[0])
    #     log.debug("Total Count of Samples {0}".format(theQry.count()))

        
    #     #theQry = theQry.limit(10)
    #     #Calibrate
    #     theGenerator = models.calibratePairs(theQry)
    #     theData = list(theGenerator)
    #     theDict = {"name":"({0}) {1} {2}".format(nodeId[0],theLocation.room.name,sensorType),
    #                "data":theData}
    #     outList.append(theDict)
    #log.debug("Data Processing Complete")
    #log.debug(outList)
    #return [outList]

def fetchLocationData(sensorType,startDate,endDate,locationId,sensorTypeId):
    """Fetch data for a specific location

    :var list parameterList: List of parameters (sensorType,startDate,stopDate,locationId)
    """
    
    session = meta.Session()

    theLocation = session.query(models.Location).filter_by(id=locationId).first()
    log.debug("Searching forl Location {0} == {1}".format(locationId,theLocation))
    #theQry = session.query(models.Reading).filter_by(locationId = locationId)
    #theQry = theQry.filter_by(typeId = sensorTypeId)

    log.debug("Location is {0} ({1}".format(theLocation,locationId))
    #recordCount = theQry.count()

    #if recordCount == 0:
    #    return None
    #return
    uniqueNodes = session.query(sqlalchemy.distinct(models.Reading.nodeId)).filter_by(locationId = locationId)
    log.debug("Unique Nodes {0}".format(uniqueNodes.all()))
    
    #log.debug("Location {0} {1} Initial Query Records {2}".format(locationId,sensorType,recordCount))
    outList = []
    for nodeId in uniqueNodes:
        #print "Sorting Node {0}".format(nodeId)
        theQry = session.query(models.Reading).filter_by(locationId = locationId)
        theQry = theQry.filter_by(typeId = sensorTypeId)

        theQry = theQry.filter_by(nodeId = nodeId[0])
        theCount = theQry.count()
        log.debug("Total Count of Samples {0}".format(theCount))
        if theCount == 0:
            continue
        #    return

        
        #theQry = theQry.limit(10)
        #Calibrate
        theGenerator = models.calibratePairs(theQry)
        theData = list(theGenerator)
        theDict = {"name":"({0}) {1}<br>{2}".format(nodeId[0],theLocation.room.name,sensorType.name),
                   "data":theData,
                   "id":"{0}_{1}".format(theLocation.houseId,theLocation.id),
                   }
        outList.append(theDict)

    #Look for Events attacehd to this datastream
    log.debug("Location Details {0}".format(theLocation))
    events = session.query(models.Event).filter_by(houseId = theLocation.houseId)
    if events.count() > 0:
        log.debug("==== EVENTS ====")
        log.debug(events)
        theDict = {"type":"flags",
                   "data":[],
                   "shape":"squarepin",
                   "width":16}
        data = []
        for evt in events:
            log.debug(evt)
            newTime = time.mktime(evt.time.timetuple())*1000.0
            log.debug("Time {0}  New {1}".format(evt.time,newTime))
            data.append({"x":newTime,
                         "title":evt.name})

        theDict["data"] = data
        log.debug("Data {0}".format(theDict))
        outList.append(theDict)
    log.debug("Data Processing Complete")
    #log.debug(outList)
    return outList

def jsonFetch(request):
    """New Location based time series data"""
    log.debug("Fetching JSON Data")

    session = meta.Session()
    
    #Lets split out the bits we definately know about
    paramDict = request.GET.mixed()
    #log.debug("Json Body {0}".format(request.json_body()))
    log.debug("--> Parameter Dictionary {0}".format(paramDict))

    sensorType = paramDict.get("sensorType",None)
    startDate = paramDict.get("startDate",None)
    endDate = paramDict.get("endDate",None)
    deployments = paramDict.get("deployments",None)
    houses = paramDict.get("houses",None)
    locations = paramDict.get("locations",None)
    locType = paramDict.get("locType",None)
    #treeItems = paramDict.get("treeItems",None)
    graphType = paramDict.get("graphType","time")


    if sensorType == "":
        sensorType = None
    if startDate:
        startDate = dateutil.parser.parse(startDate)
    if endDate:
        endDate = dateutil.parser.parse(endDate)

    log.debug("Sensor Type: {0}".format(sensorType))
    log.debug("Date Range: {0} -> {1}".format(startDate,endDate))
    log.debug("Deployments: {0}".format(deployments))
    log.debug("Houses: {0}".format(houses))
    log.debug("Locations: {0}".format(locations))
    log.debug("Loc Type: {0}".format(locType))
    log.debug("Type: {0}".format(graphType))
    

    return
    paramDict = [sensorType,startDate,endDate,1]

    data = []
    graphTitle = None
    legendSuffix = None

    #Lets do a little sanity checking.
    if deployments:
        log.info("Deployment or House Supplied, Limiting to Temperature Data")
        if sensorType is None:
            sensorType = 0 #Default to temperature

        #Get the Title Sorted
            
        graphTitle = "Deployment Temperature Data"
    elif houses:
        graphTitle = "Time Series Data"


    sList =  ["Temperature","Humidity"]#,"Light TSR","Light PAR","CO2","Air Quality","VOC"]
        
    if sensorType:
        if graphType == "temp":
            sensorType = session.query(models.SensorType).filter_by(id=sensorType).first()
            legendSuffix = "{0} {1}".format(sensorType.name,sensorType.units)
            sList = [sensorType.name]
        else:
            if sensorType == "1":
                sList = ["Temperature"]
            elif sensorType == "2":
                sList = ["Humidity"]
            elif sensorType == "3":
                sList = ["Co2"]

    #sList = ["Temperature"]
    #else:
    #    sensorType = 0 #FIX THIS UP SO WE MOVE TO ALL "INTERESTING" Sensors
    #    legendSuffix = "Temperature (C)"

    targetLocations = []
    outSeries = []
    """
    I feel the easiest way to procede is to 
    1) Pull all the deployments into houses
    2) Then Turn these into Locations
    """
    
    if locType:
        log.warning("Location Type Specified {0}".format(locType))
        if not type(locType) == list:
            locType = [locType]
        for item in locType:
            locId,typeId = item.split(",")
            log.debug("===== Split item {0} = Loc{1} Type{2} =====".format(item,locId,typeId))
            theSensor = session.query(models.SensorType).filter_by(id = typeId).first()
            seriesData = fetchLocationData(theSensor,startDate,endDate,locId,typeId)
            #log.debug(seriesData)
            #if seriesData:
            #if seriesData is not None:
            outSeries.extend(seriesData)
            #log.debug("Data {0}".format(seriesData))
        #log.debug("All Data")
        #log.debug(outSeries)
        log.debug(theSensor)
        return {"title":"{0} ({1})".format(theSensor.name,theSensor.units),
                "series":outSeries}

    if deployments:
        if type(deployments) != list:
            deployments = [deployments]
        for item in deployments:
            
            theDeployment = session.query(models.Deployment).filter_by(id=item).first()
            log.debug("Fetching Houses for Deployment {0} -> {1}".format(item,theDeployment))
            depHouses = theDeployment.houses
            log.debug("Houses are {0}".format(depHouses))
            #Then Locations
            for house in depHouses:
                log.debug("Locations for {0} are {1}".format(house,house.locations))
                targetLocations.extend([x.id for x in house.locations])
    if houses:
        log.debug("Processing Houses {0}".format(houses))
        if type(houses) != list:
            houses = [houses]
        for item in houses:
            theHouse = session.query(models.House).filter_by(id=item).first()
            log.debug("House {0} is {1}".format(item,theHouse))
            targetLocations.extend([x.id for x in theHouse.locations])
    
    if locations:
        targetLocations.extend([int(x) for x in locations])
    #data = fetchLocationData(sensorType,startDate,endDate,1,0)
    targetLocations = set(targetLocations)
    log.debug("Target Locations {0}".format(targetLocations))
  
    returnItem = {}

    log.debug("Sensor List {0}".format(sList))
    #return 

    for sType in sList:       
        theSensor = session.query(models.SensorType).filter_by(name=sType).first()
        log.debug("Processing Sensor {0}".format(theSensor))


        if sType == "Temperature":
            seriesList = [{"name":"Potental Health <16C","data":[]},
                          {"name":"Cold <=18C","data":[]},
                          {"name":"Comfort <=22C","data":[]},
                          {"name":"Warm <=27C","data":[]},
                          {"name":"Overheated >27C","data":[]},
                          ]

            sensorList = []
            returnItem["title"] = "Temperature Exposure"
        elif sType == "Humidity":
            seriesList = [{"name": "Dry < 45%","data":[]},
                          {"name": "Comfort <65%","data":[]},
                          {"name": "Damp <=85%","data":[]},
                          {"name": "Risk > 85%","data":[]},
                          ]
            returnItem["title"] = "Humidity Exposure"
            sensorList = []
                         

        seriesData = None
        for loc in targetLocations:
            log.debug("Processing Location {0}".format(loc))
            if graphType == "temp" or graphType == "time":
                log.debug("--> Fetch Time Data")
                seriesData = fetchLocationData(theSensor,startDate,endDate,loc,theSensor.id)
            elif graphType == "expose":
                log.debug("--> FETCH EXPOSE DATA")
                seriesName,seriesData = fetchExposeData(theSensor,startDate,endDate,loc,theSensor.id)
                #sensorList.append(loc
                log.debug("===== SERIES DATA {0}".format(seriesData))
                sensorList.append(seriesName)
                for x,item in enumerate(seriesData):
                    seriesList[x]["data"].append(item)
                
            #log.debug("Data {0}".format(seriesData))
            if seriesData:
                #log.debug("Data {0}".format(seriesData[0]))
                outSeries.extend(seriesData)
            

    if seriesList:
        #returnItem["title"] = "FOOBAR"
        returnItem["series"] = seriesList
        returnItem["headers"] = sensorList
    else:

        returnItem["series"] = outSeries
    return returnItem



def jsonnav(request):
    """Return a json representation of the information stored in the database,
    this can then be used for navigation etc."""
    jsonData = []


    log.debug("Json Nav")
    session = meta.Session()


    theList = []
    jsonDict = {}

    sTypes = []
    typeQuery = session.query(models.SensorType).all()
    for item in typeQuery:
        #sTypes.append(item.asJSON())
        sTypes.append({"id":item.id,
                       "name":item.name,
                       "type":"sensor"})

    #sensorTypes["children"] = sTypes
    theData= {"identifier":"id",
              "label":"name",
              "items":sTypes}

    #import pprint
    #pprint.pprint(theData)

    return theData


# def jsonRest(request):

#     #Get any Parameters supplied pat of the URL
#     deployId = request.matchdict.get("deployId",None)
#     session = meta.Session()
#     log.debug("{0} JSON REST CALLED {0}".format("=-"*20))
#     log.debug("Useful Request information")
#     log.debug("Method {0}".format(request.method))
#     log.debug("Parameters {0}".format(request.params))
#     log.debug("Matchdict {0}".format(request.matchdict))
#     log.debug("UrlArgs {0}".format(deployId))
#     log.debug("="*40)

#     #testItems = {"id":"A","label":"Root","children":[{"id":"A1","label":"A1"},
#     #                                                 {"id":"A2","label":"A2"}]}

#     #Do this in a basic way, Just give us a tree
#     rootItem = {"id":"root",
#                 "label":"deployments"}
    

#     children = []

#     noDep = {"id":"nodep","label":"No Deployment"}
    
#     #And get any children ("deployments")
#     deployments = session.query(models.Deployment).all()
#     log.debug("Deployments")
#     for item in deployments:
#         treeItem = item.asTree()
#         children.append(treeItem)
#         #treeItem = None
#         #log.debug("--> {0} {1}".format(item,treeItem))


#     #Sort out houses without a deployment
#     children.append(noDep)
#     rootItem["children"] = children
#     return [rootItem]

#     theQry = session.query(models.House).filter_by(deploymentId=None)
#     log.debug("Houses without a Deployment")
#     for item in theQry:
#         log.debug("--> {0}".format(item))
#         treeItem = item.asTree()
#         children.append(treeItem)


#     rootItem["children"] = children


#     #We only have one root, but there could be more
#     theTree = [rootItem]
#     #import pprint
#     #pprint.pprint(theTree)
#     return theTree


#     return

#     if request.method == "GET":
#         #GETS ask for an Item.
#         #Generally if there are no parameters then we return everything
#         log.debug("--> GET REQUEST")
#         #Deal with the case where we want the root item

#         if deployId == "root":
#             log.debug("--> --> Returning Root Object")

#             #Add A Root Node
#             theItem = {"id":"root",
#                        "name":"kangaroot",
#                        "children": [{"id":"D_1",
#                                      "name":"Dep1"},
#                                     {"id":"D_2",
#                                      "name":"Dep2"}
#                                     ]
#                        }
#             return theItem
#         elif deployId == None:
#             log.debug("{0} No Deployment Id Given {0}".format("-"*5))
#             #This means we need to issue a general query
            
#             #Take a look at the parameters we have been Given
#             params = request.params
#             parent = params.get("parent",None)
#             if parent:
#                 log.debug(" Searching for objects with parent {0}".format(parent))
                
#                 if parent == "root":
#                     #We need to return deployments
#                     theQry = session.query(models.Deployment)
#                     #log.debug("Query Results {0}".format(theQry))
#                     retVals = [x.asJSON() for x in theQry]
#                     #log.debug("Return {0}".format(retVals))
#                     return retVals
            
#         else:
#             log.warning("{0} Dealing with another deployment Id {0}".format("#"*30))


#         return ""
