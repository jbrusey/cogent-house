"""
Methods to upload the contents of a current cost database to the server

This module provides functionality to transfer data from eiher
databases created by the current cost logging functionality on the
Arch rock server, or the CSV files holding data from the Jodrell
Street deployments.

@author: Dan Goldsmith
@version: 0.1.1
@date: November 2011
"""

#Standard Python Library
import logging
log = logging.getLogger(__name__)

import numpy
import time
import csv
import datetime

#Sqlalchemy for local connection
import sqlalchemy
import sqlalchemy.orm

#Pyramid modules
from sqlalchemy.ext.declarative import declarative_base
from pyramid.response import Response
from pyramid.renderers import render_to_response
import transaction

#My modules
import general
import orbit_viewer.models as models
import orbit_viewer.models.meta as meta

from node import summariseData as summarise


THRESHOLD = 50.0 #Threshold to trigger a new KwH Sample (~1 ES light bulb)
localBase = declarative_base()


class CCData(localBase):
    """Maps to Data table in current cost DB"""
    __tablename__ = "data"
    DeviceId = sqlalchemy.Column(sqlalchemy.Integer)
    DateTime = sqlalchemy.Column(sqlalchemy.DateTime, primary_key=True)
    Watts = sqlalchemy.Column(sqlalchemy.Float)
    kWh = sqlalchemy.Column(sqlalchemy.Float)

    def __init__(self, **kwargs):
        """Generalised Initialisation function.
        @param kwargs: Keyword arguments to initilise
        """
        self.update(kwargs)

    def update(self, theDict={}, **kwargs):
        """Generalized update function"""
        theDict.update(kwargs)

        for key, value in theDict.iteritems():
            setattr(self, key, value)

    def __repr__(self):
        return "{0}: {1} {2}".format(self.DateTime,
                                     self.Watts,
                                     self.kWh)


class CurrentCostBase(object):
    """
    Base Class for Current Cost Parsers.
    Holds some of the more general functionalty that will be needed by the
    parsing classes such as:

    * Checking for and creating new deployments, sensors, nodes
    * Parsing and loading the data
    """
    def __init__(self):
        """Standard initilaisation stuff"""
        self.log = logging.getLogger("CurrentCost")
        self.log.setLevel(logging.DEBUG)

    def createDBObjects(self, deploymentName):
        """Create or link to requried database objects
        *currentSensor:  Link to a current type of sensor
        * kwhsensor: Link to the kwH type of sensor
        * deployment: Deployment Object

        @param deploymentName: Name of the current deployment
        """

        log = self.log
        session = meta.DBSession()

        transaction.begin()

        sensorType = session.query(models.sensor.SensorType)
        sensorType=sensorType.filter_by(sensor_type = "Current Draw").first()
        self.currentSensor = sensorType

        sensorType = session.query(models.sensor.SensorType)
        sensorType=sensorType.filter_by(sensor_type = "kWh Usage").first()
        self.kwhSensor = sensorType

        #Check the deployment exists and create if it doesn't
        depQry = session.query(models.deployment.Deployment)
        depQry = depQry.filter_by(name=deploymentName).first()

        if depQry is None:
            theDeployment = models.deployment.Deployment(name=deploymentName)
            session.add(theDeployment)
            session.flush()
            log.info("New Deployment Created {0}".format(theDeployment))
        else:
            log.info("Using Existing Deployment {0}".format(depQry))
            theDeployment = depQry

        self.theDeployment = theDeployment

        #Add a Current Cost node to this deployment
        theQry = session.query(models.nodes.Node)

        theQry = theQry.filter_by(name="currentcost",
                                  deploymentId = self.theDeployment.Id).first()

        if theQry is None:
            self.theNode = models.nodes.Node(name="currentcost",
                                        deploymentId=self.theDeployment.Id)
            session.add(self.theNode)
            logging.info("Adding New Node to Database {0}".format(self.theNode))
            session.flush()
        else:
            self.theNode = theQry
            logging.info("Using Existing Node {0}".format(self.theNode))

        #And the Two Current Cost Sensors
        qry = session.query(models.sensor.Sensor)
        qry = qry.filter_by(nodeId = self.theNode.Id,
                            sensorTypeId = self.currentSensor.Id).first()

        if qry is None:
            self.nodeCurrent = models.sensor.Sensor(nodeId = self.theNode.Id,
                                               sensorTypeId = self.currentSensor.Id,
                                               name="watts")
            session.add(self.nodeCurrent)
            log.info("New Current Sensor Created {0}".format(self.nodeCurrent))
        else:
            self.nodeCurrent = qry
            log.info("Use Existing Current Sensor {0}".format(self.nodeCurrent))


        qry = session.query(models.sensor.Sensor)
        qry = qry.filter_by(nodeId = self.theNode.Id,
                            sensorTypeId = self.kwhSensor.Id).first()

        if qry is None:
            self.nodeKwh = models.sensor.Sensor(nodeId = self.theNode.Id,
                                               sensorTypeId = self.kwhSensor.Id,
                                               name="kWh")
            session.add(self.nodeKwh)
            log.info("New Kwh Sensor Created {0}".format(self.nodeKwh))
        else:
            self.nodeKwh = qry
            log.info("Use Existing Kwh Sensor {0}".format(self.nodeKwh))


        transaction.commit()


    def storeData(self,data,save=True):
        """Process data from a current cost deployment.
        This function will process the data gathered, transforming it into
        objects that can be stored in our database system.

        The class makes use of a modified form of the SIP, to reduce the
        huge number of samples that are generated.
        This assumes that the reading will remain static rather than follow
        a linear trend,  and trigger a update when the error excedes the
        :py:const: `THRESHOLD` value.

        The compression system also has a 5 minuite heartbeat.

        @param data: A list containing all the data we wish to store
        @param save: Save the samples or return a list
        @return: A list of samples if the `save` parameter is true.
        """
        log = self.log
        session = meta.DBSession()
        transaction.begin()

        #As there is a heckofalot(TM) of data collected by the current cost then
        #we summarise

        lastReading = None #Value of last reading
        lastHour = None #Hour last KwH sample was stored
        lastKwh = None  #value of last KwH stored
        prevReading = None #Previous reading
        readingCache = []
        samples = [] #Place to put generated samples
        kwSamples = []
        cumKwh = 0.0

        if save:
            nodeCurrent = self.nodeCurrent
            nodeKwh = self.nodeKwh
        else:
            nodeCurrent = models.nodes.Node(Id = 1)
            nodeKwh = models.nodes.Node(Id = 1)

        for reading in data:
            #print reading
            readingCache.append(reading.Watts)

            if not lastReading:
                log.info("Initialising")
                #Initialise everything
                lastReading = reading
                lastKwh = reading
                prevReading = reading
                #Get the hour for the last KwH
                lastHour = datetime.datetime(year = lastReading.DateTime.year,
                                             month = lastReading.DateTime.month,
                                             day = lastReading.DateTime.day,
                                             hour = lastReading.DateTime.hour)

                log.debug("Last Reading {0} Hour {1}".format(lastReading,
                                                             lastHour))

            #Log a sample if we reach the threshold

            if abs(prevReading.Watts - reading.Watts) >= THRESHOLD:
                #log.info("Threshold Exceded")

                rCache = numpy.array(readingCache)
                avgValue = rCache.mean()

                theSample = models.sample.Sample(timestamp = reading.DateTime,
                                                 sensorId = nodeCurrent.Id,
                                                 value = reading.Watts)
                                                 #value = reading.Watts)
                samples.append(theSample)

                lastReading = reading
                readingCache = []


            #Time Difference
            tdiff = reading.DateTime - lastReading.DateTime
            if tdiff.seconds >= 5*60:
                #Get the Average Reading over this time period
                rCache = numpy.array(readingCache)
                avgValue = rCache.mean()

                theSample = models.sample.Sample(timestamp = reading.DateTime,
                                                 sensorId = nodeCurrent.Id,
                                                 value = avgValue)
                                                 #value = reading.Watts)
                samples.append(theSample)

                lastReading = reading
                readingCache = []

                #Total kWh used

            #Summarise the Kwh
            timeSec = (reading.DateTime - prevReading.DateTime).seconds
            timeHours = timeSec / (60.0*60.0)
            thisKwh = (reading.Watts * timeHours) / 1000.0
            cumKwh += thisKwh


            if (reading.DateTime - lastHour).seconds >= (60*60):
                #log.debug("New Hour {1} - {0}".format(reading,lastKwh))

                theSample = models.sample.Sample(timestamp = lastHour,
                                                 value = cumKwh,
                                                 sensorId = nodeKwh.Id)
                kwSamples.append(theSample)

                cumKwh = 0.0
                lastHour = datetime.datetime(year = reading.DateTime.year,
                                             month = reading.DateTime.month,
                                             day = reading.DateTime.day,
                                             hour = reading.DateTime.hour)



            prevReading = reading

        #session.add_all(samples)

        if save:
            t1 = time.time()

            session.query(models.sample.Sample).filter_by(sensorId = nodeCurrent.Id).delete()
            session.flush()

            t2 = time.time()
            log.debug("Deleting Old Data {0} seconds taken".format(t2-t1))

            session.add_all(samples)
            session.flush()

            t3 = time.time()
            log.debug("Inserting New Data {0} seconds taken".format(t3-t2))


            session.flush()

            #And the Same for the KwH
            session.query(models.sample.Sample).filter_by(sensorId = nodeKwh.Id).delete()
            session.add_all(kwSamples)
            session.flush()

            t1 = time.time()
            transaction.commit()
            t2 = time.time()
            log.debug("Total Transaction time {0}".format(t2-t1))
            return True
        else:
            return samples


class CurrentCostParser(CurrentCostBase):
    """Class to deal with uploading current cost data

    This file will take the data output by the perl / python current cost storage
    """
    def __init__(self,ccDb):
        """Initialise the Parser

        @param ccDb: Current Cost Database object
        """

        self.log = logging.getLogger("CurrentCost")
        self.log.setLevel(logging.DEBUG)
        log = self.log
        log.debug("Creating CC Parser")

        ccEngine = sqlalchemy.create_engine("sqlite:///{0}".format(ccDb))
        ccMetadata = localBase.metadata
        ccMetadata.create_all(ccEngine)

        self.makeSession = sqlalchemy.orm.sessionmaker(bind=ccEngine)


    def toCSV(self,outFile="output.csv",startDate=None,endDate=None):
     
        ccSession = self.makeSession()
        data = ccSession.query(CCData)

        if startDate:
            data = data.filter(CCData.DateTime >= startDate)
        if endDate:
            data = data.filter(CCData.DateTime <= endDate)

        cleanData = self.storeData(data,save=False)

        writer = csv.writer(open(outFile,"wb"),delimiter=",")
        writer.writerow(["time","reading"])
        for item in cleanData:
            writer.writerow([time.mktime(item.timestamp.timetuple()),item.value])
            

    def transferData(self,deploymentName,startDate=None,endDate=None):
        """
        Transfer databetween the local database and the main database.
        As there is a heckofalot of data, we make use of a SI like
        protocol to reduce the amount of info that has to be stored,
        Basically, only store a sample if it differs from the previous
        by +/- some threshold (CHANGE_THRESHOLD).

        We also log data every 5 mins to keep some kind of parity with
        the data sensed by arch rock

        @param deploymentName: Name of deployment to add this data to
        """
        session = meta.DBSession()
        ccSession = self.makeSession()

        status = {}
        log = self.log

        #transaction.begin()

        self.createDBObjects(deploymentName)

        ## Next we fetch the data and add it to the DBSession

        data = ccSession.query(CCData)
        print data.count()
        if startDate:
            data = data.filter(CCData.DateTime >= startDate)
        if endDate:
            data = data.filter(CCData.DateTime <= endDate)

        data = data.order_by(CCData.DateTime)
        log.debug("Total items to add {0}".format(data.count()))
        self.storeData(data)

class CurrentCostFileParser(CurrentCostBase):
    """
    Parser to deal with current cost filtes that have been exported to CSV
    The files from the Nibe Deployments are one example of these type of files.
    """
    def __init__(self,theFile):
        """Initialise the Parser

        @param theFile: File to take data from
        """

        self.log = logging.getLogger("CurrentCost")
        self.log.setLevel(logging.DEBUG)
        log = self.log
        log.debug("Creating CC File Parser")

        #Store the file
        reader = csv.reader(open(theFile,"r"),delimiter="\t")
        #Remve the header
        reader.next()
        self.reader = reader


    def transferData(self,deploymentName,startDate=None,endDate=None):
        """
        Transfer databetween the local database and the main database.
        As there is a heckofalot of data, we make use of a SI like protocol to
        reduce the amount of info that has to be stored,  Basically, only store
        a sample if it differs from the previous by +/- some threshold
        (CHANGE_THRESHOLD).

        We also log data every 5 mins to keep some kind of parity with the data
        sensed by arch rock

        @param deploymentName: Name of deployment to add this data to
        """
        log = self.log
        session = meta.DBSession()

        self.createDBObjects(deploymentName)

        #Load the file itself and cast all data objects into
        #CCData objects
        data = []
        reader = self.reader
        #for x in range(5):
        #    line = reader.next()

        testDate = {}
        for line in reader:

            dateArray = line[0].split()
            dt = [int(x) for x in dateArray[0].split("/")] #Date Portion
            tm = [int(x) for x in dateArray[1].split(":")] #Time Portion
            theTime = datetime.datetime(dt[2],dt[1],dt[0],tm[0],tm[1],tm[2])

            exists = testDate.get(theTime,None)
            if exists:
                #log.debug("Duplicate Valures {0} {1}".format(theTime,line))
                pass
            else:
                testDate[theTime] = True
                #And the Reading
                current = int(line[1])
                kwhReading = float(line[2])
                #print line

                #@TODO: Fix the start and stop dates
                #if startDate and theTime > startDate:
                #    if endDate and theTime < endDate:
                ccObj = CCData()
                ccObj.DateTime = theTime
                ccObj.Watts = current
                ccObj.kWh = kwhReading
                data.append(ccObj)

        log.debug("Storing {0} Objects".format(len(data)))
        self.storeData(data)
        log.debug("Summarising")
        summarise(self.theDeployment.Id)
        log.debug("Upload Complete")

if __name__ ==  "__main__":
    from pyramid.paster import bootstrap
    env = bootstrap('../../development.ini')
    env['request'].route_url('home')

    import logging.config
    logging.config.fileConfig("../../development.ini")

    log = logging.getLogger("ccDB")
    log.debug("Uploading Current Cost Database Information")

    #runUpload(env['request'])
    
    #theFile = "FoleshillElec.db"
    #theFile = "/home/dang/DEPLOYMENTDATA/currentCostStPeters.db"
    #startDate = datetime.datetime(2011,9,12)
    #endDate = datetime.datetime(2011,9,12+7)

    theDeployment = "RooftopNibe"
    theFile = "/home/dang/DEPLOYMENTDATA/rooftopNibe.db"

    foo = CurrentCostParser(theFile)
    #foo.toCSV("FhDump.csv",startDate,endDate)
    foo.transferData(theDeployment)

    #theFile = "/home/dang/DeploymentData/119Jodrell/119JodrelElectricity.csv"
    #foo = CurrentCostFileParser(theFile)
    #foo.transferData("119Jodrell")

    env['closer']()
