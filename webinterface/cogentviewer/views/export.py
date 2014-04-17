"""
Module for exporting data.




"""


import time
import datetime
from itertools import groupby

from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import view_config
import pyramid.url

import sqlalchemy

import subprocess

import logging
LOG = logging.getLogger(__name__)

import cogentviewer.models.meta as meta
import cogentviewer.models as models
#import cogentviewer.views.homepage
import homepage

import pandas
import dateutil.parser

#MAGIC NUMBERS THAT NEED TO BE FUCKED OFF
PULSE_PER_UNIT = 1000
VOLUME_FACTOR = 1.022640
CALORIFIC_FACTOR = 39.3
KWH_CONVERSION  =3.6

@view_config(route_name='export', renderer='cogentviewer:templates/export.mak',permission="view")
def exportdata(request):
    """
    View that allows exporting of data.
    """

    #session = meta.Session)
    #deployments = session.query(models.deployment.Deployment).all()

    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)
    outDict["pgTitle"] = "Export"
    theUser = homepage.getUser(request)
    outDict["user"] = theUser.username

    LOG.debug(request.POST)

    session = meta.Session()

    if "submit" in request.POST:
        LOG.debug("Dealing with form submission")

        #Fetch the House Id
        houseId = request.POST.get("houseId")
        LOG.debug("--> House Id {0}".format(houseId))
        if houseId is None or houseId == "":
            LOG.warning("No House Supplied")
            outDict["warnings"] = "You must supply a house"
            return outDict
            #houseId = 26
        #else:
        #    houseId = int(houseId)

        #Do we want to examine all rooms
        allRooms = request.POST.get("allrooms") == "on"
        LOG.debug("--> Do All Rooms {0}".format(allRooms))
        if allRooms:
            LOG.debug("--> All Rooms checked")
            locids = None
        else:
            ##Otherwise work out what room we wish to do.
            LOG.debug("--> Select rooms  from List")
            locids = request.POST.getall("locids")

        LOG.debug("--> Locations {0}".format(locids))

        #Sensors to get
        sensors = request.POST.getall("stype")
        LOG.debug("--> Sensors {0}".format(sensors))
        if sensors is None:
            LOG.debug("--> Default to just Temperature sensors")
            sensorlist = [0]
        else:
            #for sensor in sensors:
            LOG.debug("--> Processing Sensor Types")
            sensorlist = []
            for sensor in sensors:                   
                theQry = session.query(models.SensorType).filter_by(name=sensor).first()
                LOG.debug("--> --> Processing Type {0} = {1}".format(sensor,theQry))
                if theQry:
                    sensorlist.append(int(theQry.id))

            #Append Pulse outputs
            if "Power" in sensors:
                theQry = session.query(models.SensorType).filter_by(name="Opti Smart Count").first()
                if theQry:
                    sensorlist.append(int(theQry.id))

            LOG.debug("--> Final Sensor List {0}".format(sensorlist))


        #Aggregate
        aggregate = request.POST.get("aggregate")
        LOG.debug("--> Aggregate {0}".format(aggregate))
        if aggregate == "aggregate5":
            aggregate = "5Min"
        elif aggregate == "aggregate15":
            aggregate = "15Min"
        elif aggregate == "aggregate30":
            aggregate = "30Min"
        elif aggregate == "aggregateHour":
            aggregate = "1H"
        elif aggregate == "aggregateDaily":
            aggregate = "1D"
        else:
            aggregate = None
        
        #Aggregate parameters
        aggparam = request.POST.getall("agg-param")
        LOG.debug("--> Aggregate Parameters {0}".format(aggparam))

        #Start and Stop dates
        sdate = request.POST.get("startdate")
        edate = request.POST.get("stopdate")
        LOG.debug("start {0} Stop {1}".format(sdate,edate))
        startdate = None
        enddate = None
        if sdate:
            startdate = dateutil.parser.parse(sdate,dayfirst=True)
        if edate:
            enddate = dateutil.parser.parse(edate,dayfirst=True)
        LOG.debug("Start {0} End {1}".format(startdate,enddate))

        interpolate = request.POST.get("interp")
        LOG.debug("--> Interpolate {0}".format(interpolate))
        

        #Try the string export
        LOG.debug("--> Setup Download")
        #theDf = processExport(houseId
        theDf = processExport(houseId = houseId,
                              locationIds = locids,  
                              typeIds = sensorlist,
                              aggregate = aggregate,
                              aggregateby = aggparam,
                              startDate = startdate,
                              endDate = enddate,
                              interpolate = interpolate,
                              )

        #LOG.debug(theDf)
        #LOG.debug(theDf.head())
        LOG.debug("Data Returned")
        if type(theDf) == dict:
            outDict["warnings"] = "No valid data of this type"
            return outDict
        else:
            request.override_renderer = "pancsv"
            return {"data":theDf}

        
    return outDict

def processExport(houseId,
                  locationIds=None,
                  typeIds=None,
                  startDate = None,
                  endDate =None,
                  aggregate=None,
                  aggregateby=None,
                  interpolate=None):
    """Process data for Export as a CSV file.

    This function will fetch the sepecifed data from the DB and reformat it ready for export as CSV.
    
    :param houseId:  Id of house to fetch data for
    :param locationIds: List of location Ids that we want to fetch data for. Defaults to all locations at the house
    :param typeIds: List of sensor type Ids 
    :startDate: String representation of the date to start fetching data in DD-MM-YYYY (HH:MM)
    :endDate: String represetnation of cutoff date in DD-MM-YYYY (HH:MM)
    :aggregate: Aggregate Data.  Accepts a Pandas Time string (ie 5Min)
    :aggregateby: Either a string or list of strings for summary statistics ie "mean" or ["mean","min","max"]
    :interpolate: Interpolate missing values (currently just linear interpolation)

    :return: A pandas dataframe representing this data
    """
    
    session = meta.Session()
    theqry = session.query(models.House)
    theqry = theqry.filter_by(id = houseId)

    theHouse = theqry.first()
    LOG.debug("Checking Houses with Id {0}".format(houseId))
    LOG.debug("--> {0}".format(theHouse))


    #Filter by Location
    if locationIds:
        locIds = locationIds
    else:
        locations = theHouse.locations
        locIds = [x.id for x in locations]
    LOG.debug("--> locations Ids {0}".format(locIds))

    dataqry = session.query(models.Reading).filter(models.Reading.locationId.in_(locIds))

    #Do we want to limit to certain sensor type
    if typeIds:
        typelist = typeIds
    else:
        typelist = [0,2,4,5,6,8,9,11,15,16]        

    LOG.debug("Filter By Sensor Types: {0}".format(typelist))
    dataqry = dataqry.filter(models.Reading.typeId.in_(typelist))


    #By Start and End Data
    if startDate:
        dataqry = dataqry.filter(models.Reading.time >= startDate)
    if endDate:
        dataqry = dataqry.filter(models.Reading.time <= endDate)
    
    dataqry = dataqry.order_by(models.Reading.time)
    #print dataqry
    #if limit:
    #    dataqry = dataqry.limit(limit)

    LOG.debug("Query is {0}".format(dataqry))
    LOG.debug("No of Samples {0}".format(dataqry.count()))
    if dataqry.count() == 0:
        return {}

    dataList = list(models.reading.calibPandas(dataqry))
    #print dataList
    #print dataList
    df = pandas.DataFrame(dataList)
    #print df.head()
    #print df.tail()
    
    #df.to_pickle('rawdata.pkl')

    #Before we make this wide we want to append any current stuff
    df = calculateCurrent(df,aggregate)
    df = calculateGasPulse(df,aggregate)

    df.to_csv("rawdata.csv")    

    #Turn into a "wide" version
    wide = df.pivot(index='time',columns="location",values="value")
    #wide.head()

    #Resample ?
    #wide.resample("10Min")



    if aggregate:
        LOG.debug("== Aggregate {0}".format(aggregate))
        if aggregateby:
            LOG.debug("== Aggregate By {0}".format(aggregateby))
            resample =  wide.resample(aggregate,how=aggregateby)
        else:
            resample =  wide.resample(aggregate)    
    else:   
        resample =  wide

    if interpolate:
        resample = resample.apply(pandas.Series.interpolate)

    return resample
    #This may be useful to reindex or whatever
    #for item in models.reading.calibPandas(dataqry):
    #    tmpIdx.append(item["time"])
    #    tmpLoc.append(item["location"])
    #    tmpList.append(item["value"])

    #print "tmpList=",tmpList
    #print "tmpLoc=",tmpLoc
    #print "tmpIdx=",tmpIdx
    #out = pandas.DataFrame(tmpList,index=[tmpIdx,tmpLoc],columns=["value"]) #We dont need the time index here if we do a pivot
    #out = pandas.DataFrame(tmpList)
    #out["nodestr"] = "{0}_{1}".format(out["nodeId"],out["typeId"])
    #LOG.debug("--")
    #LOG.debug("\n{0}".format(out))
    #LOG.debug("=====")
    #piv = out.pivot(index='time',columns="location",values="value")
    #LOG.debug(piv)
    #theData = 

    #for item in locations:
    #    LOG.debug(item)

def calcualteElecPusle(df,aggregate=None):
    """Calculate electric pulses"""
    LOG.debug("--> Converting Electric Pulses")

    session = meta.Session()
    theQry  = session.query(models.SensorType).filter_by(name="Opti Smart Count").first()
    if theQry is None:
        LOG.warning("No optismart sensor in Db")
        return df

    pulseId = theQry.id

    pulse = df[df["typeId"] == pulseId]
    if len(pulse) == 0:
        LOG.debug("---- No Electric  Pulse Data ----")
        return df

    #Otherwise do the calculations
    pulse["count"] = pulse["value"] - pulse["value"].shift()    
    pulse["kwh"] = pulse["count"] / PULSE_PER_UNIT

    locationStr = pulse.iloc[0]['location']

    #Deal with counts
    outpulse = pulse[["time","count"]]
    outpulse.rename(columns={"count":"value"},inplace=True)
    outpulse["location"] = "{0} (Count)".format(locationStr)
    df = df.append(outpulse)

    if aggregate:
        tmppulse = outpulse
        tmppulse.index = tmppulse["time"]
        tmppulse= tmppulse.resample(aggregate,how="max")
        tmppulse["time"] = tmppulse.index
        tmppulse["location"] = "{0} (Count Maximum)".format(locationStr)
        df = df.append(tmppulse) 

    #And KwH
    outpulse = pulse[["time","kwh"]]
    outpulse.rename(columns={"kwh":"value"},inplace=True)
    outpulse["location"] = "{0} (Kwh)".format(locationStr)
    df = df.append(outpulse)

    if aggregate:
        tmppulse = outpulse
        tmppulse.index = tmppulse["time"]
        tmppulse= tmppulse.resample(aggregate,how="sum")
        tmppulse["time"] = tmppulse.index
        tmppulse["location"] = "{0} (kWh Cumulative)".format(locationStr)
        df = df.append(tmppulse) 


def calculateGasPulse(df,aggregate=None):
    """Convert gas pulses to kWh"""
    LOG.debug("--> Converting Gas")

    session = meta.Session()
    theQry  = session.query(models.SensorType).filter_by(name="Gas Pulse Count").first()

    if theQry is None:
        LOG.warning("No Gas Pulse Sensor in Db")
        return df
    pulseId = theQry.id

    gas = df[df["typeId"] == pulseId] #43
    if len(gas) == 0:
        LOG.debug("---- No Gas Pulse Data ----")
        return df


    gas["count"] = gas["value"] - gas["value"].shift()
    gas["mcubed"] = gas["count"] / PULSE_PER_UNIT
    gas["kwh"] = (gas["mcubed"] * VOLUME_FACTOR * CALORIFIC_FACTOR) / KWH_CONVERSION
    #LOG.debug(gas.head())    
    #print gas.head()
    locationStr = gas.iloc[0]['location']

    #Deal with counts
    outgas = gas[["time","count"]]
    outgas.rename(columns={"count":"value"},inplace=True)
    outgas["location"] = "{0} (Count)".format(locationStr)
    df = df.append(outgas)

    if aggregate:
        tmpgas = outgas
        tmpgas.index = tmpgas["time"]
        tmpgas= tmpgas.resample(aggregate,how="max")
        tmpgas["time"] = tmpgas.index
        tmpgas["location"] = "{0} (Count Maximum)".format(locationStr)
        df = df.append(tmpgas) 

    # outgas = gas[["time","mcubed"]]
    # outgas.rename(columns={"mcubed":"value"},inplace=True)
    # outgas["location"] = "{0} (M3)".format(locationStr)
    # df = df.append(outgas)    

    # if aggregate:
    #     tmpgas = outgas
    #     tmpgas.index = tmpgas["time"]
    #     tmpgas= tmpgas.resample(aggregate,how="sum")
    #     tmpgas["time"] = tmpgas.index
    #     tmpgas["location"] = "{0} (MCubed Cumulative)".format(locationStr)
    #     df = df.append(tmpgas) 

    #And kWh
    outgas = gas[["time","kwh"]]
    outgas.rename(columns={"kwh":"value"},inplace=True)
    outgas["location"] = "{0} (Kwh)".format(locationStr)
    df = df.append(outgas)

    if aggregate:
        tmpgas = outgas
        tmpgas.index = tmpgas["time"]
        tmpgas= tmpgas.resample(aggregate,how="sum")
        tmpgas["time"] = tmpgas.index
        tmpgas["location"] = "{0} (kWh Cumulative)".format(locationStr)
        df = df.append(tmpgas) 



    return df
    
    
def calculateCurrent(df,aggregate=None):
    """Convert Current Readings to kWh
    
    :param df: Dataframe containing readings to work with
    :param aggregate: Any aggregtions (so we can sum readings)
    """

    #Focus only on Electricity Data
    elec = df[df["typeId"]==11]
    if len(elec) == 0:
        LOG.debug("------- NO POWER DATA -------")
        return df

    #Calculate the Delta
    elec["delta"] = elec["time"] - elec["time"].shift()
    #Do the Conversion
    elec["kWh"]  = elec.apply(currentFunc,axis=1)

    outelec = elec[["location","time","kWh"]]
    #outelec.colums = ["location","time","value"]
    outelec.rename(columns={"kWh":"value"},inplace=True)

    #Append the kWh
    outelec["location"] = outelec["location"].map(lambda x: "{0} (kWh)".format(x))
    df = df.append(outelec)
    

    locationStr = elec.iloc[0]['location']
    if aggregate:
        tmpelec = outelec 
        tmpelec.index = tmpelec["time"]
        tmpelec= tmpelec.resample(aggregate,how="sum")
        tmpelec["time"] = tmpelec.index
        tmpelec["location"] = "{0} (kWh Cumulative)".format(locationStr)
        df = df.append(tmpelec) 

    return df


def currentFunc(theRow):   
    delta = theRow["delta"]
    if delta is None:
        return

    kW = theRow["value"] / 1000.0
    #Convert from nanoseconds
    delta =  delta / 1000000000.0
    #And to Hours
    hours = delta / (60*60)
    return hours / kW
    #delta = s["delta"]
    #value = s["value"]
