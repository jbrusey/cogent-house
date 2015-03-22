"""
==========
JSON.py
==========

This class contains methods for fetching infomration from the database,
and returning it to a web page through a JSON interface.

@author:  Dan Goldsmith
@date: December 2012
"""

import sqlalchemy

import logging

import cogentviewer.models.meta as meta
from ..models.meta import DBSession
import cogentviewer.models as models

import time
import datetime
#For JS Dates
import dateutil.parser


log = logging.getLogger(__name__)
#log.setLevel(logging.INFO)

def expose_temp(qry, categories, nodeid):
    """Process temperature readings

    :param qry: Query object to Process
    :param categories: List of categories
    :param nodeid: Id of node to deal with
    """
    #Process temperature readings
    log.setLevel(logging.INFO)
    outlist = [0, 0, 0, 0, 0]

    #Get any calibration details
    sensorqry = DBSession.query(models.Sensor)
    sensorqry = sensorqry.filter_by(nodeId = nodeid,
                                    sensorTypeId = 0)
    sensor = sensorqry.first()

    if sensor is None:
        sensor = models.Sensor(calibrationOffset = 0,
                               calibrationSlope = 1)

    log.debug("Sensor Related to this Node is {0}".format(sensor))

    prevreading = None

    #decalibrate the bands
    val1 = (16 / sensor.calibrationSlope) - sensor.calibrationOffset
    val2 = (18 / sensor.calibrationSlope) - sensor.calibrationOffset
    val3 = (22 / sensor.calibrationSlope) - sensor.calibrationOffset
    val4 = (27 / sensor.calibrationSlope) - sensor.calibrationOffset

    #Lookup for finding the corrsing point
    crossingpoints = {0:val1,
                      1:val2,
                      2:val3,
                      3:val4}

    for reading in qry:
        value = reading.value

        thiscat = None

        if value < val1:
            thiscat = 0
        elif value <= val2:
            thiscat = 1
        elif value <= val3:
            thiscat = 2
        elif value <= val4:
            thiscat = 3
        else:
            thiscat = 4

        if prevreading is None:
            prevreading = reading
            lastcat = thiscat

        else:
            tdiff = reading.time - prevreading.time
            thours = (tdiff.days * 24.0) + (tdiff.seconds / 60.0 / 60.0 )

            if thiscat == lastcat:
                #If categorys match then we just add the time
                outlist[thiscat] += thours
            else:
                # log.debug("===== Categories differ ======")
                log.debug("Cats Differ This {0} , Prev {1}".format(reading,
                                                                   prevreading))
                # log.debug("Time Difference {0} {1}".format(tdiff, thours))

                #Calculate crossing poiint
                vdiff = prevreading.value - reading.value#dv
                delta = vdiff / thours #Rate of change
                # log.debug("Vdiff: {0}  Roc {1}".format(vdiff, delta))

                #Calculate the crossing point
                crossingidx = min([thiscat, lastcat])
                crossingvalue = crossingpoints[crossingidx]
                log.debug("Crosing point is {0} == {1}".format(crossingidx,
                                                               crossingvalue))

                #Differnece between crossing and actual point
                crossdiff = reading.value - crossingvalue
                #Time Calculation
                crosstime = abs(crossdiff / delta)
                #log.debug("X Diff {0} X time {1}".format(crossdiff,
                #                                         crosstime))

                outlist[thiscat] += crosstime
                outlist[lastcat] += thours - crosstime

                #log.debug("="*50)

            prevreading = reading
            lastcat = thiscat

    for idx, value in enumerate(outlist):
        categories[idx]["data"].append(value)

    log.setLevel(logging.DEBUG)
    return categories

def expose_humid(qry, categories, nodeid):
    """Work out exposure for humidity readings
    """
    #Process temperature readings
    log.setLevel(logging.INFO)
    outlist = [0, 0, 0, 0]

    #Get any calibration details
    sensorqry = DBSession.query(models.Sensor)
    sensorqry = sensorqry.filter_by(nodeId = nodeid,
                                    sensorTypeId = 2) #MAGIC NO
    sensor = sensorqry.first()

    if sensor is None:
        sensor = models.Sensor(calibrationOffset = 0,
                               calibrationSlope = 1)

    log.debug("Sensor Related to this Node is {0}".format(sensor))

    prevreading = None

    #decalibrate the bands
    val1 = (45 / sensor.calibrationSlope) - sensor.calibrationOffset
    val2 = (65 / sensor.calibrationSlope) - sensor.calibrationOffset
    val3 = (85 / sensor.calibrationSlope) - sensor.calibrationOffset


    #Lookup for finding the corrsing point
    crossingpoints = {0:val1,
                      1:val2,
                      2:val3,
                      }

    for reading in qry:
        value = reading.value

        thiscat = None

        if value < val1:
            thiscat = 0
        elif value <= val2:
            thiscat = 1
        elif value <= val3:
            thiscat = 2
        else:
            thiscat = 3

        if prevreading is None:
            prevreading = reading
            lastcat = thiscat

        else:
            tdiff = reading.time - prevreading.time
            thours = (tdiff.days * 24.0) + (tdiff.seconds / 60.0 / 60.0 )

            if thiscat == lastcat:
                #If categorys match then we just add the time
                outlist[thiscat] += thours
            else:
                # log.debug("===== Categories differ ======")
                log.debug("Cats Differ This {0} , Prev {1}".format(reading,
                                                                   prevreading))
                # log.debug("Time Difference {0} {1}".format(tdiff, thours))

                #Calculate crossing poiint
                vdiff = prevreading.value - reading.value#dv
                delta = vdiff / thours #Rate of change
                # log.debug("Vdiff: {0}  Roc {1}".format(vdiff, delta))

                #Calculate the crossing point
                crossingidx = min([thiscat, lastcat])
                crossingvalue = crossingpoints[crossingidx]
                log.debug("Crosing point is {0} == {1}".format(crossingidx,
                                                               crossingvalue))

                #Differnece between crossing and actual point
                crossdiff = reading.value - crossingvalue
                #Time Calculation
                crosstime = abs(crossdiff / delta)
                #log.debug("X Diff {0} X time {1}".format(crossdiff,
                #                                         crosstime))

                outlist[thiscat] += crosstime
                outlist[lastcat] += thours - crosstime

                #log.debug("="*50)

            prevreading = reading
            lastcat = thiscat

    for idx, value in enumerate(outlist):
        categories[idx]["data"].append(value)

    log.setLevel(logging.INFO)
    return categories

def _getexposecategories(sensortype):
    """Return categories for a given sensor type

    :param sensortype: sensor type to work with
    """
    log.debug("Fetching Exposure for {0}".format(sensortype))
    if sensortype.name == "Temperature":
        serieslist = [{"name":"Potental Health <16C", "data":[],
                       "color": "#4575b4" },
                      {"name":"Cold <=18C", "data":[],
                       "color": "#adb9e9"},
                      {"name":"Comfort <=22C", "data":[],
                       "color": "#aab8bc"},
                      {"name":"Warm <=27C", "data":[],
                       "color": "#fee090"},
                      {"name":"Overheated >27C", "data":[],
                       "color": "#fc8d59"},
                      ]



    elif sensortype.name == "Humidity":
        serieslist = [{"name": "Dry < 45%", "data":[],
                       "color": "#2c7bb6"},
                      {"name": "Comfort <65%", "data":[],
                       "color": "#adb9e9"},
                      {"name": "Damp <=85%", "data":[],
                       "color": "#fdae61"},
                      {"name": "Risk > 85%", "data":[],
                       "color": "#d7191c"},
                      ]


    return serieslist

def fetchExposeData(start_date, end_date, sensortype, location_list):
    """Fetch Exposure data for a specific location

    :param startdate:  filter by start date
    :param enddate:    filter by end datetime
    :param sensortype: filter by sensor type
    :param location_list:  List of location ids to work with
    """


    log.debug("{0} EXPOSURE {0}".format("-"*25))
    log.debug("--> Type: {0}".format(sensortype))
    log.debug("--> Locations {0}".format(location_list))

    #Convert the sensorType to match the values stored in the DB
    theQry = DBSession.query(models.SensorType)
    theQry = theQry.filter_by(id = sensortype)

    thesensor = theQry.first()
    log.debug("Converted Sensor Type {0} == {1} {2}".format(sensortype,
                                                            thesensor,
                                                            thesensor.id))

    #Work out categories
    categories = _getexposecategories(thesensor)
    log.debug("Categories {0}".format(categories))

    #And a placeholder for location objects
    labels = []

    #Fetch and process the data for each Location
    for location in location_list:
        log.debug("-->--> Processing Location {0}".format(location))
                  #It is possible that a location has one or more nodes

        theQry = DBSession.query(models.Location).filter_by(id = location)
        theLocation = theQry.first()

        uniqueNodes = DBSession.query(sqlalchemy.distinct(models.Reading.nodeId))
        uniqueNodes = uniqueNodes.filter_by(locationId = location).all()
        log.debug("Unique Nodes {0}".format(uniqueNodes))


        if uniqueNodes is None or uniqueNodes == []:
            log.debug("No Nodes for location {0}".format(location))
            return

        #Otherwise we fetch the data
        #Location
        for node in uniqueNodes:
            qry = DBSession.query(models.Reading).filter_by(locationId = location)
            qry = qry.filter_by(typeId = thesensor.id) #Sensor Type
            qry = qry.filter_by(nodeId = node[0])

            #Start and End dates
            if start_date:
                log.debug("Filter Start Date")
                qry = qry.filter(models.Reading.time >= start_date)
            if end_date:
                log.debug("Filter End Date")
                qry = qry.filter(models.Reading.time <= end_date)

                log.debug(qry)

            #Work out 'Category' Label
            label = "({0}) {1}".format(node[0],
                                       theLocation.room.name)
            labels.append(label)

            log.debug("Category Label {0}".format(label))

            if thesensor.name == "Temperature":
                log.debug("Classifing based on temperture")

                categories = expose_temp(qry, categories, node[0])

            elif thesensor.name == "Humidity":
                log.debug("Classifing based on Humidity")
                categories = expose_humid(qry, categories, node[0])


    log.debug("List of Labels {0}".format(labels))
    log.debug("List of categories {0}".format(categories))
    return {"labels": labels,
            "series": categories,
            "title": "{0} Exposure Data".format(thesensor.name),
            "divid": sensortype}


def fetchLocationData(sensorType,
                      startDate,
                      endDate,
                      locationId,
                      sensorTypeId):
    """Fetch time series data for a specific location

    """

    theLocation = DBSession.query(models.Location).filter_by(id=locationId)
    theLocation = theLocation.first()

    log.debug("Searching for Location {0} == {1}".format(locationId,
                                                         theLocation))
    log.debug("--> Location Room {0}".format(theLocation.room))

    log.debug("Location is {0} ({1}".format(theLocation,
                                            locationId))

    uniqueNodes = DBSession.query(sqlalchemy.distinct(models.Reading.nodeId))
    uniqueNodes = uniqueNodes.filter_by(locationId = locationId).all()
    log.debug("Unique Nodes {0}".format(uniqueNodes))

    if uniqueNodes is None or uniqueNodes == []:
        log.debug("No Data for node {0}".format(theLocation))
        return [{"name":"{0} (no-data)".format(theLocation.room.name),
                "data":[]}]

    outList = []
    for nodeId in uniqueNodes:
        print "Sorting Node {0}".format(nodeId)
        theQry = DBSession.query(models.Reading).filter_by(locationId=locationId)
        theQry = theQry.filter_by(typeId = sensorTypeId)
        theQry = theQry.filter_by(nodeId = nodeId[0])
        theQry = theQry.order_by(models.Reading.time)

        log.debug("--> Start {0} End {1}".format(startDate, endDate))
        if startDate:
            log.debug("-- Filter to start {0}".format(startDate))
            theQry = theQry.filter(models.Reading.time >= startDate)
        if endDate:
            log.debug("-- Filter to End {0}".format(endDate))
            theQry = theQry.filter(models.Reading.time <= endDate)

        theCount = theQry.count()
        log.debug("The Query as SQL {0}".format(theQry))
        log.debug("Total Count of Samples {0}".format(theCount))
        if theCount == 0:
            log.debug("Location Room Name {0}".format(theLocation.room.name))
            log.debug("SensorType.name {0}".format(sensorType.name))
            theDict = {"name":"({0}) {1}<br>{2}".format(nodeId[0],
                                                        theLocation.room.name,
                                                        sensorType.name),
                       "data":[],
                       "id":"{0}_{1}".format(theLocation.houseId,theLocation.id),
                       "lineWidth": 0,
                       "marker":{"enabled":True, "radius":2},
                       }
        else:
            theGenerator = models.calibratePairs(theQry)
            theData = list(theGenerator)
            theDict = {"name":"({0}) {1}<br>{2}".format(nodeId[0],
                                                        theLocation.room.name,
                                                        sensorType.name),
                       "data":theData,
                       "id":"{0}_{1}".format(theLocation.houseId,
                                             theLocation.id),
                       "lineWidth": 0,
                       "marker":{"enabled":True, "radius":2}
                       }

            # #Check to see if this is SIP data.
            # if sensorType.id in [0, 2]:
            #     log.debug("--> Sensor Type is possible SIP")
            #     lastSample = theQry[-1]
            #     log.debug("--> Last Sample is {0}".format(lastSample))
            #     sipQry = DBSession.query(models.Reading)
            #     sipQry = sipQry.filter_by(time=lastSample.time,
            #                               nodeId=lastSample.nodeId,
            #                               typeId = lastSample.typeId+1,
            #                               locationId = lastSample.locationId)
            #     sipQry = sipQry.first()
            #     log.debug("Sip Query is {0}".format(sipQry))
            #     if sipQry:
            #         log.debug("Estimating SIP Values")
            #         #Get Calibrated version
            #         calib = lastSample.getCalibValues()
            #         log.debug("--> Calibrated {0}".format(calib))

            #         currentTime = datetime.datetime.now()
            #         lastTime = lastSample.time

            #         timeDiff = currentTime - sipQry.time
            #         if timeDiff.days > 0 or  timeDiff.seconds >= (60*60*8):
            #             timeDiff = datetime.timedelta(hours=8)
            #             #timeDiff = currentTime - datetime.timedelta(hours=8)
            #             lastTime = currentTime - timeDiff

            #         td = (timeDiff.seconds + (timeDiff.days * 24 * 3600))

            #         #Forward predict
            #         endValue = calib[1] + (sipQry.value * td)
            #         log.debug("--> Estimted Value is {0}".format(endValue))

            #         data = [[time.mktime(lastTime.timetuple())*1000.0,
            #                 calib[1]],
            #                [time.mktime(currentTime.timetuple())*1000.0,
            #                  endValue],
            #                ]
            #         log.debug("SIP Output is {0}".format(data))

            #         nodeStr = "({0}) {1}<br>{2}".format(nodeId[0],
            #                                             theLocation.room.name,
            #                                             sensorType.name)

            #         sipDict = {"name":nodeStr,
            #                    "data":data,
            #                    "dashStyle":"longdash",
            #                    #"marker":{"enabled":True, "radius":3}
            #                   }
            #         outList.append(sipDict)

        outList.append(theDict)
    outList.reverse()

    #return outList
    #Look for Events attacehd to this datastream
    log.debug("Location Details {0}".format(theLocation))
    events = DBSession.query(models.Event)
    events = events.filter_by(houseId = theLocation.houseId)
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
            log.debug("Time {0}  New {1}".format(evt.time, newTime))
            data.append({"x":newTime,
                         "title":evt.name})

        theDict["data"] = data
        log.debug("Data {0}".format(theDict))
        outList.append(theDict)
    log.debug("Data Processing Complete")
    #log.debug(outList)
    return outList

def jsonFetch(request):
    """New Location based time series data

    """
    log.debug("Fetching JSON Data")

    #Lets split out the bits we definately know about
    paramDict = request.GET.mixed()
    log.debug("--> Parameter Dictionary {0}".format(paramDict))

    graphType = paramDict.get("graphType","time")
    log.debug("Graph Type {0}".format(graphType))

    if graphType == "time":
        return _fetchTimeData(request, paramDict)
    elif graphType == "expose":
        return _fetchExposeData(request, paramDict)


def _fetchTimeData(request, paramDict):
    """Fetch and Process time seris data"""
    log.debug("--> Fetching Time Series Data")

    #Parse the Paramdict
    sensorType = paramDict.get("sensorType", None)
    startDate = paramDict.get("startDate", None)
    endDate = paramDict.get("endDate", None)
    deployments = paramDict.get("deployments", None)
    houses = paramDict.get("houses", None)
    locations = paramDict.get("locations", None)
    locType = paramDict.get("locType", None)

    if sensorType == "":
        sensorType = None
    if startDate:
        startDate = dateutil.parser.parse(startDate)
    if endDate:
        endDate = dateutil.parser.parse(endDate)

    log.debug("-------------------------------------------")
    log.debug("Sensor Type: {0}".format(sensorType))
    log.debug("Date Range: {0} -> {1}".format(startDate, endDate))
    log.debug("Deployments: {0}".format(deployments))
    log.debug("Houses: {0}".format(houses))
    log.debug("Locations: {0}".format(locations))
    log.debug("Loc Type: {0}".format(locType))
    log.debug("-------------------------------------------")
    #If a house / deployment is selected, and no sensor type Given
    #Then limit our results to temperture only.

    if houses or deployments:
        if sensorType is None:
            log.debug("--> Limit to Temperature Data")
            sensorType = 0

        #TODO Write code to add all locations to "locations"

    #Build the list of datastreams we want to deal with
    sensorList = []

    #Individual Sensors (Ie Location + Type)
    if locType:
        if type(locType) == list:
            sensorList.extend(locType)
        else:
            sensorList.append(locType)

    #Locations (Ie All Sensors at this location)
    if locations:
        if type(locations) == unicode:
            locations = [locations,]
        for item in locations:
            log.debug("--> Dealing with location {0}".format(item))
            #Find all nodes attached to this location

            theQry = DBSession.query(models.Location).filter_by(id = item).first()
            log.debug("The Location is {0}".format(theQry))
            #All nodes that have been registered with this location

            for node in theQry.allnodes:
                #Work out Sensors
                log.debug("--> Node {0} Associated".format(node))
                if sensorType:
                    locString = "{0},{1}".format(item, sensorType)
                    if locString in sensorList:
                        continue
                    else:
                        sensorList.append(locString)
                else:
                    for sensor in node.sensors:
                        log.debug("--> --> Sensor {0}".format(sensor))
                        locString = "{0},{1}".format(item, sensor.sensorTypeId)
                        log.debug( "Loc String is {0}".format(locString))
                        if locString in sensorList:
                            continue
                        else:
                            sensorList.append(locString)
            log.debug("Associated Nodes {0}".format([x.id for
                                                     x in theQry.allnodes]))

    log.debug("Sensor List is > {0}".format(sensorList))

    #Actually fetch the data
    #Series needs to be [{name:xxx, data:[(0,0),(1,1)]},...]
    outSeries = []
    for item in sensorList:
        locId,typeId = item.split(",")
        log.debug("Fetch Data for {0} = {1} / {2}".format(item, locId, typeId))
        theSensor = DBSession.query(models.SensorType).filter_by(id = typeId)
        theSensor = theSensor.first()
        log.debug("--> Sensor {0}".format(theSensor))
        seriesData = fetchLocationData(theSensor,
                                       startDate,
                                       endDate,
                                       locId,
                                       typeId)

        outSeries.extend(seriesData)

    return {"series": outSeries}


# ----------------------------------------------------------------------
#
#                              EXPOSURE
#
# ----------------------------------------------------------------------


def _fetchExposeData(request, paramDict):
    """Fetch and Process data for an Exposure Graph"""

    log.debug("--> Fetching Exposure Data")

    sensorType = paramDict.get("sensorType", None)
    startDate = paramDict.get("startDate", None)
    endDate = paramDict.get("endDate", None)
    deployments = paramDict.get("deployments", None)
    houses = paramDict.get("houses", None)
    locations = paramDict.get("locations", [])
    locType = paramDict.get("locType", [])

    if sensorType == "":
        sensorType = None
    if startDate:
        startDate = dateutil.parser.parse(startDate)
    if endDate:
        endDate = dateutil.parser.parse(endDate)

    log.debug("-"*50)
    log.debug("Sensor Type: {0}".format(sensorType))
    log.debug("Date Range: {0} -> {1}".format(startDate, endDate))
    log.debug("Deployments: {0}".format(deployments))
    log.debug("Houses: {0}".format(houses))
    log.debug("Locations: {0}".format(locations))
    log.debug("Loc Type: {0}".format(locType))
    log.debug("-"*50)

    #Get the Houses / Locations
    if type(locations) == list:
        locationList = locations
    else:
        locationList = [locations]

    if type(locType) != list:
        locType = [locType]

    #Work out sensor types
    #if type(sensorType) != list:
    #    sensorType = [sensorType]
    sensorType = [int(x) for x in sensorType]
    log.debug("Initial Sensor Type {0}".format(sensorType))
    for item in locType:
        log.debug(item)
        locId, typeId = item.split(",")
        typeId = int(typeId)
        if locId not in locationList:
            log.debug("Appending Location {0}".format(locId))
            locationList.append(locId)
        #if typeId not in sensorType:
        #    log.debug("Appending Id")
        #    sensorType.append(typeId)


    #And Fetch all locations attached to a house
    if houses:
        log.debug("House Specified {0}".format(houses))
        #Fetch all locations associated with this house
        theQry = DBSession.query(models.Location).filter_by(houseId = houses)
        locationList.extend([x.id for x in theQry.all()])

    log.debug("Location List {0}".format(locationList))

    #Map Sensor types correctly

    #So fetch the details for each sensor type
    outGraphs = []
    for sensor in sensorType:
        sensor = int(sensor)
        log.debug("Fetching Exposure Data for Sensor {0}".format(sensor))
        out = fetchExposeData(startDate, endDate, sensor, locationList)

    return out

    # ----------------------------------------------------------
    #treeItems = paramDict.get("treeItems",None)

def jsonnav(request):
    """Return a json representation of the information stored in the database,
    this can then be used for navigation etc."""

    log.debug("Json Nav")

    sTypes = []
    typeQuery = DBSession.query(models.SensorType).all()
    for item in typeQuery:
        #sTypes.append(item.asJSON())
        sTypes.append({"id":item.id,
                       "name":item.name,
                       "type":"sensor"})

    theData= {"identifier" : "id",
              "label" : "name",
              "items" : sTypes}

    return theData
