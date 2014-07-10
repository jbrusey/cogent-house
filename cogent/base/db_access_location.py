from sqlalchemy import create_engine, and_, distinct, select, alias, distinct
from sqlalchemy.orm import sessionmaker
import sqlalchemy.orm.query
#from datetime import datetime, timedelta
import datetime
import os.path
import csv
import scipy.stats as stats
import sys

from cogent.base.model import *


def get_calibration(session, node_id, reading_type):
    return (1.0, 0.0)

# A list that we can store metadata about (the reading_type for the data it
# contains for example).
class ReadingList(list):
    def __init__(self, *arg, **kwarg):
        list.__init__(self, *arg, **kwarg)
        self.meta_data = {}

    def set_meta_data(self, key, value):
        self.meta_data[key] = value
        
    def get_meta_data(self, key):
        return self.meta_data[key]


# The list of reading_types. The position in the list corresponds to the ID used in the database.
reading_types = ['temperature', 'd_temperature', 'humidity', 'd_humidity', 'tsr', 'par', 'battery', 'd_battery', 'co2', 'aq', 'voc', 'cc', 'duty', 'error', 'size_v1', 'cc_min', 'cc_max', 'cc_kwh']

# The list of node types. The position in the list corresponds to the ID used in the database.
node_types = ['standard', 'electricity', 'co2', 'aq', 'heat_meter']

# The reading limits for different types of data. These are used to exclude
# readings that are invalid (outside of the sensing range for example).
reading_limits = {
        'temperature' : (0.0, 50.0),
        'humidity'    : (0.0, 100.0),
        'co2'         : (0.0, 6000.0)
    }


def _locCalibrateReadings(session,theQuery):
    """Generator object to calibate all readings,
    hopefully this gathers all calibration based readings into one 
    area

    :param theQuery: SQLA query object containing Reading values"""
    #Dictionary to hold all sensor paramters
    sensorParams = {}

    for reading in theQuery:

        theSensor = sensorParams.get((reading.nodeId,reading.typeId),None)
        log.debug("Original Reading {0} Sensor is {1}".format(reading,theSensor))
        if not theSensor:
            theSensor = session.query(sensor.Sensor).filter_by(nodeId = reading.nodeId,sensorTypeId = reading.typeId).first()
            if theSensor is None:
                theSensor = sensor.Sensor(calibrationSlope = 1.0,calibrationOffset = 0.0)
            sensorParams[(reading.nodeId,reading.typeId)] = theSensor

        #Then add the offset etc
        cReading = Reading(time=reading.time,
                           nodeId = reading.nodeId,
                           typeId = reading.typeId,
                           locationId = reading.locationId,
                           value = theSensor.calibrationOffset + (theSensor.calibrationSlope * reading.value),
                           )
    
        yield cReading



def _query_by_location_and_type_with_join_target(session, loc_id, reading_type, start_time, end_time, target, filter_values = True, calib=True):
    rtype_id = reading_types.index(reading_type)
    if reading_type in reading_limits and filter_values:
        theQuery = session.query(Reading, target.c.Reading_value).filter(and_(
            Reading.time >= start_time,
            Reading.time < end_time,
            Reading.locationId == loc_id,
            Reading.typeId == rtype_id,
            Reading.value >= reading_limits[reading_type][0],
            Reading.value <= reading_limits[reading_type][1])).order_by(Reading.time)
	if calib:
	        return _locCalibrateReadings(session,theQuery)
	else:
		return theQuery

    else:
        theQuery = session.query(Reading, target.c.Reading_value).filter(and_(
            Reading.time >= start_time,
            Reading.time < end_time,
            Reading.locationId == loc_id,
            Reading.typeId == rtype_id)).order_by(Reading.time)
	if calib:
	        return _locCalibrateReadings(session,theQuery)
	else:
		return theQuery



def _query_by_type_location(session, reading_type, start_time, end_time, filter_values = True, calib=True):
    rtype_id = reading_types.index(reading_type)
    if reading_type in reading_limits and filter_values:
        theQuery = session.query(Reading).filter(and_(
            Reading.time >= start_time,
            Reading.time < end_time,
            Reading.typeId == rtype_id,
            Reading.value >= reading_limits[reading_type][0],
            Reading.value <= reading_limits[reading_type][1]))
 	if calib:
	        return _locCalibrateReadings(session,theQuery)
	else:
		return theQuery   
    else:
        theQuery = session.query(Reading).filter(and_(
            Reading.time >= start_time,
            Reading.time < end_time,
            Reading.typeId == rtype_id))
	if calib:
	        return _locCalibrateReadings(session,theQuery)
	else:
		return theQuery


def _query_by_location_and_type(session, loc_id, reading_type, start_time, end_time, filter_values = True, calib=True):
    rtype_id = reading_types.index(reading_type)
    if reading_type in reading_limits and filter_values:
        theQuery =  session.query(Reading).filter(and_(
            Reading.time >= start_time,
            Reading.time < end_time,
            Reading.locationId == loc_id,
            Reading.typeId == rtype_id,
            Reading.value >= reading_limits[reading_type][0],
            Reading.value <= reading_limits[reading_type][1])).order_by(Reading.time)
	if calib:
	        return _locCalibrateReadings(session,theQuery)
	else:
		return theQuery
    else:
        theQuery =  session.query(Reading).filter(and_(
            Reading.time >= start_time,
            Reading.time < end_time,
            Reading.locationId == loc_id,
            Reading.typeId == rtype_id)).order_by(Reading.time)
	if calib:
	        return _locCalibrateReadings(session,theQuery)
	else:
		return theQuery
    
def _query_by_type_with_join_target(session, reading_type, start_time, end_time, target, filter_values = True):
    rtype_id = reading_types.index(reading_type)
    if reading_type in reading_limits and filter_values:
        return session.query(Reading.nodeId, Reading.time, Reading.value, target.c.Reading_value).filter(and_(
            Reading.time >= start_time,
            Reading.time < end_time,
            Reading.typeId == rtype_id,
            Reading.value >= reading_limits[reading_type][0],
            Reading.value <= reading_limits[reading_type][1]))
    
    else:
        return session.query(Reading.nodeId, Reading.time, Reading.value, target.c.Reading_value).filter(and_(
            Reading.time >= start_time,
            Reading.time < end_time,
            Reading.typeId == rtype_id))


def create_db_engine_mysql(username, database, host='localhost'):
    _DBURL = 'mysql://%s@%s/%s?connect_timeout=1' % (username, host, database)
    engine = create_engine(_DBURL, echo=False)
    return engine


def create_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    return Session()
    

def create_session_mysql(username, database, host='localhost'):
    db_engine = create_db_engine_mysql(username, database, host)
    return create_session(db_engine)

def get_house_details(session, house_id):
    row = session.query(House).filter(House.id==house_id).first()
    return row

def get_house_address(session, house_id):
    row = session.query(House).filter(House.id==house_id).first()
    return row.address


def get_house_id(session, address):
    row = session.query(House).filter(House.address==address).first()
    return row.id


def get_locations_by_house(session, house_id, include_external=True):
    node_details={}

    rows = session.query(Location).filter(Location.houseId==house_id).join(House, Room).order_by(House.address, Room.name)
    for row in rows:
        node_id = int(row.id)
        node_details[row.room.name] = node_id   
    return node_details


def get_nodeId_by_location(session, loc_id, start_time, end_time, type_id=0):
    nid=None
    rows =  session.query(Reading.nodeId).filter(and_(
            Reading.time >= start_time,
            Reading.time < end_time,
            Reading.locationId == loc_id,
            Reading.typeId == type_id)).first()

    nid = int(rows.nodeId)
    return nid


def get_data_by_location_and_type(session, loc_id, reading_type, start_time = datetime.datetime.fromtimestamp(0), end_time = datetime.datetime.utcnow(), postprocess=True, cal_func=get_calibration, with_deltas=False):
    if reading_type in ['d_temperature', 'd_humidity', 'd_battery', 'cc', 'duty', 'error', 'size_v1', 'cc_min', 'cc_max', 'cc_kwh'] and postprocess:
        print >> sys.stderr, "Cleaning is being applied to reading type %s, this is not generally wanted. Check your code!" % reading_type
     
    if with_deltas:
        delta_rows = _query_by_location_and_type(session, loc_id, 'd_' + reading_type, start_time, end_time, filter_values = False).with_labels().subquery()
        rows = _query_by_location_and_type_with_join_target(session, loc_id, reading_type, start_time, end_time, delta_rows, filter_values = False)
        rows = rows.join((delta_rows, Reading.time == delta_rows.c.Reading_time))
    else:
        rows = _query_by_location_and_type(session, loc_id, reading_type, start_time, end_time, filter_values = False) 
    


    data = ReadingList()
    data.set_meta_data('reading_type', reading_type)
    data.set_meta_data('location_id', loc_id)
    data.set_meta_data('has_deltas', with_deltas)
    for row in rows:
        if with_deltas:
            data.append((row.time, row.value, row.Reading_value))
        else:
            data.append((row.time, row.value))

    if postprocess:
        data = clean_data(session, data)
    
    return data


def get_location_types(session, loc_id, start_time = datetime.datetime.fromtimestamp(0), end_time = datetime.datetime.utcnow()):
    theQuery =  session.query(distinct(Reading.typeId)).filter(and_(
        Reading.time >= start_time,
        Reading.time < end_time,
        Reading.locationId == loc_id)).order_by(Reading.time)

    types=[]
    for row in theQuery:
        types.append(int(row[0]))
    
    return types



def get_data_by_location_and_type_with_battery(session, loc_id, reading_type, start_time = datetime.datetime.fromtimestamp(0), end_time = datetime.datetime.utcnow(), postprocess=True):
    if reading_type in ['d_temperature', 'd_humidity', 'd_battery', 'cc', 'duty', 'error', 'size_v1', 'cc_min', 'cc_max', 'cc_kwh'] and postprocess:
        print >> sys.stderr, "Cleaning is being applied to reading type %s, this is not generally wanted. Check your code!" % reading_type
     
    battery_rows = _query_by_location_and_type(session, loc_id, "battery", start_time, end_time, filter_values = False,calib=False).with_labels().subquery()
    rows = _query_by_location_and_type_with_join_target(session, loc_id, reading_type, start_time, end_time, battery_rows, filter_values = False,calib=False)
    rows = rows.join((battery_rows, Reading.time == battery_rows.c.Reading_time))

    data = ReadingList()
    data.set_meta_data('reading_type', reading_type)
    data.set_meta_data('location_id', loc_id)
    for row in rows:
        data.append((row[0].time, row[0].value, row[1]))

    if postprocess:
        data = clean_data(session, data)
    
    return data





def get_data_by_type_location(session, reading_type, start_time = datetime.datetime.fromtimestamp(0), end_time = datetime.datetime.utcnow(), postprocess=True, with_deltas=False):
    if reading_type in ['d_temperature', 'd_humidity', 'd_battery', 'cc', 'duty', 'error', 'size_v1', 'cc_min', 'cc_max', 'cc_kwh'] and postprocess:
        print >> sys.stderr, "Cleaning is being applied to reading type %s, this is not generally wanted. Check your code!" % reading_type

    if with_deltas:
        delta_rows = _query_by_type(session, 'd_' + reading_type, start_time, end_time, filter_values = False).with_labels().subquery()
        rows = _query_by_type_with_join_target(session, reading_type, start_time, end_time, delta_rows, filter_values = False)
        rows = rows.join((delta_rows, Reading.time == delta_rows.c.Reading_time))
    else:
        rows = _query_by_type_location(session, reading_type, start_time, end_time, filter_values = False)
    
    data = {}
    for row in rows:
        loc_id = int(row.locationId)
        if loc_id not in data:
            data[loc_id] = ReadingList()
            data[loc_id].set_meta_data('reading_type', reading_type)
            data[loc_id].set_meta_data('loc_id', loc_id)
            data[loc_id].set_meta_data('has_deltas', with_deltas)

        if with_deltas:
            data[loc_id].append((row.time, row.value, row.Reading_value))
        else:
            data[loc_id].append((row.time, row.value))
    
    if postprocess:
        data = clean_data(session, data)
    
    return data

    

def clean_data(session, data, reading_type = None):
    if len(data) == 0: return data

    if type(data) == list or type(data) == ReadingList:
        return _clean_data(session, data, reading_type)
    elif type(data) == dict:
        cleaned = {}
        for key,value in data.iteritems():
            cd = clean_data(session, value, reading_type)
            if len(cd) > 0: cleaned[key] = cd
        return cleaned
    elif type(data) == sqlalchemy.orm.query.Query:
        clean_data(session, data.all(), reading_type)
    else:
        import sys
        print >> sys.stderr, "Bad data for cleaning:", type(data)
        exit(1)

def _clean_data(session, data, reading_type = None):
    # Until the copy is transparent
    md = data.meta_data
    
    if reading_type != None:
        print >> sys.stderr, "[db_access._clean_data] Use of the reading_type parameter is deprecated."

    if type(data) == ReadingList and reading_type == None:
        reading_type = data.get_meta_data('reading_type')

    if reading_type != None and reading_type in reading_limits:
        lt, ut = reading_limits[reading_type]
        data = filter(lambda x: x[1] >= lt and x[1] <= ut, data)

    ub, lb = _get_outlier_thresholds([x[1] for x in data])
    data = filter(lambda x: x[1] >= lb and x[1] <= ub, data)

    # Until the copy is transparent
    data = ReadingList(data)
    data.meta_data = md

    return data
    

def _get_outlier_thresholds(data):
    # 1.5 times the IQR from the upper and lower quartiles (2 times the IQR from the median)
    lq  = stats.scoreatpercentile(data, 25)			# Lower quartile (25%)
    uq  = stats.scoreatpercentile(data, 75)			# Upper quartile (75%)
    iqr = uq - lq					                # Interquartile range
    ub  = uq + (1.5 * iqr)			                # Upper outlier threshold
    lb  = lq - (1.5 * iqr)			                # Lower outlier threshold
    return (ub, lb)


def get_yield(session, node_id, reading_type, start_time = datetime.datetime.fromtimestamp(0), end_time = datetime.datetime.utcnow()):
    days = int((end_time - start_time).days)
    expected_rows = float(days * 288.)

    return 100.0
    row_count = _query_by_node_and_type(session, node_id, reading_type, start_time, end_time).count()

    return (row_count * 100.0) / expected_rows


def get_yield_location(session, loc_id, reading_type, start_time = datetime.datetime.fromtimestamp(0), end_time = datetime.datetime.utcnow()):
    days = int((end_time - start_time).days)
    expected_rows = float(days * 288.)
    
    rows = _query_by_location_and_type(session, loc_id, reading_type, start_time, end_time)
    row_count=len(list(rows))
   
    return (row_count * 100.0) / expected_rows
    
def get_yield_by_nodes_and_date(session, hnum, reading_type, start_time = datetime.datetime.fromtimestamp(0), end_time = datetime.datetime.utcnow()):

    yields={}
    expected_rows = 288.
    d = datetime.timedelta(days=1)
    locations = get_locations_by_house(session, hnum)
    

    
    for room,lid in locations.iteritems():
        start = start_time
        plus_one = start_time + d
      	while start < end_time:
      	    rows = _query_by_location_and_type(session, lid, reading_type, start, plus_one)
            row_count=len(list(rows))
            
            if room not in yields:            
                yields[room]={}
                
            yields[room][start] = (row_count * 100.0) / expected_rows
            
            start = start + d
            plus_one = plus_one + d
  	
    return yields



def get_houses(session):
    houses = {}
    for hid, addr, depl in session.query(House.id, House.address, Deployment.name):
        if depl not in houses:
            houses[depl] = []
        houses[depl].append((hid, addr))
    return houses


def node_is_battery_powered(node_id):
    return node_id < 2000



def node_has_co2(session, node_id):
    #Fuck It
    #co2 is type 8
    qry = session.query(Reading).filter_by(nodeId = node_id,
                                           typeId = 8)
    return qry.first()

