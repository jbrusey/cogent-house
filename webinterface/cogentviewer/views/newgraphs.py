"""
Break out graphing functionlity
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

from pyramid.view import view_config

import pandas
import time

# @view_config(route_name='newgraphs',
#              renderer='jsonp')
@view_config(route_name='newgraphs',
             renderer='pandas_jsonp')
def getdata(request):
    """New Grahping functionlity"""
    log = logging.getLogger(__name__)

    reqtype = request.method

    log.debug("Reqest Type {0}".format(reqtype))

    if reqtype != "GET":
        return

    #Get all of our parameters
    paramdict = request.GET.mixed()
    log.debug("--> Parameter Dictionary {0}".format(paramdict))

    #First thing is to check for the graph type
    graphtype = paramdict.get("graphtype")
    #graphtype="pushstatus"
    if graphtype == "pushstatus":
        log.debug("Fetching Push Status")
        return _getpushstatus(request)
    if graphtype == "nodestate":
        log.debug("Fetching Node State")
        return _getnodestate(request)
    if graphtype == "nodestate-pandas":
        log.debug("Fetching Pandas Version of Node State")
        return _getnodestate_pandas(request)
    return []

def _getpushstatus(request):
    """Fetch a time series history of push statuses for this server"""
    log = logging.getLogger(__name__)
    #Get all of our parameters
    paramdict = request.GET.mixed()

    hostname = "eti10"
    hostname = paramdict.get("hostname", None)
    offset = float(paramdict.get("offset", 100))
    if hostname is None:
        log.info("No Hostname Supplied")
        return []
    
    #Check the Host actually exists
    qry = DBSession.query(models.Server).filter_by(hostname = hostname)
    server = qry.first()
    if server is None:
        log.info("No Server with hostname {0}".format(hostname))
        return []


    qry = DBSession.query(models.PushStatus).filter_by(hostname = hostname)
    qry = qry.order_by(models.PushStatus.time)
    log.debug("{0} Push Status".format(qry.count()))

    jsonfmt = [[time.mktime(x.time.timetuple()) * 1000, offset] for x in qry.all()]
    #df = pandas.DataFrame([x.pandas() for x in qry.all()])
    #print df
    #print df.head()
    #jsonfmt = df.to_json(orient="records",date_format="iso")

    return jsonfmt
    

def _getnodestate(request):
    """Fetch a time series history of push statuses for this server"""
    log = logging.getLogger(__name__)
    #Get all of our parameters
    paramdict = request.GET.mixed()

    node = paramdict.get("node", None)
    log.debug("Node id is {0}".format(node))

    qry = DBSession.query(models.NodeState).filter_by(nodeId = node)
    qry = qry.group_by(models.NodeState.time, models.NodeState.seq_num)
    qry = qry.order_by(models.NodeState.time)
    #jsonfmt = []
    #for item in qry:
    #    ttup = time.mktime(item.time.timetuple())
    #
    #        jsonfmt.append([ttup * 1000,  item.nodeId])

    jsonfmt = [[time.mktime(item.time.timetuple())* 1000, item.nodeId] for item in qry]

    outlist = {"name": "Node {0}".format(node),
               "data": jsonfmt,
               "marker" : {"enabled": True}
               }

    return outlist

def _getnodestate_pandas(request):
    """Fetch a time series history of push statuses for this server"""
    log = logging.getLogger(__name__)
    #Get all of our parameters
    paramdict = request.GET.mixed()

    node = paramdict.get("node", 33)
    log.debug("Node id is {0}".format(node))

    qry = DBSession.query(models.Reading, sqlalchemy.func.count(models.Reading)).filter_by(nodeId = node)
    qry = qry.order_by(models.Reading.time)
    qry = qry.group_by(sqlalchemy.func.date(models.Reading.time))
    #qry = qry.limit(5)
    for item in qry:
        print item

    return ""


    #df = pandas.DataFrame([x.pandas() for x in qry.all()])
    #print df
    #print df
    #print df.head()
    #jsonfmt = df.to_json(orient="records",date_format="iso")
    #return jsonfmt
    #print "===== {0}".format(qry.count())
    #jsonfmt = []
    #for item in qry:
    #    ttup = time.mktime(item.time.timetuple())
    #    jsonfmt.append([ttup * 1000,  item.nodeId])
    
    #print jsonfmt
    #outlist = {"name": "Node {0}".format(node),
    #           "data": jsonfmt,
    #           "marker" : {"enabled": True}
    #           }

    #return outlist
              
