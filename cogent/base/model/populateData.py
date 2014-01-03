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
import sys
import os



#import transaction
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
from nodetype import *

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

#Globals to hold potential locations of Calibration files

def populateSensorTypes(session = False):
    """Populate the database with default sensing types,
    if they do not already exist.
    """
    LOG.debug("Populating SensorTypes")

    if not session:
        session = meta.Session()

    sensorList = [SensorType(id=0, name="Temperature",
                             code="T",
                             units="deg.C",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=1, name="Delta Temperature",
                             code="dT",
                             units="deg.C/s",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=2, name="Humidity",
                             code="RH",
                             units="%",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=3, name="Delta Humidity",
                             code="dRH",
                             units="%/s",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=4, name="Light PAR",
                             code="PAR",
                             units="Lux",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=5, name="Light TSR",
                             code="TSR",
                             units="Lux",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=6, name="Battery Voltage",
                             code="BAT",
                             units="V",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=7, name="Delta Battery Voltage",
                             code="dBT",
                             units="V/s",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=8, name="CO2",
                             code="CO2",
                             units="ppm",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=9, name="Air Quality",
                             code="AQ",
                             units="ppm",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=10, name="VOC",
                             code="VOC",
                             units="ppm",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=11, name="Power",
                             code="POW",
                             units="W",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=12, name="Heat",
                             code="HET",
                             units="W",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=13, name="Duty cycle",
                             code="DUT",
                             units="ms",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=14, name="Error",
                             code="ERR",
                             units="",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=15, name="Power Min",
                             code="PMI",
                             units="w",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=16, name="Power Max",
                             code="PMA",
                             units="w",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=17, name="Power Consumption",
                             code="CON",
                             units="kWh",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=18, name="Heat Energy",
                             code="HEN",
                             units="kWh",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=19, name="Heat Volume",
                             code="HVO",
                             units="L",
                             c0=0., c1=1., c2=0., c3=0.),
                  #!-- RENUMBERED ---
                  SensorType(id=20, name="Delta CO2",
                            code="dCO2",
                            units="ppm/s",
                            c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=21, name="Delta VOC",
                             code="dVOC",
                             units="ppm/s",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=22, name="Delta AQ",
                             code="dAQ",
                             units="v/s",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=23,name="Temperature Health",
                             code="TH",
                             units="%",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=24, name="Temperature Cold",
                             code= "TC",
                             units= "%",
                             c0=0., c1=1., c2=0., c3=0.),    
                  SensorType(id=25,
                             name="Temperature Comfort",
                             code="TM",
                             units="%",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=26,
                             name="Temperature Warm",
                             code="TW",
                             units="%",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=27,
                             name="Temperature Over",
                             code="TO",
                             units="%",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=28,
                             name="Humidity Dry",
                             code="HD",
                             units="%",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=29,
                             name="Humidity Comfort",
                             code="HD",
                             units="%",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=30,
                             name="Humidity Damp",
                             code="HD",
                             units="%",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=31,
                             name="Humidity Risk",
                             code="HR",
                             units="%",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=32,
                             name="CO2 Acceptable",
                             code="CA",
                             units="%",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=33,
                             name="CO2 Minor",
                             code="Cmin",
                             units="%",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=34,
                             name="CO2 Medium",
                             code="CMED",
                             units="%",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=35,
                             name="CO2 Major",
                             code="CMAJ",
                             units="%",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=36,
                             name="VOC Acceptable",
                             code="VA",
                             units="%",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=37,
                             name="VOC Poor",
                             code="VP",
                             units="%",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=38,
                             name="AQ Acceptable",
                             code="AA",
                             units="%",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=39,
                             name="AQ Poor",
                             code="AP",
                             units="%",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=40,
                             name="Opti Smart Count",
                             code="imp",
                             units="imp"),
                  SensorType(id=41,
                             name="Temperature ADC0",
                             code="T",
                             units="deg.C",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id="42",
                             name="Delta Temperature ADC0",
                             code="dT",
                             units="deg.C/s",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=43,
                             name="Gas Pulse Count",
                             code="imp",
                             units="imp",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=44,
                             name= "Delta Opti",
                             code= "imp",
                             units= "imp",
                             c0= 0., c1= 1., c2= 0., c3= 0),
                  SensorType(id= 45, 
                             name= "Window State",
                             code= "ste",
                             units= "ste",
                             c0= 0., c1= 1., c2= 0., c3= 0.),
                  SensorType(id=99, name="Gas Consumption",
                             code="Gas",
                             units="kWh",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=102, name="Outside Temperature",
                             code="ws_temp_out",
                             units="deg.C",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=103, name="Outside Humidity",
                             code="ws_hum_out",
                             units="deg.C",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=104, name="WS Inside Temperature",
                             code="ws_temp_in",
                             units="deg.C",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=105, name="WS Inside Humidity",
                             code="ws_hum_in",
                             units="deg.C",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=106, name="Dew Point",
                             code="ws_dew",
                             units="deg.C",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=107, name="Apparent Temperature",
                             code="ws_apparent_temp",
                             units="deg.C",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=108, name="Wind Gust",
                             code="ws_wind_gust",
                             units="mph",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=109, name="Average Wind Speed",
                             code="ws_wind_ave",
                             units="mph",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=110, name="Wind Direction",
                             code="ws_wind_dir",
                             units="",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=111, name="Wind Chill",
                             code="ws_wind_chill",
                             units="deg.C",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=112, name="Rain Fall",
                             code="ws_rain",
                             units="mm",
                             c0=0., c1=1., c2=0., c3=0.),
                  SensorType(id=113, name="Absolute Pressure",
                             code="ws_abs_pressure",
                             units="hpa",
                             c0=0., c1=1., c2=0., c3=0.),
                  ]
    


    for item in sensorList:        
        LOG.debug("Adding Sensor {0}".format(item.name))
        session.merge(item)

    session.flush()
    session.commit()
    #session.close()


def populateNodeTypes(session = False):
    """Populate the database with default node types,
    if they do not already exist.

    (Added due to alembic revision 1f9a02a1b28
    """

    LOG.debug("Populating SensorTypes")

    if not session:
        session = meta.Session()

    # nodelist = []
    
    nodelist = [{'id': 0, 'name': "Base",
                 'time': "2011-07-10 00:00:00",
                 'seq': 1,
                 'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '31,4'},            
                {'id': 1, 'name': "Current Cost",
                 'time': "2011-07-10 00:00:00",
                 'seq': 1,
                 'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '31,5'},
                {'id': 2, 'name': "CO2",
                 'time': "2011-07-10 00:00:00",
                 'seq': 1,
                 'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '63,4'},
                {'id': 3, 'name': "Air Quality",
                 'time': "2011-07-10 00:00:00",
                 'seq': 1,
                 'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '255,4'},
                {'id': 4, 'name': "Heat Meter",
                 'time': "2011-07-10 00:00:00",
                 'seq': 1,
                 'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '31,4'},
                {'id': 5, 'name': "EnergyBoard",
                 'time': "2011-07-10 00:00:00",
                 'seq': 1,
                 'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '31,4'},
                {'id': 6, 'name': "TempADC0 Node",
                 'time': "2011-07-10 00:00:00",
                 'seq': 1,
                 'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '31,4'},
                {'id': 7, 'name': "Gas Node",
                 'time': "2011-07-10 00:00:00",
                 'seq': 1,
                 'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '31,4'},
                {'id': 8, 'name': "Window Sensor",
                   'time': "2011-07-10 00:00:00",
                   'seq': 1,
                   'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '31,4'},
                {'id': 10, 'name': "ClusterHead CO2",
                 'time': "2011-07-10 00:00:00",
                 'seq': 1,
                 'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '31,4'},
                {'id': 11, 'name': "ClusterHead AQ",
                 'time': "2011-07-10 00:00:00",
                 'seq': 1,
                 'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '31,4'},
                  {'id': 12, 'name': "ClusterHead CC",
                   'time': "2011-07-10 00:00:00",
                   'seq': 1,
                   'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '31,4'}      
                ]
                


    for item in nodelist:
        thisNode = NodeType()
        thisNode.from_dict(item) #Dict based update
        session.merge(thisNode)
        
    # with transaction.manager:
    #     for item in nodelist:
    #         LOG.debug("Adding NodeType {0}".format(item.name))
    #         session.merge(item)

    session.flush()
    session.commit()

def _parseCalibration(filename, sensorcode, session=False):
    """Helper method to Parse a sensor calibration file

    :param filename: Name of file we get coefficients from
    :param sensorcode:
        sensor code of sensor type these Coefficients correspond to
    """

    LOG.debug("Updating Coefficients from {0}".format(filename))

    theFile = "{0}.csv".format(filename)
    LOG.debug("Checking for file {0}".format(theFile))

    #We then want to look relitive to the current path (ie if we are runing in development mode)

    LOG.debug("--> Current Working path is {0}".format(os.getcwd()))

    #There are two places the calibration configuration files should be
    #1) <prefered>  /<base systems path>/share/cogent-viewer/calibration/ 
    #2) <develop>   <basedir>/calibration
    #Where base systems python path path is likely to be /usr on a linux box
    

    if sys.prefix  == "/usr":
        conf_prefix = "/etc" #If its a standard "global" instalation
    else :
        conf_prefix = os.path.join(sys.prefix, "etc")

    basepath = os.path.join(conf_prefix,"cogent-house","calibration",theFile)
    LOG.debug("Looking for Path {0} >{1}<".format(basepath,os.path.exists(basepath)))

    thepath = None

    if os.path.exists(basepath):
        thepath = basepath
    else:
        #Check if we are in the development directory and make use of that instead
        basepath = os.path.join("calibration",theFile)
        if os.path.exists(basepath):
            thepath = basepath

    if thepath is None:
        LOG.warning("** Unable to locate calibration file {0}".format(thepath))
        return False
                   

    LOG.debug("Fetching calibration from {0}".format(thepath))
    # basePath = None
    # for item in CALIB_LOCS:
    #     thePath = os.path.join(*item)
    #     LOG.debug("Looking in path {0}".format(thePath))
    #     if os.path.exists(thePath):
    #         basePath = thePath
    #         LOG.debug("Base Path is {0}".format(basePath))
    #         break

    # if basePath is None:
    #     LOG.warning("** Unable to locate calibration file {0}".format(theFile))
    #     return False
        
    # thePath = os.path.join(basePath,theFile)

    #Find the relevant sensor type
    sensorType = session.query(SensorType).filter_by(code=sensorcode).first()

    try:
        reader = csv.reader(open(thepath,"r"),delimiter=",")
    except IOError,e:
        LOG.warning("Unable to parse calibration {0}".format(e))
        return False


    for row in reader:
        if len(row) == 2:
            nodeId,c = row
            m = 1.0
        elif len(row) == 3:
            nodeId,m,c = row
        else:
            LOG.warning("--> Unable to parse Coefficients")

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
            LOG.debug("--> Creating Node {0}".format(theNode))
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
            LOG.debug("--> Adding New Sensor {0}".format(theSensor))

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
    Populate the Sensor Table with the correct calibration Coefficients for each
    Sensor

    :param session: Session to use if not the default session
    """
    LOG.debug("Populating Calibration Data")
    #List of (file, sensor code) pairs
    calibFiles = [("aq_coeffs","AQ"),
                  ("co2_coeffs","CO2"),
                  ("hum_coeffs","RH"),
                  ("temp_coeffs","T"),
                  ("voc_coeffs","VOC")]


    for item in calibFiles:
        status = _parseCalibration(item[0],item[1],session)

    return

def populateRoomTypes(session):
    """Add Some Default Room Types

    :param session: Session to be used if not the global database session
    """
    LOG.debug("Populating Room Types")

    if not session:
        session = meta.Session()

    roomTypes = [["Bedroom", ["Master Bedroom",
                              "Second Bedroom",
                              "Third Bedroom"]],
                 ["Living Area", ["Living Room",
                                  "Dining Room"]],
                 ["Wet Room", ["Bathroom",
                               "WC",
                               "Kitchen"]],
                 ["Unocupied", ["Hallway",
                                "Upstairs Hallway",
                                "Utility Room",
                                "Spare Room"]]
                 ]


    for roomType, rooms in roomTypes:
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

def init_data(session=False, docalib=True):
    """Populate the database with some initial data

    :param session: Session to use if not the default
    """

    if not session:
        session = meta.Session()
    
    populateSensorTypes(session = session)
    populateNodeTypes(session= session)
    populateRoomTypes(session = session)
    if docalib:
        populateCalibration(session = session)
    #session.commit()
    LOG.debug("Database Population Complete")
