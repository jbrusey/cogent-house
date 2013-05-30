from pyramid.response import Response
from pyramid.renderers import render_to_response
import pyramid.url

import cogentviewer.models.meta as meta
import cogentviewer.models as models
import homepage

import logging

import pyrrd.rrd as rrd
import pyrrd.graph as graph

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import time
import datetime
import math


def _loadRRD(thefile):
    theRRD = rrd.RRD(thefile,mode="r")
    return theRRD

def _jsonify(theRRD):
    """turn this item into a JSON Representation Acceptble"""
    #Get the high res Version
    
    last = theRRD.last()

    print "Most Recent Sample {0} {1}".format(last,time.ctime(last))
    hifirst = theRRD.first()
    print "First Sample (Hi Rez) {0} {1}".format(hifirst,time.ctime(hifirst))
    print "First Hi Rez (CALC) {0}".format(last+(300*4032))
    #Middle Resolution

    midfirst = theRRD.first(1)
    print "First Sample (Mid Rez) {0} {1}".format(midfirst,time.ctime(midfirst))

    lowfirst = theRRD.first(4)
    print "First Sample (Low Rez) {0} {1}".format(lowfirst,time.ctime(lowfirst))

    #Fetch the data
    hifetch = theRRD.fetch(start=hifirst,end=last)
    hidata = hifetch["temp"]


    #midfetch = theRRD.fetch(start=midfirst,end=hifirst-600)
    midfetch = theRRD.fetch(start=midfirst,end=last)
    middata = midfetch["temp"]
    lowfetch = theRRD.fetch(cf="AVERAGE",start=lowfirst,end=last)
    lowdata =  lowfetch["temp"]
    # lowdataL = theRRD.fetch(cf="MIN",start=lowfirst,end=last)
    # lowfetchL = lowdataL["temp"]
    # lowdataH = theRRD.fetch(cf="MAX",start=lowfirst,end=last)
    # lowfetchH = lowdataH["temp"]
    
    
    #hidata.extend(middata)
    # #hidata = [[datetime.datetime.fromtimestamp(value[0]).isoformat(),value[1]] for value in hidata]
    # hidata = [[value[0],value[1]] for value in hidata]
    
    # #lowdata = [[datetime.datetime.fromtimestamp(value[0]).isoformat(),value[1]] for value in lowdata]

    t1 = time.time()
    # outValues = []    
    # lowValues = []
    # # #Iterating


    # for idx,value in enumerate(lowdata):
    #     if math.isnan(value[1]):
    #         continue
    #     #lowValues.append([datetime.datetime.fromtimestamp(value[0]).isoformat(),value[1]])
    #     lowValues.append([value[0]*1000,value[1]])
    #     outValues.append([value[0]*1000,lowfetchL[idx][1],lowfetchH[idx][1]])
    #     #value = value + tuple(lowfetchL[idx][1])# + tuple(lowfetchH[idx][1])

    # midValues = []
    # for idx,value in enumerate(middata):
    #     if math.isnan(value[1]):
    #         continue
    #     #lowValues.append([datetime.datetime.fromtimestamp(value[0]).isoformat(),value[1]])
    #     midValues.append([value[0]*1000,value[1]])
    #     #outValues.append([value[0]*1000,midfetchL[idx][1],midfetchH[idx][1]])
    


    hiValues = []
    count = 0
    #import csv
    #tmp = csv.writer(open("test.csv","w"))
    
    for idx,value in enumerate(hidata):
        if math.isnan(value[1]):
            continue
        hiValues.append([value[0]*1000,value[1]])
        #tmp.writerow([value[0],value[1]])
        #hiValues.append([datetime.datetime.fromtimestamp(value[0]).isoformat(),value[1]])


    midValues = []
    for idx,value in enumerate(middata):
        if math.isnan(value[1]):
            continue
        midValues.append([value[0]*1000,value[1]])
        
    lowValues = []
    lowOffset = (60*60)*3 #Offset so point is at midday
    #lowOffset = 0
    for idx,value in enumerate(lowdata):
        if math.isnan(value[1]):
            continue
        lowValues.append([(value[0]-lowOffset)*1000,value[1]])

        
    t2 = time.time()
    print "Time for Enumerate {0}".format(t2-t1)
    
    #And Spit out in a form that the Vis tool likes
    series = [# {"name":"Daily Min Max",
              #  "type":"arearange",
              #  "data":outValues},
              {"name":"6Hr Avg",
               #"step":True,
               "data":lowValues},
              {"name":"Reading",
               "data":hiValues},
              {"name":"Hourly Avg",
               "data":midValues},
              ]

    #jsonStr = json.dumps(series)
    #print len(jsonStr)
    return series

def jsonrrd(request):
    fd = "cogentviewer/static/pytest.rrd"

    theRRD = _loadRRD(fd)
    jsonout = _jsonify(theRRD)
    return jsonout


def rrdgraph(request):
    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)

    outDict["pgTitle"] = "Time Series Data"
    #outDict["deployments"] =deps
    outDict["nodeDropdowns"] = homepage.getNodeDropdowns()

    #Graphing


    fd = "cogentviewer/static/pytest.rrd"
    theRRD = rrd.RRD(fd,mode="r")

    last = theRRD.last()
    first = last - (300*4032)
    hifirst = theRRD.first()
    lofirst = theRRD.first(4)
    print "LAST {0} First {1} / {2}".format(last,first,hifirst)
    graphfile = "cogentviewer/static/theGraph.png"
    g = graph.Graph(graphfile,
                    start = hifirst,
                    end = last,
                    imgformat="PNG")



    def1 = graph.DEF(rrdfile=fd,
                     vname="tempavg",
                     dsName="temp")

    def2 = graph.DEF(rrdfile=fd,
                     vname="tempmin",
                     dsName = "temp",
                     cdef="MIN")

    line1 = graph.LINE(defObj=def1,color="#FF0000",legend="temperature")
    line2 = graph.LINE(defObj=def2,color="#00FF00",legend="min")
    g.data.extend([def1,line1,def2,line2])
    g.write()
    

    graphfile = "cogentviewer/static/theGraphLow.png"
    g = graph.Graph(graphfile,
                    start = lofirst,
                    end = last,
                    imgformat="PNG")



    def1 = graph.DEF(rrdfile=fd,
                     vname="tempavg",
                     dsName="temp",
                     cdef="AVERAGE")
    def2 = graph.DEF(rrdfile=fd,
                     vname="tempmin",
                     dsName="temp",
                     cdef="MIN")
    def3 = graph.DEF(rrdfile=fd,
                     vname="tempmax",
                     dsName="temp",
                     cdef="MAX")


    line1 = graph.LINE(defObj=def1,color="#FF0000",legend="Average")
    line2 = graph.LINE(defObj=def2,color="#FF0000",legend="Min")
    line3 = graph.LINE(defObj=def3,color="#FF0000",legend="Max")
    g.data.extend([def1,line1,def2,line2,def3,line3])
    g.write()



    return render_to_response('cogentviewer:templates/rrdgraph.mak',
                              outDict,
                              request=request)

    
