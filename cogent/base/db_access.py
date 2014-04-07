from sqlalchemy import create_engine, and_, distinct, select, alias
from sqlalchemy.orm import sessionmaker
import sqlalchemy.orm.query
from datetime import datetime
import os.path
import csv
import scipy.stats as stats
import sys


from cogent.base.model import *


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


# Yes, run this when this file is imported
calib = {}

def fetch_calib(filename, dtype):
    calib_file = csv.reader(open(os.path.join(os.path.dirname(__file__), 'Calibration', filename), 'r'), delimiter=',')

    for row in calib_file:
        if len(row) == 2:
            node_id,c = row
            m = 1.0
        elif len(row) == 3:
            node_id,m,c = row
        else:
            continue
        
        if m == '':
            m = 1.0
        if c == '':
            c = 0.0
            
        node_id = int(node_id)
        m = float(m)
        c = float(c)
        
        if node_id not in calib:
            calib[node_id] = {}
        
        calib[node_id][dtype] = (m, c)

fetch_calib('temp_coeffs.csv', 'temperature')
fetch_calib('hum_coeffs.csv', 'humidity')
fetch_calib('co2_coeffs.csv', 'co2')
fetch_calib('voc_coeffs.csv', 'voc')
fetch_calib('aq_coeffs.csv', 'aq')
fetch_calib('cc_coeffs.csv', 'cc')
    
# Get calibration constants from local files. Once Sampson Close is set up,
# this (and the mess above) can go away.
def get_calibration(session, node_id, reading_type):
    try:
        values = calib[node_id][reading_type]
    except:
        values = (1.0, 0.0)
    return values


# Get calibration constants from the database. Note that Sampson Close does not
# have this set up yet.
def get_calibration_db(session, node_id, reading_type):
	rtype_id = reading_types.index(reading_type)
	row = session.query(Sensor.calibrationSlope, Sensor.calibrationOffset).filter(and_(Sensor.nodeId == node_id, Sensor.sensorTypeId == rtype_id)).first()
	if row == None: return (1.0, 0.0)
	return (row.calibrationSlope, row.calibrationOffset)


# Calibrate data.
def calibrate(session, data, node_id = None, reading_type = None, cal_func = get_calibration):
    if node_id != None or reading_type != None:
        print >> sys.stderr, "[db_access.calibrate] Use of the node_id and reading_type parameters is deprecated."

    if reading_type == None:
        if type(data) == ReadingList:
            reading_type = data.get_meta_data('reading_type')
        else:
            print >> sys.stderr, "No reading type specified for calibration."
            exit(1)
    
    if node_id == None:
        if type(data) == ReadingList:
            node_id = data.get_meta_data('node_id')
        else:
            print >> sys.stderr, "No node_id specified for calibration."
            exit(1)
    
    # Until the copy is transparent
    md = data.meta_data
    
    m, c = cal_func(session, node_id, reading_type)
    if data.get_meta_data('has_deltas'):
        data = ReadingList((row[0], m * row[1] + c, row[2]) for row in data)
    else:
        data = ReadingList((row[0], m * row[1] + c) for row in data)
    
    # Until the copy is transparent
    data.meta_data = md
    return data


def _query_by_node_and_type_with_join_target(session, node_id, reading_type, start_time, end_time, target, filter_values = True):
    rtype_id = reading_types.index(reading_type)
    if reading_type in reading_limits and filter_values:
        return session.query(Reading.time, Reading.value, target.c.Reading_value).filter(and_(
            Reading.time >= start_time,
            Reading.time < end_time,
            Reading.nodeId == node_id,
            Reading.typeId == rtype_id,
            Reading.value >= reading_limits[reading_type][0],
            Reading.value <= reading_limits[reading_type][1]))
    else:
        return session.query(Reading.time, Reading.value, target.c.Reading_value).filter(and_(
            Reading.time >= start_time,
            Reading.time < end_time,
            Reading.nodeId == node_id,
            Reading.typeId == rtype_id))

def _query_by_node_and_type(session, node_id, reading_type, start_time, end_time, filter_values = True):
    rtype_id = reading_types.index(reading_type)
    if reading_type in reading_limits and filter_values:
        return session.query(Reading.time, Reading.value).filter(and_(
            Reading.time >= start_time,
            Reading.time < end_time,
            Reading.nodeId == node_id,
            Reading.typeId == rtype_id,
            Reading.value >= reading_limits[reading_type][0],
            Reading.value <= reading_limits[reading_type][1]))
    else:
        return session.query(Reading.time, Reading.value).filter(and_(
            Reading.time >= start_time,
            Reading.time < end_time,
            Reading.nodeId == node_id,
            Reading.typeId == rtype_id))



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


def _query_by_type(session, reading_type, start_time, end_time, filter_values = True):
    rtype_id = reading_types.index(reading_type)
    if reading_type in reading_limits and filter_values:
        return session.query(Reading.nodeId, Reading.time, Reading.value).filter(and_(
            Reading.time >= start_time,
            Reading.time < end_time,
            Reading.typeId == rtype_id,
            Reading.value >= reading_limits[reading_type][0],
            Reading.value <= reading_limits[reading_type][1]))
    
    else:
        return session.query(Reading.nodeId, Reading.time, Reading.value).filter(and_(
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


def get_node_locations_by_house(session, house_id, include_external=True):
    node_details={}

    rows = session.query(Node).filter(Node.houseId==house_id).join(House, Room).order_by(House.address, Room.name)
    for row in rows:
        node_id = int(row.id)

        if row.nodeTypeId == node_types.index('electricity'):
            if include_external:
                node_details['External'] = node_id
        else:
            node_details[row.room.name] = node_id
    
    return node_details



def get_data_by_type(session, reading_type, start_time = datetime.fromtimestamp(0), end_time = datetime.utcnow(), postprocess=True, with_deltas=False):
    if reading_type in ['d_temperature', 'd_humidity', 'd_battery', 'cc', 'duty', 'error', 'size_v1', 'cc_min', 'cc_max', 'cc_kwh'] and postprocess:
        print >> sys.stderr, "Cleaning is being applied to reading type %s, this is not generally wanted. Check your code!" % reading_type

    if with_deltas:
        delta_rows = _query_by_type(session, 'd_' + reading_type, start_time, end_time, filter_values = False).with_labels().subquery()
        rows = _query_by_type_with_join_target(session, reading_type, start_time, end_time, delta_rows, filter_values = False)
        rows = rows.join((delta_rows, Reading.time == delta_rows.c.Reading_time))
    else:
        rows = _query_by_type(session, reading_type, start_time, end_time, filter_values = False)
        
    rows.order_by(Reading.time)
    
    data = {}
    for row in rows:
        node_id = int(row.nodeId)
        if node_id not in data:
            data[node_id] = ReadingList()
            data[node_id].set_meta_data('reading_type', reading_type)
            data[node_id].set_meta_data('node_id', node_id)
            data[node_id].set_meta_data('has_deltas', with_deltas)

        if with_deltas:
            data[node_id].append((row.time, row.value, row.Reading_value))
        else:
            data[node_id].append((row.time, row.value))
    
    if postprocess:
        for node_id,values in data.iteritems():
            data[node_id] = calibrate(session, values, cal_func = cal_func)
        data = clean_data(session, data)
    
    return data


def get_data_by_node_and_type(session, node_id, reading_type, start_time = datetime.fromtimestamp(0), end_time = datetime.utcnow(), postprocess=True, cal_func=get_calibration, with_deltas=False):
    if reading_type in ['d_temperature', 'd_humidity', 'd_battery', 'cc', 'duty', 'error', 'size_v1', 'cc_min', 'cc_max', 'cc_kwh'] and postprocess:
        print >> sys.stderr, "Cleaning is being applied to reading type %s, this is not generally wanted. Check your code!" % reading_type
     
    if with_deltas:
        delta_rows = _query_by_node_and_type(session, node_id, 'd_' + reading_type, start_time, end_time, filter_values = False).with_labels().subquery()
        rows = _query_by_node_and_type_with_join_target(session, node_id, reading_type, start_time, end_time, delta_rows, filter_values = False)
        rows = rows.join((delta_rows, Reading.time == delta_rows.c.Reading_time))
    else:
        rows = _query_by_node_and_type(session, node_id, reading_type, start_time, end_time, filter_values = False) 
        
    rows.order_by(Reading.time)
    
    data = ReadingList()
    data.set_meta_data('reading_type', reading_type)
    data.set_meta_data('node_id', node_id)
    data.set_meta_data('has_deltas', with_deltas)
    for row in rows:
        if with_deltas:
            data.append((row.time, row.value, row.Reading_value))
        else:
            data.append((row.time, row.value))

    if postprocess:
        data = calibrate(session, data, cal_func = cal_func)
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


def get_yield(session, node_id, reading_type, start_time = datetime.fromtimestamp(0), end_time = datetime.utcnow()):
    days = int((end_time - start_time).days)
    expected_rows = float(days * 288.)
    
    row_count = _query_by_node_and_type(session, node_id, reading_type, start_time, end_time).count()

    return (row_count * 100.0) / expected_rows



def get_houses(session):
    houses = {}
    for hid, addr, depl in session.query(House.id, House.address, Deployment.name):
        if depl not in houses:
            houses[depl] = []
        houses[depl].append((hid, addr))
    return houses


def node_is_battery_powered(session, node_id):
    return node_id < 2000

