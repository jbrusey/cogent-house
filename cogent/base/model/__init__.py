"""
Classes to initialise the SQL and populate with default Sensors

:version: 0.3
:author: Dan Goldsmith
:date: Feb 2012

"""

import logging
log = logging.getLogger(__name__)

import csv
import os

from sqlalchemy.exc import IntegrityError

from meta import *

#Namespace Mangling
from deployment import *
from deploymentmetadata import *
from host import *
from house import *
from housemetadata import *
from lastreport import *
from location import *
from node import *
from nodehistory import *
from nodestate import *
from nodetype import *
from occupier import *
from rawmessage import *
from reading import *
from room import *
from roomtype import *
from sensor import *
from sensortype import *
from weather import *

   
def populateSensorTypes():
    """Populate the database with default sensing types,
    if they do not already exist.
    """
    log.debug("Populating Sensors")
    session = Session()
    #transaction.begin()

    sensorList = [SensorType(id=0,name="Temperature",
                            code="T",
                            units="deg.C",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=1,name="Delta Temperature",
                            code="dT",
                            units="deg.C/s",
                            c0=0., c1=1., c2=0., c3=0.),                              
                 SensorType(id=2,name="Humidity",
                            code="RH",
                            units="%",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=3,name="Delta Humidity",
                            code="dRH",
                            units="%/s",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=4,name="Light PAR",
                            code="PAR",
                            units="Lux",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=5,name="Light TSR",
                            code="TSR",
                            units="Lux",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=6,name="Battery Voltage",
                            code="BAT",
                            units="V",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=7,name="Delta Battery Voltage",
                            code="dBT",
                            units="V/s",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=8,name="CO2",
                            code="CO2",
                            units="ppm",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=9,name="Air Quality",
                            code="AQ",
                            units="ppm",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=10,name="VOC",
                            code="VOC",
                            units="ppm",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=11,name="Power",
                            code="POW",
                            units="W",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=12,name="Heat",
                            code="HET",
                            units="W",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=13,name="Duty cycle",
                            code="DUT",
                            units="ms",
                            c0=0., c1=1., c2=0., c3=0.),
        	 SensorType(id=99,name="Gas Consumption",
                            code="Gas",
                            units="kWh",
                            c0=0., c1=1., c2=0., c3=0.),
        	SensorType(id=102,name="Outside Temperature",
                            code="ws_temp_out",
                            units="deg.C",
                            c0=0., c1=1., c2=0., c3=0.),   
        	SensorType(id=103,name="Outside Humidity",
                            code="ws_hum_out",
                            units="deg.C",
                            c0=0., c1=1., c2=0., c3=0.),    
        	SensorType(id=104,name="WS Inside Temperature",
                            code="ws_temp_in",
                            units="deg.C",
                            c0=0., c1=1., c2=0., c3=0.),   
        	SensorType(id=105,name="WS Inside Humidity",
                            code="ws_hum_in",
                            units="deg.C",
                            c0=0., c1=1., c2=0., c3=0.),    
                 SensorType(id=106,name="Dew Point",
                            code="ws_dew",
                            units="deg.C",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=107,name="Apparent Temperature",
                            code="ws_apparent_temp",
                            units="deg.C",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=108,name="Wind Gust",
                            code="ws_wind_gust",
                            units="mph",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=109,name="Average Wind Speed",
                            code="ws_wind_ave",
                            units="mph",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=110,name="Wind Direction",
                            code="ws_wind_dir",
                            units="",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=111,name="Wind Chill",
                            code="ws_wind_chill",
                            units="deg.C",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=112,name="Rain Fall",
                            code="ws_rain",
                            units="mm",
                            c0=0., c1=1., c2=0., c3=0.),
                 SensorType(id=113,name="Absolute Pressure",
                            code="ws_abs_pressure",
                            units="hpa",
                            c0=0., c1=1., c2=0., c3=0.)]

    for item in sensorList:
        session.merge(item)


def _parseCalibration(filename,sensorcode):
    """Helper method to Parse a sensor calibration file

    :param filename: Name of file we get cooeficencts from
    :param sensorcode: sensor code of sensor type these Cooeficients correspond to
    """
    
    log.debug("Updating Cooeficents from {0}".format(filename))

    session = Session()        

    theFile = "{0}.csv".format(filename)
    thePath = os.path.join("cogentviewer","calibration",theFile)
    
    #Find the relevant sensor type
    sensorType = session.query(SensorType).filter_by(code=sensorcode).first()
    #log.debug("Sensor Type for {0} is {1}".format(sensorcode,sensorType))
    

    #log.debug("Dealing with file {0} Path {1}".format(theFile,thePath))
    reader = csv.reader(open(thePath,"r"),delimiter=",")
    for row in reader:
        #log.debug(row)
        if len(row) == 2:
            nodeId,c = row
            m = 1.0
        elif len(row) == 3:
            nodeId,m,c = row
        else:
            log.warning("Unable to parse Cooeficients")

        #Check for blank values
        if m == '':
            m = 1.0
        if c == '':
            c = 0.0
            
        nodeId = int(nodeId)
        m = float(m)
        c = float(c)
        
        #Check if we know about this sensor
        theQry = session.query(Sensor).filter_by(sensorTypeId = sensorType.id,
                                                 nodeId = nodeId).first()

        if theQry is None:
            #Add a new Sensor

            theSensor = Sensor(sensorTypeId = sensorType.id,
                               nodeId = nodeId,
                               calibrationSlope = m,
                               calibrationOffset = c)
            session.add(theSensor)
            log.debug("Adding New Sensor {0}".format(theSensor))

        else:
            #Update the Sensor ?
            theQry.calibrationSlope = m
            theQry.calibrationOffset = c
            
    session.flush()


def populateCalibration():
    """
    Populate the Sensor Table with the correct calibration Cooeficients for each Sensor
    """
    log.debug("Populating Calibrations")
    
    #List of (file, sensor code) pairs
    calibFiles = [("aq_coeffs","AQ"),
                  ("co2_coeffs","CO2"),
                  ("hum_coeffs","RH"),
                  ("temp_coeffs","T"),
                  ("voc_coeffs","VOC")]
    for item in calibFiles:
        _parseCalibration(item[0],item[1])


def populateRoomTypes():
    """Add Some Default Room Types"""
    log.debug("Populating room types")
    session = Session()

    roomList = ["Bedroom",
                "Bathroom",
                "Living Room",
                "Kitchen",
                "Hallway",
                "Spare Room"]
    for item in roomList:
        theQry = session.query(RoomType).filter_by(name=item).first()
        if theQry is None:
            session.add(RoomType(name=item))
            
    session.flush()

        

def initialise_sql(engine):
    """Initialise the database, standard Pyramid Code"""
    Session.configure(bind=engine)
    Base.metadata.bind=engine
    Base.metadata.create_all(engine)
    
    populateSensorTypes()
    populateCalibration()
    populateRoomTypes()

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine)
