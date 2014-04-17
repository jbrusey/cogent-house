"""
Node Status and Admin
"""

import time
import datetime
import logging

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.WARNING)

from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import view_config
import pyramid.url

import sqlalchemy

import pandas
import numpy

import homepage
import cogentviewer.models as models
import cogentviewer.models.meta as meta

SAMPLE_RATE_MINUTES = 5.0
SAMPLE_RATE_DAY = (60*24) / SAMPLE_RATE_MINUTES

@view_config(route_name='yield',
             renderer='cogentviewer:templates/yield.mak',
             permission="view")
def yieldpage(request):
    """Display the Yield Homepage"""
    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)
    theUser = homepage.getUser(request)
    outDict["user"] = theUser.username
    outDict["pgTitle"] = "Yield Report"
    #outDict["deployments"] =deps
    outDict["nodeDropdowns"] = homepage.getNodeDropdowns()

    #And actual page logic

    summarytable = {"totalhouses":0,
                    "totalnodes":0,
                    "nodes90":0,
                    "nodestoday":0}


    yieldtable = []
    #So we first want the list of houses
    session = meta.Session()
    houses =  session.query(models.House).filter(models.House.address!="Test")
    #houses =  session.query(models.House).filter_by(address ="69 longford road")
    #houses =  session.query(models.House).filter_by(address ="c4 59 radnormere drive")

    now = datetime.datetime.now()
    #now = datetime.datetime(2013,11,18,15,00,00)

    for house in houses:
        houseyield = {"house":house.address}
        summarytable["totalhouses"] += 1
        nodeyields = []
        #We then fetch the nodes
        nodeids, nodedesc  = queuenodes(house.id)
        yieldsum = 0.0
        #for node in nodedesc:
        for node in nodedesc:
            #if node["nodeid"] != 65:
            #    continue
            summarytable["totalnodes"] += 1
            yieldrow = {
                        "nodeid": node["nodeid"],
                        "room": node["room"]}
            #And work out yields
            #yieldinfo = calcyield(node["nodeid"],startdate=datetime.datetime(2013,11,5,00,00,00))
            yieldinfo = calcyield(node["nodeid"],startdate=datetime.datetime(2013,12,1,00,00,00))
            yieldrow["lasttx"] = yieldinfo[0]
            #Class  /Highlighting for the last transmision

            if type(yieldinfo[0]) == pandas.tslib.Timestamp:
                lasttx_delta = now - yieldinfo[0]
                if lasttx_delta.days <= 1:
                    yieldrow["txclass"] = "text-success"
                    summarytable["nodestoday"] += 1
                elif lasttx_delta.days <= 3:
                    yieldrow["txclass"] = "text-warning"
                elif lasttx_delta.days > 3:
                    yieldrow["txclass"] = "text-error"
                else:
                    yieldrow["txclass"] = "text-success"
            else:
                yieldrow["txclass"] = "text-info"

            yieldrow["datayield"] = yieldinfo[1]
            yieldrow["packetyield"] = yieldinfo[2]

            if yieldinfo[1] > 90:
                summarytable["nodes90"] += 1

            if yieldinfo[2] != "N/A" :
                yieldsum += yieldinfo[2]
            nodeyields.append(yieldrow)

        #avgyield = yieldsum / len(nodedesc)
        avgyield = "N/A"

        houseyield["data"] = nodeyields
        houseyield["avg"] = avgyield

        yieldtable.append(houseyield)

    outDict["yieldtable"] = yieldtable
    outDict["summarytable"] = summarytable
    exportYield()
    return outDict

def exportYield():
    """Exports yield as a pandas object"""
    yieldtable = []
    #So we first want the list of houses
    session = meta.Session()
    houses =  session.query(models.House).filter(models.House.address!="Test")
    #houses =  session.query(models.House).filter_by(address ="f1 16 redfern house")

    for house in houses:
        #houseyield = {"house":house.address}
        #nodeyields = []
        #We then fetch the nodes
        nodeids, nodedesc  = queuenodes(house.id)
        #yieldsum = 0.0
        for node in nodedesc:
            yieldrow = {"houseid": house.id,
                        "house":house.address,
                        "nodeid": node["nodeid"],
                        "room": node["room"]}
            #And work out yields
            yieldinfo = calcyield(node["nodeid"], startdate=datetime.datetime(2013,11,4,00,00,00))
            #yieldinfo = calcyield(node["nodeid"])
            yieldrow["lasttx"] = yieldinfo[0]
            yieldrow["yield"] = yieldinfo[1]
            yieldtable.append(yieldrow)

    #outDict["yieldtable"] = yieldtable
    df = pandas.DataFrame(yieldtable)
    df.to_csv("yieldreport.csv")

def queuenodes(houseid):
    """
    Helper method to fetch and queue nodes for each houses
    Yield report.

    This will return a tuple containing:
    1) List of nodesId's in each deployment
    2) List of dictionary discriptions to generate yield table

    Desctiption takes the form of {nodeId, locationId, room}

    :param houseid:  Id of house we want to fetch data for

    :return: [[NodeIds],[{Node Description}]]
    """

    nodelist = [] #Containers for output
    desclist = []


    session = meta.Session()

    thehouse = session.query(models.House).filter_by(id=houseid).first()

    #nodes associated with this house
    locations = thehouse.locations


    LOG.debug("Locations:")
    for location in locations:
        LOG.debug("--> {0}".format(location))
        #See if the location has a node associated with it

        for node in location.nodes:
            LOG.debug("--> --> {0}".format(node))
            nodelist.append(node.id)
            desclist.append({"nodeid":node.id,
                             "locationid":location.id,
                             "room":location.room.name})

    #We can also have the case where the node has been incorrectly setup
    #Hopefully we can remove this code at some point

    locids = [x.id for x in locations]
    qry = session.query(models.Reading.nodeId, models.Reading.locationId)
    qry = qry.filter(models.Reading.locationId.in_(locids))
    qry = qry.distinct()

    LOG.debug(" From Query ")
    for item in qry:
        LOG.debug("{0}".format(item))
        nodeid, locationid = item
        if nodeid in nodelist:
            #If we allready know about it
            continue

        location = session.query(models.Location).filter_by(id=locationid)
        location = location.first()
        nodelist.append(nodeid)
        desclist.append({"nodeid":nodeid,
                         "locationid":locationid,
                         "room":location.room.name})


    return nodelist, desclist

def calcyield(nodeid, startdate=None, enddate=None):
    """
    Method to calcualate Yield for a given node Id

    This will return a dictionaty containing various yield
    Statistics

    {firstTx,
     lastTx,
     number of samples,
     data yield (calculated based on "good" data)
     packet yield (based on number of packets)
     }

    :param nodeId:  Id of node we want to calcualte yield for
    :param startdate: Date to limit start of yield to
    :param enddate: Date to limit end of yield to
    :return:  Dictionary containing Yield Statistics
    """

    
    LOG.debug("{1} CALCUALTE YIELD FOR NODE {0} {1}".format(nodeid,"="*20))

    lastsample = None
    datayield = 0
    packetyield = 0

    outdict = {}

    #Fetch samples
    session = meta.Session()
    qry = session.query(models.NodeState).filter_by(nodeId = nodeid)
    qry = qry.filter(models.NodeState.seq_num != None)
    qry = qry.order_by(models.NodeState.time)
    if startdate:
        qry = qry.filter(models.NodeState.time >= startdate)
    if enddate:
        qry = qry.filter(models.NodeState.time <= enddate)
    
    qry = qry.group_by(models.NodeState.time, models.NodeState.seq_num)


    #Convert to pandas
    df = pandas.DataFrame([x.pandas() for x in qry])
    #df.to_pickle("nodestate.pkl")

    if len(df) == 0:
        LOG.warning("No Data for this node {0}")
        return "No Data", 0.0, 0.0
    elif len(df) == 1:
        LOG.warning("Single Sample for this Node")
        return df.irow(-1)["time"], 0.0, 0.0

    firstsample = df.irow(0)["time"]
    lastsample = df.irow(-1)["time"]

    duration = lastsample - firstsample
    #Work out how many are expected for complete days
    expected = duration.days * SAMPLE_RATE_DAY 
    expected += duration.seconds / (SAMPLE_RATE_MINUTES*60)

    LOG.debug("First {0} Last {1} Duration {2} Expected {3}".format(firstsample,
                                                                    lastsample,
                                                                    duration,
                                                                    expected))
    if expected < 1.0:
        LOG.warning("Single Sample for th")
        return lastsample, "N/A", "N/A"


    """
    #So the simple way of calculating packetyield is
    # Nrows / Rxpected * 100.0
    # This should give us the "compression factor"
    """

    nrows = float(len(df))
    LOG.debug("{0} Compression Factor {0}".format("-"*10))
    LOG.debug("Nrows {0} Expected {1}".format(len(df), expected))

    packetyield = (len(df) / expected) * 100.0

    LOG.debug("Compression Factor {0} {1} {2}".format(len(df),
                                                      expected,
                                                      packetyield))

    """
    And packet yield is
    Total Packets - (Diff Sequence > 1)
    """

    #Calculate Diffs
    df["time_dif"] = df.time.diff()
    df.time_dif = df.time_dif.fillna(0)
    #df["expected"] = df.time.diff.total_seconds() / (5*60)
    df["seq_dif"] = df.seq_num.diff()
    df.seq_dif = df.seq_dif.fillna(1)
    df["expected"] = df.time_dif.apply(lambda x : round(x / numpy.timedelta64(datetime.timedelta(minutes=5))),0)
    df["new_dif"] = df.seq_dif

    #Check if the localtime is not ascending
    df["localtime_diff"] = df.localtime.diff()

    #Work out the time difference when we wrap around
    df.new_dif[df.new_dif < 0] = 255 + df.new_dif
    df["bad_samples"] = df.new_dif - 1
    df["good_samples"] = df.expected - df.bad_samples

    #For the moment, I am going to assume that all the data up to the reset is Good.
    df.good_samples[df.localtime_diff < 0] = df.expected
    df.bad_samples[df.localtime_diff < 0] = 0

    #And if we have more than 8 hours of data between samples (96)
    LOG.debug("Total with more than 8 hours of data {0}".format(len(df[df.good_samples>96])))
    df.bad_samples[df.good_samples > 96] =  df.good_samples
    df.good_samples[df.good_samples > 96] = 0


    #Delivered Packets
    delivered = len(df)
    totalretries = len(df[df.new_dif > 1])
    LOG.debug("--> Total Retries {0}".format(totalretries))
    failed = df.new_dif[df.new_dif > 1].sum() - totalretries

    sumgood = df.good_samples.sum()
    sumbad = df.bad_samples.sum()
    datayield = sumgood / expected * 100.0

    # LOG.debug("--------")
    # print df.head()
    # LOG.debug("Delivered Packets {0}".format(delivered))
    # LOG.debug("Failed Packets {0}".format(failed))


    # packetyield = (1 - (failed / expected)) * 100.0
    LOG.debug("Deliviered {0} Failed {1} Good {2}  Bad {3} Yield {4}".format(delivered,
                                                                             failed,
                                                                             sumgood,
                                                                             sumbad,
                                                                             datayield))
    df.to_csv("yielddumpOrd.csv")
    df.to_pickle("yielddumpOrd.pkl")
    return lastsample, datayield, packetyield




def calcyieldNew(nodeid, startdate=None, enddate=None):
    """
    Alternate method of calculating Yield

    Method to calcualate Yield for a given node Id.
    Upto the current date

    This will return a dictionaty containing various yield
    Statistics



    {firstTx,
     lastTx,
     number of samples,
     data yield (calculated based on "good" data)
     packet yield (based on number of packets)
     nodeResets (How many times the local clock has moved backwards)
     }

    :param nodeId:  Id of node we want to calcualte yield for
    :param startdate: Date to limit start of yield to
    :param enddate: Date to limit end of yield to
    :return:  Dictionary containing Yield Statistics
    """

    
    LOG.debug("{1} CALCUALTE YIELD FOR NODE {0} {1}".format(nodeid,"="*20))

    lastsample = None
    datayield = 0
    packetyield = 0

    outdict = {}

    #Fetch samples
    session = meta.Session()
    qry = session.query(models.NodeState).filter_by(nodeId = nodeid)
    qry = qry.filter(models.NodeState.seq_num != None)
    qry = qry.order_by(models.NodeState.time)
    if startdate:
        qry = qry.filter(models.NodeState.time >= startdate)
    if enddate:
        qry = qry.filter(models.NodeState.time <= enddate)
    
    qry = qry.group_by(models.NodeState.time, models.NodeState.seq_num)

    #Convert to pandas
    df = pandas.DataFrame([x.pandas() for x in qry])
    #df.to_pickle("nodestate.pkl")

    if len(df) == 0:
        LOG.warning("No Data for node {0}".format(nodeid))
        return "No Data", 0.0, 0.0, 0.0
    elif len(df) == 1:
        LOG.warning("Single Sample for this Node")
        return df.irow(-1)["time"], 0.0, 0.0, 0.0

    if startdate:
        firstsample = startdate
    else:
        firstsample = df.irow(0)["time"]
    if enddate:
        lastsample = enddate
    else:
        lastsample = datetime.datetime.now()
        #lastsample = df.irow(-1)["time"] #This calculated based on the data we had

    duration = lastsample - firstsample
    #Work out how many are expected for complete days
    expected = duration.days * SAMPLE_RATE_DAY 
    expected += duration.seconds / (SAMPLE_RATE_MINUTES*60)

    LOG.debug("First {0} Last {1} Duration {2} Expected {3}".format(firstsample,
                                                                    lastsample,
                                                                    duration,
                                                                    expected))
    if expected < 1.0:
        LOG.warning("Single Sample for th")
        return lastsample, 0, 0, 0


    """
    #So the simple way of calculating packetyield is
    # Nrows / Rxpected * 100.0
    # This should give us the "compression factor"
    """

    nrows = float(len(df))
    LOG.debug("{0} Compression Factor {0}".format("-"*10))
    LOG.debug("Nrows {0} Expected {1}".format(len(df), expected))

    packetyield = (len(df) / expected) * 100.0

    LOG.debug("Compression Factor {0} {1} {2}".format(len(df),
                                                      expected,
                                                      packetyield))

    """
    And packet yield is
    Total Packets - (Diff Sequence > 1)
    """

    #Calculate Diffs
    df["time_dif"] = df.time.diff()
    df.time_dif = df.time_dif.fillna(0)
    #df["expected"] = df.time.diff.total_seconds() / (5*60)
    df["seq_dif"] = df.seq_num.diff()
    df.seq_dif = df.seq_dif.fillna(1)
    df["expected"] = df.time_dif.apply(lambda x : round(x / numpy.timedelta64(datetime.timedelta(minutes=5))),0)
    df["new_dif"] = df.seq_dif

    #Check if the localtime is not ascending
    df["localtime_diff"] = df.localtime.diff()

    #Work out the time difference when we wrap around
    df.new_dif[df.new_dif < 0] = 255 + df.new_dif
    df["bad_samples"] = df.new_dif - 1
    df["good_samples"] = df.expected - df.bad_samples

    #For the moment, I am going to assume that all the data up to the reset is Good.
    df.good_samples[df.localtime_diff < 0] = df.expected
    df.bad_samples[df.localtime_diff < 0] = 0

    #And if we have more than 8 hours of data between samples (96)
    LOG.debug("Total with more than 8 hours of data {0}".format(len(df[df.good_samples>96])))
    df.bad_samples[df.good_samples > 96] =  df.good_samples
    df.good_samples[df.good_samples > 96] = 0


    #Delivered Packets
    delivered = len(df)
    totalretries = len(df[df.new_dif > 1])
    LOG.debug("--> Total Retries {0}".format(totalretries))
    failed = df.new_dif[df.new_dif > 1].sum() - totalretries

    sumgood = df.good_samples.sum()
    sumbad = df.bad_samples.sum()
    datayield = sumgood / expected * 100.0

    #How many times has our clock reset
    noderesets = df[df.localtime_diff < 0].count()[0]

    # LOG.debug("--------")
    # print df.head()
    # LOG.debug("Delivered Packets {0}".format(delivered))
    # LOG.debug("Failed Packets {0}".format(failed))


    # packetyield = (1 - (failed / expected)) * 100.0
    LOG.debug("Deliviered {0} Failed {1} Good {2}  Bad {3} Yield {4}".format(delivered,
                                                                             failed,
                                                                             sumgood,
                                                                             sumbad,
                                                                             datayield))
    df.to_csv("yielddumpOrd.csv")
    df.to_pickle("yielddumpOrd.pkl")
    return lastsample, datayield, packetyield, noderesets
