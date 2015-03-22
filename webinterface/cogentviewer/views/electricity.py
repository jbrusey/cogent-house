"""
Deal with Electriricty Data
"""

from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import view_config

import logging
log = logging.getLogger(__name__)

import homepage
from ..models.meta import DBSession
import cogentviewer.models as models
import time

@view_config(route_name='electricity', renderer='cogentviewer:templates/electricity.mak',permission="view")
def electricity(request):
    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)
    theUser = homepage.getUser(request)
    outDict["user"] = theUser.username

    outDict["pgTitle"] = "Electricity Data"
    #outDict["deployments"] =deps

    outDict["nodeDropdowns"] = homepage.getNodeDropdowns()

    return render_to_response('cogentviewer:templates/electricity.mak',
                              outDict,
                              request=request)


def getStats(theQry):
    outList = []
    lastTime = None
    for item in theQry:
        time = item.time
        value = item.value
        tDiff = "NA"
        wH = "NA"
        if lastTime is None:
            lastTime = time
            pass
        else:
            tDiff = (time-lastTime).total_seconds()
            tDiff = tDiff / 3600 #Turn this into Hours
            lastTime = time
            wH = value * tDiff #/ 1000.0

            outList.append([time,value,tDiff,wH])
    
    return outList

def getStatsHour(theQry):
    outList = []
    lastTime = None
    lastHour = None
    cumWatts = 0.0

    NA = "NA"


    for item in theQry:
        #log.debug(item)
        theTime = item.time
        value = item.value
        tDiff = "NA"
        wH = "NA"
        if lastTime is None:
            lastTime = theTime
            lastHour = theTime
            outList.append([time.mktime(theTime.timetuple()),value,0.0,0.0])
            continue
        


        #log.debug(theTime.hour - lastHour.hour)
        tDiff = (theTime-lastTime).total_seconds()
        lastDiff = (theTime-lastHour).total_seconds()
        tHours = tDiff / 3600 #Turn this into Hours
        lastTime = theTime
        wH = value * tHours #/ 1000.0
        cumWatts += wH
        
        #Sumnmarise by Hour
        if lastDiff >= 3600*24:
            lastHour = theTime
            pass

        outList.append([time.mktime(theTime.timetuple()),value,tDiff,wH])    

    #for item in outList:
    #    print item
    #import pprint
    #pprint.pprint(outList)
    return outList





def getElec(request):
    # #For quickness
    readings = DBSession.query(models.Reading).filter_by(locationId = 8,
                                                       typeId = 11)
    readings = readings.order_by(models.Reading.time.asc())
    log.debug("COunt of Readings {0}".format(readings.count()))
    #readings = readings.limit(10)
    #values = [[x.time,x.value] for x in readings]

    
    #headers = ["time","value","Diff","wH"]
    #values = getStats(readings)


                
    headers = ["time","value","diff","wH"]
    values = getStatsHour(readings)

    outDict = {"header":headers,"rows":values}
    return outDict
    # #return readings.all()
    # outReadings = [[x.time.isoformat(),x.value] for x in readings]
    # #return outReadings
    # return Response(

def getPv(request):
    headers=["time","pulse","diff"]

    readings = DBSession.query(models.Reading).filter_by(typeId= 20,
                                                 locationId = 3)
    readings = readings.order_by(models.Reading.time.asc())
    
    #Strip out the Values
    #readings = readings.limit(10)

    #for item in readings:
    #    print item
    values = []
    lastTime = None
    for x in readings:
        if lastTime is None:
            timeDiff = 0.0
        else:
            timeDiff = (x.time - lastTime).total_seconds()
        values.append([time.mktime(x.time.timetuple()),x.value,timeDiff])
        lastTime = x.time

    #values = [[x.time,x.value] for x in readings]
    #values = []
    outDict = {"header":headers,
               "rows":values,
               "fName":"pv.csv"}
    return outDict
