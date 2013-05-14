"""
Class to populate the database with some default items

* Sensors
* Calibrations
* Rooms

:author: Dan Goldsmith <djgoldsmith@googlemail.com>
"""

import logging

import os
import csv

#DB Relevant imports
#from meta import *
import meta

#Interesting, this sets up the log to be the same log as the most recent object
#Therefore we need to setup the log after we import 
from sensortype import *
from roomtype import *
from node import *
from sensor import *
from room import *

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

#Globals to hold potential locations of Calibration files
CALIB_LOCS = [["cogent","base","Calibration"],
              ["cogentviewer","calibration"],
              ]

def populateSensorTypes(session = False):
    """Populate the database with default sensing types,
    if they do not already exist.
    """
    log.info("Populating SensorTypes")

    if not session:
        session = meta.Session()

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
                 SensorType(id=20,name="Power pulses",
                            code="POP",
                            units="p",
                            c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=50,name="Plogg Power",
                             code="plogg_kwh",
                             units="kWh"),
                  SensorType(id=51,name="Plogg Current",
                             code="plogg_a",
                             units="A"),
                  SensorType(id=51,name="Plogg Wattage",
                             code="plogg_w",
                             units="W"),
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

    session.flush()
    session.commit()
    session.close()


def _parseCalibration(filename,sensorcode,session=False):
    """Helper method to Parse a sensor calibration file

    :param filename: Name of file we get coefficients from
    :param sensorcode: sensor code of sensor type these Coefficients correspond to
    """
    
    log.debug("Updating Coefficients from {0}".format(filename))

    #if not session:
    #    session = meta.Session() 

    theFile = "{0}.csv".format(filename)
    basePath = None
    for item in CALIB_LOCS:
        thePath = os.path.join(*item)
        log.debug("Path to test {0}".format(thePath))
        if os.path.exists(thePath):
            basePath = thePath
            log.debug("Base Path is {0}".format(basePath))
            break

    if basePath is None:
    #log.info("Path to test {0}".format(basePath,))
        thePath = theFile
    else:
        thePath = os.path.join(basePath,theFile)

    #Find the relevant sensor type
    sensorType = session.query(SensorType).filter_by(code=sensorcode).first()

    try:
        reader = csv.reader(open(thePath,"r"),delimiter=",")
    except IOError,e:
        log.warning("Unable to parse calibration {0}".format(e))
        return False

    for row in reader:
        if len(row) == 2:
            nodeId,c = row
            m = 1.0
        elif len(row) == 3:
            nodeId,m,c = row
        else:
            log.warning("--> Unable to parse Coefficients")

        #Check for blank values
        if m == '':
            m = 1.0
        if c == '':
            c = 0.0
            
        nodeId = int(nodeId)
        m = float(m)
        c = float(c)
        
        #Check if we know about this Node
        theNode = session.query(Node).filter_by(id = nodeId).first()
        if theNode is None:
            #Create a new Node
            theNode = Node(id=nodeId)
            log.debug("--> Creating Node {0}".format(theNode))
            session.add(theNode)
        
        
        #Check if we know about this sensor
        theSensor = session.query(Sensor).filter_by(sensorTypeId = sensorType.id,
                                                    nodeId = nodeId).first()

        if theSensor is None:
            #Add a new Sensor
            theSensor = Sensor(sensorTypeId = sensorType.id,
                               nodeId = nodeId,
                               calibrationSlope = m,
                               calibrationOffset = c)
            session.add(theSensor)
            log.debug("--> Adding New Sensor {0}".format(theSensor))

        else:
            #Update the Sensor ?
            theSensor.calibrationSlope = m
            theSensor.calibrationOffset = c

    session.flush()
    session.commit()
    session.close()
    return True

def populateCalibration(session = False):
    """
    Populate the Sensor Table with the correct calibration Coefficients for each Sensor

    :param session: Session to use if not the default session
    """
    log.info("Populating Calibration Data")
    
    #List of (file, sensor code) pairs
    calibFiles = [("aq_coeffs","AQ"),
                  ("co2_coeffs","CO2"),
                  ("hum_coeffs","RH"),
                  ("temp_coeffs","T"),
                  ("voc_coeffs","VOC")]


    for item in calibFiles:
        status = _parseCalibration(item[0],item[1],session)
        if not status:
            break

def populateRoomTypes(session):
    """Add Some Default Room Types

    :param session: Session to be used if not the global database session
    """
    log.info("Populating room types")
    
    if not session:
        session = meta.Session()

    roomTypes = [["Bedroom",["Master Bedroom","Second Bedroom","Third Bedroom"]],
                 ["Living Area",["Living Room","Dining Room"]],
                 ["Wet Room",["Bathroom","WC","Kitchen"]],
                 ["Unocupied",["Hallway","Upstairs Hallway","Utility Room","Spare Room"]]
                 ]

    for roomType,rooms in roomTypes:
        
        theType = session.query(RoomType).filter_by(name=roomType).first()
        if theType is None:
            theType = RoomType(name=roomType)
            session.add(theType)
            session.flush()

        for item in rooms:
            theQry = session.query(Room).filter_by(name=item).first()
            if theQry is None:
                session.add(Room(name=item,roomTypeId=theType.id))
        session.flush()
            
    session.flush()
    session.commit()
    session.close()
     

def init_data(session=False):
    """Populate the database with some initial data
    
    :param session: Session to use if not the default
    """

    if not session:
        session = meta.Session()

    log.info("Populating Initial Data using session {0}".format(session))
    populateSensorTypes(session = session)
    populateRoomTypes(session = session)
    populateCalibration(session = session)

