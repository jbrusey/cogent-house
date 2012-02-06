from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
import sqlalchemy.orm.query
from datetime import datetime
try:
    from base.model import *
except:
    from cogent.base.model import *
import csv
import scipy.stats as stats


# Yes, run this when this file is imported
calib = {}

def fetch_calib(filename, dtype):
    calib_file = csv.reader(open('./Calibration/' + filename, 'r'), delimiter=',')

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
    
def get_calibration(session, node_id, reading_type):
    try:
        values = calib[node_id][reading_type]
    except:
        values = (1.0, 0.0)
    return values


reading_types = ['temperature', '', 'humidity', '', 'tsr', 'par', 'battery', '', 'co2', 'aq', 'voc', 'cc']
node_types = ['standard', 'electricity', 'co2', 'aq', 'heat_meter']
reading_limits = {
        'temperature' : (0.0, 50.0),
        'humidity'    : (0.0, 100.0),
        'co2'         : (0.0, 6000.0)
    }


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


def get_house_address(session, house_id):
    row = session.query(House).filter(House.id==house_id).first()
    return row.address


def get_node_locations_by_house(session, house_id, include_external=True):
    node_details={}

    rows = session.query(Node).filter(Node.houseId==house_id).join(House, Room).order_by(House.address, Room.name)
    for row in rows:
        node_id = int(row.id)

        if row.nodeTypeId == node_types.index('electricity'):
            if include_external:
                node_details[node_id] = 'External'
        else:
            node_details[node_id] = row.room.name
    
    return node_details


def get_node_list(session):
    # Can be made faster by not relying on get_node_locations()
    return get_node_locations(session).keys()


def get_data_by_type(session, reading_type, start_time = datetime.fromtimestamp(0), end_time = datetime.now(), filter_values = True):
    rows = _query_by_type(session, reading_type, start_time, end_time, filter_values)
    rows.order_by(Reading.time)

    data = {}
    for row in rows:
        node_id = int(row.nodeId)
        if node_id not in data:
            data[node_id] = []
        data[node_id].append((row.time, row.value))
    
    return data
    

def clean_data(data, reading_type = None):
    if type(data) == list:
        return _clean_data(data, reading_type)
    elif type(data) == dict:
        cleaned = {}
        for key,value in data.iteritems():
            cleaned[key] = clean_data(value, reading_type)
        return cleaned
    elif type(data) == sqlalchemy.orm.query.Query:
        clean_data(data.all(), reading_type)
    else:
        import sys
        print >> sys.stderr, "Bad data for cleaning:", type(data)
        exit(1)


def get_data_by_node_and_type(session, node_id, reading_type, start_time = datetime.fromtimestamp(0), end_time = datetime.now(), filter_values = True):
    rows = _query_by_node_and_type(session, node_id, reading_type, start_time, end_time, filter_values)
    rows.order_by(Reading.time)
    
    data = []
    for time,value in rows:
        data.append((time, value))
    
    return data
    

def _get_outlier_thresholds(data):
    # 1.5 times the IQR from the upper and lower quartiles (2 times the IQR from the median)
    lq  = stats.scoreatpercentile(data, 25)			# Lower quartile (25%)
    uq  = stats.scoreatpercentile(data, 75)			# Upper quartile (75%)
    iqr = uq - lq					                # Interquartile range
    ub  = uq + (1.5 * iqr)			                # Upper outlier threshold
    lb  = lq - (1.5 * iqr)			                # Lower outlier threshold
    return (ub, lb)

        
def get_data_by_type_clean(session, reading_type, start_time = datetime.fromtimestamp(0), end_time = datetime.now()):
    data = get_data_by_type(session, reading_type, start_time, end_time)
    
    cleaned = {}
    for node_id, readings in data.iteritems():
        cleaned[node_id] = _clean_data(readings, reading_type)
        
    return cleaned

def get_data_by_node_and_type_clean(session, node_id, reading_type, start_time = datetime.fromtimestamp(0), end_time = datetime.now()):
    data = get_data_by_node_and_type(session, node_id, reading_type, start_time, end_time)
    return _clean_data(data, reading_type)

def _clean_data(data, reading_type = None):
    if reading_type != None and reading_type in reading_limits:
        lt, ut = reading_limits[reading_type]
        data = filter(lambda x: x[1] >= lt and x[1] <= ut, data)
    ub, lb = _get_outlier_thresholds([x[1] for x in data])
    cleaned = []
    for (time, value) in data:
        if ((value < ub) and (value > lb)):
            cleaned.append((time, value))
    return cleaned


def get_clean_data_test():
    time_format = "%d/%m/%Y"
    sd=datetime.fromtimestamp(time.mktime(time.strptime("01/01/2012", time_format)))
    ed=datetime.fromtimestamp(time.mktime(time.strptime("05/01/2012", time_format)))
    db_engine = create_db_engine_mysql('ross', "SampsonClose")
    session = create_session(db_engine)
    qry = get_data_by_type_clean(session, 'temperature', sd, ed)
    qry = get_data_by_node_and_type_clean(session, 11, 'temperature', sd, ed)
    

def get_yield(session, node_id, reading_type, start_time = datetime.fromtimestamp(0), end_time = datetime.now()):
    days = int((end_time - start_time).days)
    expected_rows = float(days * 288.)
    
    rows = _query_by_node_and_type(session, node_id, reading_type, start_time, end_time)
    row_count = float(rows.count())

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

