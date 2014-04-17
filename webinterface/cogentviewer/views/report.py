"""
Generate Summary Reports

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
import subprocess
import pandas
import numpy

@view_config(route_name='report', renderer='cogentviewer:templates/report.mak',permission="view")
def reportdata(request):
    """
    View that allows exporting of data.
    """

    #session = meta.Session)
    #deployments = session.query(models.deployment.Deployment).all()

    outDict = {}
    outDict["headLinks"] = homepage.genHeadUrls(request)
    outDict["sideLinks"] = homepage.genSideUrls(request)
    outDict["pgTitle"] = "Report"
    theUser = homepage.getUser(request)
    outDict["user"] = theUser.username

    if "submit" in request.POST:
        LOG.debug("Dealing with form submission")
        #Rscript -e "library(knitr); knit('$(rnwfile).Rnw')"
        #subprocess.call(["ls","-l"],cwd="./cogentviewer/rscripts")
        subprocess.call(["make"],cwd="./cogentviewer/rscripts")
        LOG.debug("--> Script Finished")

    #Yields
    # LOG.debug("Checking for Dupes")
    # session = meta.Session()
    # housedict = {}
    # houseqry = session.query(models.House).filter(models.House.id > 1)

    # for item in houseqry:
    #     dictitem = housedict.get(item.address,[])
    #     dictitem.append(item)
    #     housedict[item.address] = dictitem

    # for key,value in housedict.iteritems():
    #     #LOG.debug("{0} {1}".format(key,value))
    #     if len(value) > 1:
    #         LOG.warning("House {0} has more than one entries".format(key))
    #         for item in value:
    #             LOG.warning("--> {0}".format(item))

    #             #Lets try and clear this up
    #             #LOG.debug("--> Locations {0}".format(item.locations))
    #             locIds = [x.id for x in item.locations]
    #             if locIds is None:
    #                 LOG.warning("Removeing missing locations")
    #                 deleteQry = session.query(models.House).filter_by(id = item.id)
    #                 raw_input("Remove missing Locations?")
    #                 deleteQry.delete("fetch")
    #             LOG.debug("--> Location Ids {0}".format(locIds))

    #             #Check for Readings
    #             theQry = session.query(models.Reading).filter(models.Reading.locationId.in_(locIds))
    #             #thecount = theQry.count()
    #             hassample = theQry.first()
    #             LOG.debug("--> First Sample")
    #             if hassample is None:
    #                 LOG.debug("--> --> No Samples for any of these locations")

    #                 deleteQry = session.query(models.Location).filter(models.Location.id.in_(locIds))
    #                 #out = raw_input("Ok to delete {0}".format([x.id for x in deleteQry.all()]))
    #                 raw_input("Remove duplicate Readings? ")
    #                 deleteQry.delete("fetch")

    #                 deleteQry = session.query(models.House).filter_by(id = item.id)
    #                 deleteQry.delete("fetch")
                    
    #             #continue

    LOG.debug("Calclating Yields")
    session = meta.Session()
    #houseqry = session.query(models.House).filter(models.House.id != 25).filter(models.House.id != 32).filter(models.House.id != 34).filter(models.House.id != 35)

    houseqry = session.query(models.House).filter(models.House.id == 35)
    for house in houseqry:
        LOG.debug("Processing House {0}".format(house))
        #We next need locations associated with this House
        locIds = [x.id for x in house.locations]
        LOG.debug("Location Ids {0}".format(locIds))
        readingQry = session.query(models.Reading).filter(models.Reading.locationId.in_(locIds))
        #LOG.debug(readingQry)
        #LOG.debug(readingQry.first())
        #LOG.debug(readingQry.count())
        #Daily Counts

        typeQry = session.query(models.SensorType).filter_by(name="Daily Count").first()
        typeId = typeQry.id

        sumQry = session.query(models.Reading)
        sumQry = sumQry.filter_by(typeId = typeId)
        sumQry = sumQry.filter(models.Reading.locationId.in_(locIds))
        if sumQry.first():
            LOG.debug("Summary Exists for this node")
            continue


        dayQry = session.query(sqlalchemy.func.date(models.Reading.time),
                               models.Reading.nodeId,
                               models.Reading.locationId,
                               models.Reading.typeId,
                               sqlalchemy.func.count(models.Reading),
                               #sqlalchemy.func.count(models.Reading.typeId.distinct()),
                               )

        dayQry = dayQry.filter(models.Reading.locationId.in_(locIds))
        dayQry = dayQry.filter(models.Reading.typeId != typeQry.id)
        dayQry = dayQry.group_by(models.Reading.nodeId)
        dayQry = dayQry.group_by(models.Reading.locationId)
        dayQry = dayQry.group_by(models.Reading.typeId)
        dayQry = dayQry.group_by(sqlalchemy.func.date(models.Reading.time))
        
        #print dayQry
        

        #LOG.debug("Count Id is {0}".format(typeQry))
        if dayQry.count() == 0:
            LOG.warning("No Readings found")
            continue
        #import csv
        #outfd = csv.writer(open("testfile.csv","wb"))
        #outfd.writerow(["Date","Node","Location","Type","Count"])
        #for item in dayQry.limit(5):
        #    print item
        df = pandas.DataFrame(dayQry.all(),columns=["Date","nodeId","locationId","typeId","Count"])
        #print df
        #df.to_pickle("dump.pkl")
        piv = pandas.pivot_table(df,rows=["Date"],cols=["nodeId","locationId"],values="Count",aggfunc=numpy.mean)
        #And add to the database as a new summary item
        
        addSession = meta.Session()
        for item in piv.iteritems():
            thisSeries = item[1]
            nodeId,locId = thisSeries.name
            for pair in thisSeries.iteritems():
                time,value = pair
                newReading = models.Reading(time=time,
                                            nodeId=nodeId,
                                            typeId=typeId,
                                            locationId=locId,
                                            value=value)
                addSession.add(newReading)
                #print newReading
            LOG.debug("Row {0} {1} complete".format(nodeId,locId))
        
        addSession.flush()
        session.flush()

    #     print "Done"
    LOG.debug("Return Dict")
    return outDict
