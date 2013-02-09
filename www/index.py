#
# mod_python web server for simple display of cogenthouse node status
#
# author: J. Brusey, May 2011
#
from __future__ import with_statement
import cStringIO
import time
from datetime import datetime, timedelta
import urllib
# set the home to a writable directory
import os
os.environ['HOME']='/tmp'
from threading import Lock
_lock = Lock()
import numpy as np

# do this before importing pylab or pyplot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

from cogent.base.model import *
from sqlalchemy import create_engine, and_, or_, distinct, func, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound


_DBURL = "mysql://chuser@localhost/ch?connect_timeout=1"

engine = create_engine(_DBURL, echo=False, pool_recycle=60)
#engine.execute("pragma foreign_keys=on")
init_model(engine)

_periods = {
    "hour" : 60,
    "day" : 1440,
    "week" : 1440*7,
    "month" : 1440 * 7 * 52 / 12}

_navs = [
    ("Home", "index.py")
    ]

_sidebars = [
    ("Temperature", "allGraphs?typ=0", "Show temperature graphs for all nodes"),
    ("Temperature Exposure", "tempExposure", "Show temperature exposure graphs for all nodes"),
    ("Humidity", "allGraphs?typ=2", "Show humidity graphs for all nodes"),
    ("Humidity Exposure", "humExposure", "Show humidity exposure graphs for all nodes"),
    ("CO<sub>2</sub>", "allGraphs?typ=8", "Show CO2 graphs for all nodes"),
    ("AQ", "allGraphs?typ=9", "Show air quality graphs for all nodes"),
    ("VOC", "allGraphs?typ=10", "Show volatile organic compound (VOC) graphs for all nodes"),
    ("Electricity", "allGraphs?typ=11", "Show electricity usage for all nodes"),
    ("Battery", "allGraphs?typ=6", "Show node battery voltage"),
    ("Duty cycle", "allGraphs?typ=13", "Show transmission delay graphs"),
    ("Bathroom v. Elec.", "bathElec", "Show bathroom versus electricity"),

    ("Network tree", "treePage", "Show a network tree diagram"),
    ("Missing and extra nodes", "missing", "Show unregistered nodes and missing nodes"),
    ("Packet yield", "yield24", "Show network performance"),
    ("Long term yield", "dataYield", "Show network performance"),
    ("Low batteries", "lowbat", "Report any low batteries"),
    ("View log", "viewLog", "View a detailed log"),
    ("Export data", "exportDataForm", "Export data to CSV"),

     ]

def _url(path, query=None):
    if query is None or len(query) == 0:
        return path
    else:
        return path + "?" + urllib.urlencode(query)

def _main(html):
    return '<div id="main">' + html + '</div>';

def _wrap(html):
    return '<div id="wrap">' + html + '</div>';

def _nav():
    return ('<div id="nav">' +
            '<ul>' + 
            ''.join(['<li><a href="%s" title="jump to %s">%s</a></li>' % (b,a,a) for (a,b) in _navs]) +
            '</ul>' +
            '</div>')

def _sidebar():
    return ('<div id="sidebar">' +
            '<ul>' + 
            ''.join(['<li><a href="%s" title="%s">%s</a></li>' % (b,c,a) for (a,b,c) in _sidebars]) +
            '</ul>' +
            '</div>')

def _page(title='No title', html=''):
    return (_head(title) +
            _wrap(_header(title) +
                  _nav() +
                  _main(html) +
                  _sidebar() +
                  _footer()) +
            _foot())

def _head(title='No title'):
    return ('<!doctype html><html><head><title>CogentHouse Maintenance Portal - %s</title></head>' % title +
            '<link rel="stylesheet" type="text/css" href="../style/ccarc.css" />'
            '<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />'
            '<script type="text/javascript" src="../scripts/datePicker.js"></script>' +
            '<body>')

def _foot():
    return '</body></html>'
            
def _header(title):
    return ('<div id="header"><h1>%s</h1></div>' % (title))

def _footer():
    return '<div id="footer">CogentHouse &copy; <a href="http://cogentcomputing.org" title="Find out more about Cogent">Cogent Computing Applied Research Centre</a></div>'

def _redirect(url=""):
        return "<!doctype html><html><head><meta http-equiv=\"refresh\" content=\"0;url=%s\"></head><body><p>Redirecting...</p></body></html>" % url
    

        

def tree(req, period='hour'):
    try:
        mins = _periods[period]
    except:
        mins = 60
    
    try:
        session = Session()
        from subprocess import Popen, PIPE
        req.content_type = "image/svg+xml"
#        req.content_type = "text/plain"

        #t = datetime.utcnow() - timedelta(minutes=mins)

        p = Popen("dot -Tsvg", shell=True, bufsize=4096,
#        p = Popen("cat", shell=True, bufsize=4096,
              stdin=PIPE, stdout=PIPE, close_fds=True)
        (child_stdin, child_stdout) = (p.stdin, p.stdout)
        
        with p.stdin as dotfile:
            dotfile.write("digraph {");
            for (ni,pa) in session.query(NodeState.nodeId,
                                            NodeState.parent
                                            ).group_by(NodeState.nodeId, NodeState.parent):#.filter(NodeState.time>t):
                
                dotfile.write("%d->%d;" % (ni, pa))
            dotfile.write("}");

        return p.stdout.read()

    finally:
        session.close()


def treePage(period='hour'):
    s = ['<p>']
    for k in sorted(_periods, key=lambda k: _periods[k]):
        if k == period:
            s.append(" %s " % k)
        else:
            s.append(' <a href="%s" title="change period to %s">%s</a> ' % (_url("treePage", [('period', k)]),
                                                                                              k, k))

    s.append('<p>')
    u = _url("tree",[('period', period)])
    s.append('<a href="%s" title="click to zoom">' % u)
    s.append('<img src="%s" alt="network tree diagram" width="700"/></a></p>' % u)

    return _page('Network tree diagram', ''.join(s))

def index():
    s=['']
    # s.append('<p><a href="allGraphs?typ=0">Temperature Data</a></p>')
    # s.append('<p><a href="allGraphs?typ=2">Humidity Data</a></p>')
    # s.append('<p><a href="allGraphs?typ=6">Battery Data</a></p>')
    # s.append('<p><a href="allGraphs?typ=8">CO2 Data</a></p>')
    # s.append('<p><a href="allGraphs?typ=9">AQ Data</a></p>')
    # s.append('<p><a href="allGraphs?typ=10">VOC Data</a></p>')
    # s.append('<p><a href="allGraphs?typ=11">Current Cost Data</a></p>')
    # s.append('<p><a href="lastreport" title="jump to last report">Last Report</a></p>')
    # s.append('<p><a href="dataYield" title="jump to yield since first heard">Yield since first heard</a></p>')
    s.append("""<p>
    Welcome to the CogentHouse Maintenance Portal</p>
    <p>This portal can be used to monitor your deployed CogentHouse sensors and to view graphs of all recorded data.</p>
    """)
    return _page('Home page', ''.join(s))






def humExpNodeGraph(node=None):
    try:
        session = Session()

        (n, h, r) = session.query(Node.id, House.address, Room.name).join(Location, House, Room).filter(Node.id==int(node)).one()
        s = ['<p>']
 
        u = _url("humExpGraph", [('node', node)])
        s.append('<p><div id="grphtitle">%s</div><img src="%s" alt="graph for node %s" width="700" height="400"></p>' % (h + ": " + r + " (" + node + ")", u, node))

        return _page('Time series graph', ''.join(s))
    finally:
        session.close()


def humExpGraph(req,node='64', debug=None, fmt='bo'):
    col=["#FF8C00", "#006400", "#6495ED", "#00008B"]
    try:
        session = Session()
        
        debug = (debug is not None)
        
        endts = datetime.utcnow()
        
        t=[]
        bv=[]
        dry=[]
        comfort=[]
        damp=[]
        risk=[]
        
        dryqry = session.query(Reading.time,Reading.value).filter(
            and_(Reading.nodeId == int(node),
                 Reading.typeId == 56)).order_by(Reading.time)
            
        for qt, qv in dryqry:
            bv.append(100.0)
            t.append(matplotlib.dates.date2num(qt))
            dry.append(qv)
            lastdry=qv
        dry.append(lastdry)

        comfortqry = session.query(Reading.time,Reading.value).filter(
            and_(Reading.nodeId == int(node),
                 Reading.typeId == 57)).order_by(Reading.time)

        for qt, qv in comfortqry:
            comfort.append(qv)
            lastcomfort=qv
        comfort.append(lastcomfort)

        dampqry = session.query(Reading.time,Reading.value).filter(
            and_(Reading.nodeId == int(node),
                 Reading.typeId == 58)).order_by(Reading.time)

        for qt, qv in dampqry:
            damp.append(qv)
            lastdamp=qv
        damp.append(lastdamp)

        riskqry = session.query(Reading.time,Reading.value).filter(
            and_(Reading.nodeId == int(node),
                 Reading.typeId == 59)).order_by(Reading.time)

        for qt, qv in riskqry:
            risk.append(qv)
            lastrisk=qv
        risk.append(lastrisk)

        #do additions to give relative locations on the graph
        dry=np.array(dry)
        comfort=np.array(comfort)+dry
        damp=np.array(damp)+comfort
        risk=np.array(risk)+damp

        req.content_type = "image/png"

        nid=int(node)
        if not debug:
            with _lock:
                fig = plt.figure()
                fig.set_size_inches(7,4)
                ax = fig.add_subplot(111)
                ax.set_autoscaley_on(False)
                ax.set_autoscalex_on(False)
                endts=matplotlib.dates.date2num(datetime.utcnow())
                ax.set_xlim(t[0],endts)
                ax.set_ylim(0,100)


                if len(t) > 0:                            

                    t.append(endts)
                    bv.append(100.0)
                    ax.fill_between(t, 0, risk, facecolor=col[3])
                    ax.fill_between(t, 0, damp, facecolor=col[2])
                    ax.fill_between(t, 0, comfort, facecolor=col[1])
                    ax.fill_between(t, 0, dry, facecolor=col[0])

                    ax.plot_date(t, dry, fmt, lw=2, linestyle="-", color=col[0])
                    ax.plot_date(t, comfort, fmt, lw=2,  linestyle="-", color=col[1])
                    ax.plot_date(t, damp, fmt, lw=2,  linestyle="-", color=col[2])
                    ax.plot_date(t, risk, fmt, lw=2,  linestyle="-", color=col[3])


                    fig.autofmt_xdate()
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Percentage of time (%)")

                    image = cStringIO.StringIO()
                    fig.savefig(image)

                    req.content_type = "image/png"
                    return  image.getvalue()
                else:
                    req.content_type = "text/plain"
                    return "debug"

    finally:
        session.close()


def humExposure():
    try:
        session=Session()

        s=['<p>']
        is_empty = True
        for (i, h, r) in session.query(Node.id, House.address, Room.name).join(Location, House, Room).order_by(House.address, Room.name):
            is_empty = False

            fr = session.query(Reading).filter(and_(Reading.nodeId==i,
                                                    Reading.typeId==57)).first()

            if fr is not None:
                u = _url("humExpNodeGraph", [('node', i)])
                u2 = _url("humExpGraph", [('node', i)])
                s.append('<p><a href="%s"><div id="grphtitle">%s</div><img src="%s" alt=\"graph for node %d\" width=\"700\" height=\"400\"></a></p>' % (u,h + ": " + r + " (" + str(i) + ")", u2, i))
                
        if is_empty:
            s.append("<p>No nodes have reported yet.</p>")
            
            
        return _page('Time series graphs', ''.join(s))
        
    finally:
        session.close()


def tempExpNodeGraph(node=None):
    try:
        session = Session()

        (n, h, r) = session.query(Node.id, House.address, Room.name).join(Location, House, Room).filter(Node.id==int(node)).one()
        s = ['<p>']
 
        u = _url("tempExpGraph", [('node', node)])
        s.append('<p><div id="grphtitle">%s</div><img src="%s" alt="graph for node %s" width="700" height="400"></p>' % (h + ": " + r + " (" + node + ")", u, node))

        return _page('Time series graph', ''.join(s))
    finally:
        session.close()


def tempExpGraph(req,node='64', debug=None, fmt='bo'):
    col=['#000080', '#3A5FCD', '#006400', '#FFFF00', '#8B0000']
    try:
        session = Session()
        
        debug = (debug is not None)
        
        endts = datetime.utcnow()
        
        t=[]
        bv=[]
        health=[]
        cold=[]
        comfort=[]
        warm=[]
        over=[]
        
        healthqry = session.query(Reading.time,Reading.value).filter(
            and_(Reading.nodeId == int(node),
                 Reading.typeId == 50)).order_by(Reading.time)
            
        lasthealth=None
        for qt, qv in healthqry:
            bv.append(100.0)
            t.append(matplotlib.dates.date2num(qt))
            health.append(qv)
            lasthealth=qv
        health.append(lasthealth)

        coldqry = session.query(Reading.time,Reading.value).filter(
            and_(Reading.nodeId == int(node),
                 Reading.typeId == 51)).order_by(Reading.time)

        for qt, qv in coldqry:
            cold.append(qv)
            lastcold=qv
        cold.append(lastcold)

        comfortqry = session.query(Reading.time,Reading.value).filter(
            and_(Reading.nodeId == int(node),
                 Reading.typeId == 52)).order_by(Reading.time)

        for qt, qv in comfortqry:
            comfort.append(qv)
            lastcomfort=qv
        comfort.append(lastcomfort)

        warmqry = session.query(Reading.time,Reading.value).filter(
            and_(Reading.nodeId == int(node),
                 Reading.typeId == 53)).order_by(Reading.time)

        for qt, qv in warmqry:
            warm.append(qv)
            lastwarm=qv
        warm.append(lastwarm)

        overqry = session.query(Reading.time,Reading.value).filter(
            and_(Reading.nodeId == int(node),
                 Reading.typeId == 54)).order_by(Reading.time)

        for qt, qv in overqry:
            over.append(qv)
            lastover=qv
        over.append(lastover)

        #do additions to give relative locations on the graph
        health=np.array(health)
        cold=np.array(cold)+health
        comfort=np.array(comfort)+cold
        warm=np.array(warm)+comfort
        over=np.array(over)+warm

        req.content_type = "image/png"

        nid=int(node)
        if not debug:
            with _lock:
                fig = plt.figure()
                fig.set_size_inches(7,4)
                ax = fig.add_subplot(111)
                ax.set_autoscaley_on(False)
                ax.set_autoscalex_on(False)
                endts=matplotlib.dates.date2num(datetime.utcnow())
                ax.set_xlim(t[0],endts)
                ax.set_ylim(0,100)


                if len(t) > 0:                            

                    t.append(endts)
                    bv.append(100.0)
                    ax.fill_between(t, 0, over, facecolor=col[4])
                    ax.fill_between(t, 0, warm, facecolor=col[3])
                    ax.fill_between(t, 0, comfort, facecolor=col[2])
                    ax.fill_between(t, 0, cold, facecolor=col[1])
                    ax.fill_between(t, 0, health, facecolor=col[0])

                    ax.plot_date(t, health, fmt, lw=2, linestyle="-", color=col[0])
                    ax.plot_date(t, cold, fmt, lw=2,  linestyle="-", color=col[1])
                    ax.plot_date(t, comfort, fmt, lw=2,  linestyle="-", color=col[2])
                    ax.plot_date(t, warm, fmt, lw=2,  linestyle="-", color=col[3])
                    ax.plot_date(t, over, fmt, lw=2,  linestyle="-",fillstyle="full", color=col[4])

                    #ax.bar(t,bv, color="black", width=0.01)

                    fig.autofmt_xdate()
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Percentage of time (%)")


                    image = cStringIO.StringIO()
                    fig.savefig(image)

                    req.content_type = "image/png"
                    return  image.getvalue()
                else:
                    req.content_type = "text/plain"
                    return "debug"

    finally:
        session.close()



def tempExposure():
    try:
        session=Session()

        s=['<p>']
        is_empty = True
        for (i, h, r) in session.query(Node.id, House.address, Room.name).join(Location, House, Room).order_by(House.address, Room.name):
            is_empty = False

            fr = session.query(Reading).filter(and_(Reading.nodeId==i,
                                                    Reading.typeId==50)).first()

            if fr is not None:
                u = _url("tempExpNodeGraph", [('node', i)])
                u2 = _url("tempExpGraph", [('node', i)])
                s.append('<p><a href="%s"><div id="grphtitle">%s</div><img src="%s" alt=\"graph for node %d\" width=\"700\" height=\"400\"></a></p>' % (u,h + ": " + r + " (" + str(i) + ")", u2, i))
                
        if is_empty:
            s.append("<p>No nodes have reported yet.</p>")
            
            
        return _page('Time series graphs', ''.join(s))
        
    finally:
        session.close()

def allGraphs(typ="0",period="day"):
    try:
        session = Session()

        try:
            mins = _periods[period]
        except:
            mins = 1440

        s = ['<p>']
        for k in sorted(_periods, key=lambda k: _periods[k]):
            if k == period:
                s.append(" %s " % k)
            else:
                u = _url("allGraphs", [('typ', typ),
                                       ('period', k)])
                s.append(' <a href="%s" title="change period to %s">%s</a> ' % (u, k, k))
        s.append("</p>")
        
        is_empty = True
        for (i, h, r) in session.query(Node.id, House.address, Room.name).join(Location, House, Room).order_by(House.address, Room.name):
            is_empty = False

            fr = session.query(Reading).filter(and_(Reading.nodeId==i,
                                                    Reading.typeId==typ)).first()
            if fr is not None:
                u = _url("nodeGraph", [('node', i),
                                       ('typ', typ),
                                       ('period', period)])
                u2 = _url("graph", [('node', i),
                                    ('typ', typ),
                                    ('minsago', mins),
                                    ('duration', mins)])
                s.append('<p><a href="%s"><div id="grphtitle">%s</div><img src="%s" alt=\"graph for node %d\" width=\"700\" height=\"400\"></a></p>' % (u,h + ": " + r + " (" + str(i) + ")", u2, i))

        if is_empty:
            s.append("<p>No nodes have reported yet.</p>")


        return _page('Time series graphs', ''.join(s))
    finally:
        session.close()

def bathElec(period='day'):
    try:
        session = Session()

        try:
            mins = _periods[period]
        except:
            mins = 1440

        s = ['<p>']
        for k in sorted(_periods, key=lambda k: _periods[k]):
            if k == period:
                s.append(" %s " % k)
            else:
                u = _url("bathElec", [('period', k)])
                s.append(' <a href="%s" title="change period to %s">%s</a> ' % (u, k, k))
        s.append("</p>")
        
        is_empty = True
        for (h) in session.query(House):
            is_empty = False

            u = _url("bathElecImg", [('house', h.id),
                                     ('minsago', mins),
                                     ('duration', mins)])
            s.append('<p><div id="grphtitle">%s</div><img src="%s" alt="bath / elec graph for %s" width="700" height="400"></a></p>' % (h.address, u, h.address))

        if is_empty:
            s.append("<p>No nodes have reported yet.</p>")


        return _page('Bathroom v. electricity graphs', ''.join(s))
    finally:
        session.close()

def exportDataForm(err=None):
    errors = { 'notype': 'No sensor type has been specified',
               'nostart': 'No start date specified',
               'startfmt': 'Start date must be of the form dd/mm/yyyy',
               'noend': 'No end date specified',
               'endfmt': 'End date must be of the form dd/mm/yyyy',
               'nodata': 'No data found for this sensor / period',
               }
    try:
        session = Session()
        s = []
        if err is not None:
            s.append("<p>%s</p>" % errors[err])
        s.append("<form action=\"getData\">")

        s.append("<p>Sensor Type: <select name=\"sensorType\">")
        for st in session.query(SensorType):
            s.append("<option value=\"%d\">%s</option>" % (st.id, st.name))
        s.append("</select></p>")

        s.append("<table border=\"0\" width=\"650\" cellpadding=\"5\"><tr><td>")
        s.append("Start Date: <input type=\"text\" name=\"StartDate\" value=\"\" />")
        s.append("<input type=button value=\"select\" onclick=\"displayDatePicker('StartDate');\"></td><td>") 

        s.append("End Date: <input type=\"text\" name=\"EndDate\" value=\""+(datetime.utcnow()).strftime("%d/%m/%Y")+"\" />")
        s.append("<input type=button value=\"select\" onclick=\"displayDatePicker('EndDate');\"><br/></td><tr></table>") 

        s.append("<p><input type=\"submit\" value=\"Get Data\"></p>")

        s.append("</form>")

        return _page('Export data', ''.join(s))
        
    finally:
        session.close()

def getData(req,sensorType=None, StartDate=None, EndDate=None):
	 
    try:
        session = Session()
        time_format = "%d/%m/%Y"	 
 

        #Param validation
        if sensorType==None:
            return _redirect(_url("exportDataForm", [('err', 'notype')]))
        st=int(sensorType)
        if StartDate==None:
            return _redirect(_url("exportDataForm", [('err', 'nostart')]))
        try:
            sd=datetime.fromtimestamp(time.mktime(time.strptime(StartDate, time_format)))
        except:
            return _redirect(_url("exportDataForm", [('err', 'startfmt')]))
        if EndDate==None:
            return _redirect(_url("exportDataForm", [('err', 'noend')]))
        try:
            ed=datetime.fromtimestamp(time.mktime(time.strptime(EndDate, time_format)))  
        except:
            return _redirect(_url("exportDataForm", [('err', 'endfmt')]))

        ed = ed + timedelta(days=1)

        #construct query
        exportData = session.query(Reading.nodeId,Reading.time,Reading.value * Sensor.calibrationSlope + Sensor.calibrationOffset).join(
            Sensor, and_(Sensor.nodeId == Reading.nodeId,
                         Sensor.sensorTypeId == Reading.typeId)).filter(
            and_(Reading.typeId == st,
                 Reading.time >= sd,
                 Reading.time < ed)).order_by(Reading.nodeId,Reading.time).all()
        if len(exportData) == 0:
            return _redirect(_url("exportDataForm", [('err', 'nodata')]))
        req.content_type = "text/csv"
        return "".join(['%d,"%s",%s\n' % (n, t, v) for n, t, v in exportData])
        csvStr=""
        for rn,rt,rv in exportData:
            csvStr+=str(rn)+","+str(rt)+","+str(rv)+"\n"
        return csvStr
    finally:
        session.close()


def nodeGraph(node=None, typ="0", period="day"):
    try:
        session = Session()

        try:
            mins = _periods[period]
        except:
            mins = 1440

        (n, h, r) = session.query(Node.id, House.address, Room.name).join(Location, House, Room).filter(Node.id==int(node)).one()
            
        s = ['<p>']
        for k in sorted(_periods, key=lambda k: _periods[k]):
            if k == period:
                s.append(" %s " % k)
            else:
                u = _url("nodeGraph", [('node', node),
                                       ('typ', typ),
                                       ('period', k)])
                s.append(' <a href="%s" title="change period to %s">%s</a> ' % (u, k, k))
        s.append("</p>")

        u = _url("graph", [('node', node),
                           ('typ', typ),
                           ('minsago', mins),
                           ('duration', mins)])
        s.append('<p><div id="grphtitle">%s</div><img src="%s" alt="graph for node %s" width="700" height="400"></p>' % (h + ": " + r + " (" + node + ")", u, node))

        return _page('Time series graph', ''.join(s))
    finally:
        session.close()




def viewLog(req):
    with open("/var/log/ch/BaseLogger.log") as f:
        req.content_type = "text/plain"
        return f.read()

def missing():
    try:
        t = datetime.utcnow() - timedelta(hours=1)
        session = Session()
        s = ['<p>']

        report_set = set([int(x) for (x,) in session.query(distinct(NodeState.nodeId)).filter(NodeState.time > t).all()])
        all_set = set([int(x) for (x,) in session.query(Node.id).join(Location, House, Room).all()])
        missing_set = all_set - report_set
        extra_set = report_set - all_set

        if len(missing_set) == 0:
            s.append("No nodes missing")
        else:
            s.append("</table><p><p><h3>Registered nodes not reporting in last hour</h3><p>")

            s.append("<table border=\"1\">")
            s.append("<tr><th>Node</th><th>House</th><th>Room</th><th>Last Heard</th><th></th></tr>"  )

            for (ns, maxtime, nodeId, house, room) in session.query(NodeState,func.max(NodeState.time), NodeState.nodeId, House.address, Room.name).filter(NodeState.nodeId.in_(missing_set)).group_by(NodeState.nodeId).join(Node,Location,House,Room).order_by(House.address, Room.name).all():
                u = _url("unregisterNode", [('node', nodeId)])
                s.append('<tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td><a href="%s">(unregister)</a></tr>' % (nodeId, house, room, str(maxtime), u))
                  

            s.append("</table>")

        if len(extra_set) == 0:
            s.append('</p><p>No extra nodes detected.</p><p>')
        else:
            s.append("</p><h3>Extra nodes that weren't expected</h3><p>")
            for i in sorted(extra_set):
                u = _url("registerNode", [('node', i)])
                s.append('%d <a href="%s">(register)</a><br/>' % (i, u))

        # s.append("<h3>Unregistered nodes</h3><p>")
        # for n in session.query(Node).filter(or_(Node.houseId == None,Node.roomId==None)).order_by(Node.id).all():
        #     s.append("%d <a href=\"registerNode?node=%d\">(register)</a><br/>" % (n.id, n.id))
            

        return _page('Missing nodes', ''.join(s))
    finally:
        session.close()
        

def lastreport():
    try:
        session = Session()

        s = []

        s.append("<table border=\"0\">")
        s.append("<tr><th>Node</th><th>Last heard from</th>")

        for nid,maxtime in session.query(NodeState.nodeId,func.max(NodeState.time)).group_by(NodeState.nodeId).all():
        
            s.append("<tr><td>%d</td><td>%s</td></tr>" % (nid, maxtime))

        s.append("</table>")

        return _page('Last report', ''.join(s))
    finally:
        session.close()
        
def yield24():
    try:
        session = Session()
        s = []

        s.append("<table border=\"1\">")
        s.append("<tr>")
        headings = ["Node", "House", "Room", "Message count", "Min seq", "Max seq", "Yield"]
        s.extend(["<th>%s</th>" % x for x in headings])
        s.append("</tr>")

        start_t = datetime.utcnow() - timedelta(days=1)

        # next get the count per node
        seqcnt_q = (session.query(NodeState.nodeId.label('nodeId'),
                              func.count(NodeState.seq_num).label('cnt'))
                    .filter(NodeState.time >= start_t)
                    .group_by(NodeState.nodeId)
                    .subquery(name='seqcnt'))

        # next get the first occurring sequence number per node
        selmint_q = (session.query(NodeState.nodeId.label('nodeId'),
                               func.min(NodeState.time).label('mint'))
                        .filter(NodeState.time >=start_t)
                        .group_by(NodeState.nodeId)
                        .subquery(name='selmint'))

        minseq_q = (session.query(NodeState.nodeId.label('nodeId'),
                             NodeState.seq_num.label('seq_num'))
                        .join(selmint_q,
                              and_(NodeState.time == selmint_q.c.mint,
                                   NodeState.nodeId == selmint_q.c.nodeId))
                        .subquery(name='minseq'))

        # next get the last occurring sequence number per node
        selmaxt_q = (session.query(NodeState.nodeId.label('nodeId'),
                               func.max(NodeState.time).label('maxt'))
                        .filter(NodeState.time >=start_t)
                        .group_by(NodeState.nodeId)
                        .subquery(name='selmaxt'))

        maxseq_q = (session.query(NodeState.nodeId.label('nodeId'),
                              NodeState.seq_num.label('seq_num'),
                              NodeState.time.label('time'))
                        .join(selmaxt_q,
                              and_(NodeState.time == selmaxt_q.c.maxt,
                                   NodeState.nodeId == selmaxt_q.c.nodeId))
                        .subquery(name='maxseq'))

        yield_q = (session.query(maxseq_q.c.nodeId,
                             maxseq_q.c.seq_num,
                             minseq_q.c.seq_num,
                             seqcnt_q.c.cnt,
                             maxseq_q.c.time,
                             House.address,
                             Room.name)
                        .select_from(maxseq_q)
                        .join(minseq_q, minseq_q.c.nodeId == maxseq_q.c.nodeId)
                        .join(seqcnt_q, maxseq_q.c.nodeId == seqcnt_q.c.nodeId)
                        .join(Node, Node.id == maxseq_q.c.nodeId)
                        .join(Location, House, Room)
                        .order_by(House.address, Room.name))


        # nodestateq = session.query(
        #     NodeState,
        #     func.count(NodeState),
        #     func.max(NodeState.time),
        #     House.address,
        #     Room.name
        #     ).filter(NodeState.time > t
        #              ).group_by(NodeState.nodeId
        #                         ).join(Node,Location,House,Room).order_by(House.address, Room.name).all()

        for (node_id, maxseq, minseq, seqcnt, last_heard,
             house_name, room_name) in yield_q.all():

            missed = (maxseq - minseq + 257) % 256 - seqcnt
            y = (seqcnt * 100.) / ((maxseq - minseq + 257) % 256)

            values = [node_id, house_name, room_name, seqcnt, minseq, maxseq, y]
            fmt = ['%d', '%s', '%s', '%d', '%d', '%d', '%8.2f']
            s.append("<tr>")
            s.extend([("<td>" + f + "</td>") % v for (f,v) in zip(fmt, values)])
            s.append("</tr>")


        s.append("</table>")
        return _page('Yield for last day', ''.join(s))
    finally:
        session.close()

def dataYield():
    try:
        session = Session()
        s = []
        s.append("<h4>Note: this page does not yet support SIP and the yield may be wrong.</h4>")
        s.append("<table border=\"1\">")
        s.append("<tr><th>Node</th><th>House</th><th>Room</th><th>Message Count</th><th>First heard</th><th>Last heard</th><th>Yield</th></tr>")

        # TODO finish this code
        # clock_over_count = {}
        # seq_q = (session.query(NodeState.nodeId,
        #               NodeState.seq_num)
        #     .group_by(NodeState.nodeId)
        #     .order_by(NodeState.time)
        #     .all())

        # last_node = None
        # last_seq = None
        # for node_id, seq_num in seq_q:
        #     if not node_id in clock_over_count:
        #         clock_over_count[node_id] = 0

        #     if (last_seq is not None and
        #         seq_num < last_seq and
        #         last_node is not None and
        #         node_id == last_node):
        #         clock_over_count[node_id] += 1
                
        #     last_seq = seq_num
        #     last_node = node_id


        for nid, cnt, mintime, maxtime in session.query(
            
            NodeState.nodeId,
            func.count(NodeState),
            func.min(NodeState.time),
            func.max(NodeState.time)).group_by(NodeState.nodeId).all():

            try:
                n = session.query(Node).filter(Node.id == nid).one()
                try:
                    house = n.location.house.address
                except:
                    house = '-'
                try:
                    room = n.location.room.name
                except:
                    room = '-'
            except:
                house = '?'
                room = '?'
                
            td = maxtime - mintime
            yield_secs = (td.seconds + td.days * 24 * 3600) # ignore microsecs

            y = -1
            if yield_secs > 0:
                y = (cnt - 1) / (yield_secs / 300.0) * 100.0
                
            s.append("<tr><td>%d</td><td>%s</td><td>%s</td><td>%d</td><td>%s</td><td>%s</td><td>%8.2f</td></tr>" % (nid, house, room, cnt, mintime, maxtime, y))

        s.append("</table>")
        return _page('Yield since first heard', ''.join(s))
    finally:
        session.close()
    
        
def registerNode(node=None):
    try:
        if node is None:
            raise Exception("must specify node id")
        node = int(node)
        session = Session()
        n = session.query(Node).filter(Node.id==node).one()
        if n is None:
            raise Exception("unknown node id %d" % node)
        
        s = []

        s.append("<form action=\"registerNodeSubmit\">")
        s.append("<p>Node id: %d<input type=\"hidden\" name=\"node\" value=\"%d\"/></p>" % (node, node))
        s.append("<p>House: <select name=\"house\">")        
        for h in session.query(House):
            s.append("<option value=\"%d\">%s</option>" % (h.id, h.address))
        s.append("</select>")
        u = _url("addNewHouse", [('regnode', node)])
        s.append(' <a href="%s">(add new house)</a></p>' % u)
        s.append("<p>Room: <select name=\"room\">")
        for r in session.query(Room):
            s.append("<option value=\"%d\">%s</option>" % (r.id, r.name))
        s.append("</select>")
        u = _url("addNewRoom", [('regnode', node)])
        s.append(' <a href="%s">(add new room)</a></p>' % u)
        s.append("<p><input type=\"submit\" value=\"Register\"></p>")
        
        s.append("</form>")

        return _page('Register node', ''.join(s))
        
    finally:
        session.close()

def unregisterNode(node=None):
    try:
        if node is None:
            raise Exception("must specify node id")
        node = int(node)
        session = Session()
        n = session.query(Node).filter(Node.id==node).one()
        if n is None:
            raise Exception("unknown node id %d" % node)
        n = session.query(Node).filter(Node.id == int(node)).one()

        n.locationId = None
        session.commit()
        return _redirect("missing")
    
    except:
        session.rollback()
        
    finally:
        session.close()



def registerNodeSubmit(node=None, house=None, room=None):
    try:
        session = Session()

        if node is None:
            raise Exception("no node specified")
        if room is None:
            raise Exception("no room specified")
        if house is None:
            raise Exception("no house specified")

        n = session.query(Node).filter(Node.id==int(node)).one()

        ll = session.query(Location).filter(
            and_(Location.houseId == int(house),
                 Location.roomId == int(room))).first()

        if ll is None:
            ll = Location(houseId=int(house), roomId=int(room))
            session.add(ll)
            
        n.location = ll
        session.commit()
        return _redirect("missing")
    
    except:
        session.rollback()
    finally:
        session.close()

def unregisterNodeSubmit(node=None):
    try:
        session = Session()

        if node is None:
            raise Exception("no node specified")

        n = session.query(Node).filter(Node.id == int(node)).one()

        n.locationId = None
        session.commit()
        return _redirect("missing")
    
    except:
        session.rollback()
    finally:
        session.close()

#------------------------------------------------------------
# House

def addNewHouse(regnode=None, err=None, address=None):
    assert regnode is not None
    errors = { 'duphouse': 'This house address already exists'}
    if address is None:
        address = ''
    try:
        session = Session()
        
        s = []
        if err is not None:
            s.append('<p>%s</p>' % (errors[err]))
        s.append("<form action=\"addNewHouseSubmit\">")
        s.append('<input type="hidden" name="regnode" value="%s" />' % (regnode))

        s.append('<p>Address: <input type="text" name="address" value="%s"/></p>' % address)
        

        # s.append('<p>Deployment: <select name="deployment">')
        # for d in session.query(Deployment):
        #     s.append('<option value="%d">%s</option>' % (d.id, d.name))
        # s.append('</select>')
        
        s.append("<p><input type=\"submit\" value=\"Add\"></p>")
        
        s.append("</form>")

        return _page('Add new house', ''.join(s))
    finally:
        session.close()

def addNewHouseSubmit(regnode=None, address=None, deployment=None ):
    try:
        session = Session()

        if address is None:
            raise Exception("no address specified")
        if regnode is None:
            raise Exception("no regnode specified")

        address = address.strip().lower()

        h = session.query(House).filter(House.address==address).first()
        if h is not None:
            return _redirect(_url("addNewHouse", [('regnode', regnode),
                                                  ('address', address),
                                                  ('err', 'duphouse')]))

        h = House(address=address, deploymentId=deployment)
        session.add(h)
        session.commit()
        u = _url("registerNode", [('node', regnode),
                                  ('house', h.id)])
        return _redirect(u)
    except Exception, e:
        session.rollback()
        return _page('Add new house error', '<p>%s</p>' % str(e))
    finally:
        session.close()

#------------------------------------------------------------
# Room
        
def addNewRoom(regnode=None, err=None, name=None):
    assert regnode is not None
    errors = { 'duproom': 'This room name already exists',
               'nullroomtype': 'Please select a room type'}
    if name is None:
        name = ''
    try:
        session = Session()
        
        s = []
        if err is not None:
            s.append('<p>%s</p>' % (errors[err]))
        s.append("<form action=\"addNewRoomSubmit\">")
        s.append('<input type="hidden" name="regnode" value="%s" />' % (regnode))

        s.append('<p>Name: <input type="text" name="name" value="%s" /></p>' % (name))
        

        s.append('<p>Type: <select name="roomtype">')
        for d in session.query(RoomType):
            s.append('<option value="%d">%s</option>' % (d.id, d.name))
        s.append('</select>')
        u = _url("addNewRoomType", [('ref', _url("addNewRoom", [('regnode', regnode),
                                                                ('name', name)]))])
        s.append(' <a href="%s">(add new room type)</a></p>' % u)

        s.append("<p><input type=\"submit\" value=\"Add\"></p>")
        
        s.append("</form>")

        return _page('Add new room', ''.join(s))
    finally:
        session.close()

def addNewRoomSubmit(regnode=None, name=None, roomtype=None ):
    try:
        session = Session()

        if roomtype is None:
            return _redirect(_url("addNewRoom", [('regnode', regnode),
                                                  ('name', name),
                                                  ('err', 'nullroomtype')]))
        

        if name is None:
            raise Exception("no name specified")
        if regnode is None:
            raise Exception("no regnode specified")

        name = name.strip().lower()

        h = session.query(Room).filter(Room.name==name).first()
        if h is not None:
            return _redirect(_url("addNewRoom", [('regnode', regnode),
                                                  ('name', name),
                                                  ('err', 'duproom')]))

        h = Room(name=name, roomTypeId=int(roomtype))
        session.add(h)
        session.commit()
        u = _url("registerNode", [('node', regnode),
                                  ('room', h.id)])
        return _redirect(u)
    except Exception, e:
        session.rollback()
        return _page('Add new room error', '<p>%s</p>' % str(e))
    finally:
        session.close()
        
#------------------------------------------------------------
# RoomType

def addNewRoomType(ref=None, err=None, name=None):
    assert ref is not None
    errors = { 'dup': 'This room type already exists',
               'short': 'The room type name is too short'}
    if name is None:
        name = ''
    try:
        session = Session()
        
        s = []
        if err is not None:
            s.append('<p>%s</p>' % (errors[err]))
        s.append("<form action=\"addNewRoomTypeSubmit\">")
        s.append('<input type="hidden" name="ref" value="%s" />' % (ref))

        s.append('<p>Room type: <input type="text" name="name" value="%s" /></p>' % (name))

        s.append("<p><input type=\"submit\" value=\"Add\">")
        s.append('    <a href="%s">Cancel</a></p>' % (ref))
        
        s.append("</form>")

        return _page('Add new room type', ''.join(s))
    finally:
        session.close()

def addNewRoomTypeSubmit(ref=None, name=None):
    try:
        session = Session()

        if name is None:
            raise Exception("no name specified")
        if ref is None:
            raise Exception("no ref specified")

        name = name.strip().lower()
        if len(name) > 20:
            name = name[:20]
        if len(name) < 3:
            return _redirect(_url("addNewRoomType", [('ref', ref),
                                                     ('name', name),
                                                     ('err', 'short')]))

        h = session.query(RoomType).filter(RoomType.name==name).first()
        if h is not None:
            return _redirect(_url("addNewRoomType", [('ref', ref),
                                                     ('name', name),
                                                     ('err', 'dup')]))

        h = RoomType(name=name)
        session.add(h)
        session.commit()
        return _redirect(ref)
    except Exception, e:
        session.rollback()
        return _page('Add new room type error', '<p>%s</p>' % str(e))
    finally:
        session.close()

#------------------------------------------------------------

def lowbat(bat="2.6"):
    try:
        try:
            batlvl = float(bat)
        except:
            batlvl = 2.6
        t = datetime.utcnow() - timedelta(hours=1)
        session = Session()
        s = []
        empty = True
        for r in session.query(distinct(Reading.nodeId)).filter(and_(Reading.typeId==6,
                                                     Reading.value<=batlvl,
                                                     Reading.time > t)).order_by(Reading.nodeId):
            r = r[0]
            u = _url("graph", [('node', r),
                               ('typ', 6),
                               ('minsago', 60),
                               ('duration', 60)])
                               
            s.append('<p><a href="%s">%d</a></p>' % (u, r))
            empty = False

        if empty:
            s.append("<p>No low batteries found</p>")

        return _page('Low batteries', ''.join(s))
    finally:
        session.close()
            

def _calibrate(session,v,node,typ):
    # calibrate
    try:
        (mult, offs) = session.query(Sensor.calibrationSlope, Sensor.calibrationOffset).filter(
            and_(Sensor.sensorTypeId==typ,
                 Sensor.nodeId==node)).one()
        return [x * mult + offs for x in v]
    except NoResultFound, e:
        return v



_deltaDict={0: 1, 2: 3, 6: 7, 8: 17} 

def _plot(typ, t, v, startts, endts, debug, fmt, req):
    if not debug:
        with _lock:
            fig = plt.figure()
            fig.set_size_inches(7,4)
            ax = fig.add_subplot(111)
            ax.set_autoscalex_on(False)
            ax.set_xlim((matplotlib.dates.date2num(startts),
                         matplotlib.dates.date2num(endts)))
                
            if len(t) > 0:                            
                ax.plot_date(t, v, fmt)
                fig.autofmt_xdate()
                ax.set_xlabel("Date")
                try:
                    session = Session()
                    thistype = session.query(SensorType.name, SensorType.units).filter(SensorType.id==int(typ)).one()
                    ax.set_ylabel("%s (%s)" % tuple(thistype))
                    session.close()
                except NoResultFound:
                    pass


            image = cStringIO.StringIO()
            fig.savefig(image)

            req.content_type = "image/png"
            return  [req.content_type, image.getvalue()]
    else:
        req.content_type = "text/plain"
        return [req.content_type , str(t)+ str(v)]

def test(req,nid,typ,minsago):
    try:
        session = Session()

        try:
            minsago_i = timedelta(minutes=int(minsago))
        except Exception:
            minsago_i = timedelta(minutes=1)

        startts = datetime.utcnow() - minsago_i
        
        (max_time_before,) = session.query(func.max(Reading.time)).filter(
            and_(Reading.nodeId == int(nid),
                 Reading.typeId == int(typ),
                 Reading.time < startts)).first()

        (v2,) = session.query(Reading.value).filter(
            and_(Reading.nodeId == int(nid),
                 Reading.typeId == int(typ),
                 Reading.time == max_time_before)).first()


        sq = session.query(func.max(Reading.time).label('maxtime')).filter(
            and_(Reading.nodeId == int(nid),
                 Reading.typeId == int(typ),
                 Reading.time < startts)).subquery()
        
        (mt2, v3,) = session.query(Reading.time,Reading.value).join(
            sq, Reading.time==sq.c.maxtime).filter(
            and_(Reading.nodeId == int(nid),
                 Reading.typeId == int(typ))).first()

        sql = session.query(Reading.time,Reading.value).join(
            sq, Reading.time==sq.c.maxtime).filter(
            and_(Reading.nodeId == int(nid),
                 Reading.typeId == int(typ))).as_scalar()

        req.content_type='text/plain'
        return repr(max_time_before) + " " + repr(v2) + " " + repr(v3) + " " + repr(mt2) + str(sql)
        
        
    finally:
        session.close()

def _latest_reading_before(session, nid, typ, startts):
        # get latest reading / time that is before start time
        try:
            sq = session.query(func.max(Reading.time).label('maxtime')).filter(
                and_(Reading.nodeId == nid,
                     Reading.typeId == typ,
                     Reading.time < startts)).subquery()
        
            (qt, qv) = session.query(Reading.time,Reading.value).join(
                sq, Reading.time==sq.c.maxtime).filter(and_(Reading.nodeId == nid,Reading.typeId == typ)).first()

            # get corresponding delta
            (dt, dv) = session.query(Reading.time,Reading.value).join(
                sq, Reading.time==sq.c.maxtime).filter(and_(Reading.nodeId == nid,Reading.typeId == _deltaDict[typ])).first()
            return qt,qv,dv
        except:
            return None,None,None
    

thresholds = {
    0 : 0.25,
    2 : 1,
    8 : 100,
    6 : 0.1
    }

sensor_types= {
    0 : 0,
    2 : 2,
    8 : 8,
    6 : 6
    }

type_delta={
    0 : 1,
    2 : 3,
    8 : 20,
    6 : 7
}

def _interp(data):
    ft = data["time"]
    fv = data["value"]
    fd = data["delta"]

    ctd = datetime.now()
    duration = (ctd - ft).seconds

    ft = matplotlib.dates.date2num(ft)
    ct = matplotlib.dates.date2num(ctd)
    cv = fv + (duration * fd)
    
    point={}
    point["time"]=ctd
    point["value"]=cv
    point["delta"]=fd


    return ct,cv,point


def _calcSpline(first,last,typ):

    thresh = thresholds[int(typ)]

    samplePeriod = timedelta(seconds = 300)
    halfPeriod = timedelta(seconds = 150)

    codes = [Path.MOVETO,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             ]

    ft = first["time"]
    fv = first["value"]
    fd = first["delta"]

    lt = last["time"]
    lv = last["value"]
    ld = last["delta"]

    #get control point 1 time and point B
    cp1t = lt - samplePeriod
    Bv = fv + (fd * (cp1t - ft).seconds)

    #limits
    ul = Bv + thresh
    ll = Bv - thresh

    #get second control point (D)            
    cp2t = lt  - halfPeriod # 1/2 sample back
    c2v = lv - (ld * halfPeriod.seconds)

    #get xc
    xct = cp1t
    xcv =  lv - (ld * samplePeriod.seconds)

    #decide on c1v (B') actual value
    if xcv < ll:
        c1v = ll
    elif xcv > ul:
        c1v = ul
    else:
        c1v=(xcv+Bv)/2.
        #c1v=Bv

    ft = matplotlib.dates.date2num(ft)
    cp1t = matplotlib.dates.date2num(cp1t)
    cp2t = matplotlib.dates.date2num(cp2t)
    lt = matplotlib.dates.date2num(lt)

    verts = [
        (ft, fv),  # P0
        (cp1t, c1v), # P1
        (cp2t, c2v), # P2
        (lt, lv), # P3
        ]

    path = Path(verts, codes)
    return path

def getSplineData(session, node_id, reading_type, delta_type, sd, ed):
    #get values    
    data=[]
    times=[]
    xs=[]
    
    #get prev reading
    (prev_time, prev_value, prev_delta) = _latest_reading_before(session, node_id, reading_type, sd)
    if prev_time != None:
        point={}
        point["time"]=prev_time
        times.append(prev_time)
        point["value"]=prev_value
        xs.append(prev_value)
        point["delta"]=prev_delta/300.
        data.append(point)
        

    delta_rows = session.query(Reading.time, Reading.value).filter(and_(
            Reading.time >= sd,
            Reading.time < ed,
            Reading.nodeId == node_id,
            Reading.typeId == delta_type)).with_labels().subquery()
            
    rows =  session.query(Reading.time, Reading.value, delta_rows.c.Reading_value).filter(and_(
        Reading.time >= sd,
        Reading.time < ed,
        Reading.nodeId == node_id,
        Reading.typeId == reading_type))
                        
    readings = rows.join((delta_rows, Reading.time == delta_rows.c.Reading_time))

    for time,value,delta in readings:  
        point={}
        point["time"]=time
        times.append(time)
        point["value"]=value
        xs.append(value)
        point["delta"]=delta/300.
        data.append(point)

    points=[times,xs]
    return (data,points)

def _graphSplines(session, data, paths, current_point, start_time, end_time, reading_type, fmt, req):
    fig = plt.figure()
    fig.set_size_inches(7,4)
    ax = fig.add_subplot(111)
    ax.set_autoscalex_on(False)
    ax.set_xlim((matplotlib.dates.date2num(start_time),
                 matplotlib.dates.date2num(end_time)))

    for p in paths:
        patch = patches.PathPatch(p, facecolor='none', lw=2)
        ax.add_patch(patch)

    ax.plot_date(current_point[0], current_point[1], color='red', linestyle='dashed')   
    ax.plot_date(data[0], data[1],fmt)


    fig.autofmt_xdate()
    ax.set_xlabel("Date")
        

    try:
        thistype = session.query(SensorType.name, SensorType.units).filter(SensorType.id==int(reading_type)).one()
        ax.set_ylabel("%s (%s)" % tuple(thistype))
    except NoResultFound:
        pass        

    image = cStringIO.StringIO()
    fig.savefig(image)
    
    req.content_type = "image/png"
    return  [req.content_type, image.getvalue()]

def _plotSplines(node_id, reading_type, delta_type, start_time, end_time, debug, fmt, req):
    try:
        session = Session()
        data,points = getSplineData(session, node_id, reading_type, delta_type, start_time, end_time)

        paths = []
        msgs=len(data)
        i=0
        req.content_type = "text/plain"
        while i < msgs:
            try:
                path = _calcSpline(data[i],data[i+1],reading_type)
                paths.append(path)
            except IndexError:
                current_point = _interp(data[i])
                path = _calcSpline(data[i],current_point[2],reading_type)
                paths.append(path)
                break
            i+=1
        if len(paths)>0:
            return _graphSplines(session, points, paths, current_point, start_time, end_time, reading_type, fmt, req)
    finally:
        session.close()
            
def _isPlotSpline(session, node, typ, startts, endts):
    if typ in _deltaDict:
        dqry = session.query(Reading.time, Reading.value).filter(
            and_(Reading.nodeId == node,
                 Reading.typeId == _deltaDict[typ],
                 Reading.time >= startts,
                Reading.time <= endts)).first()
        return dqry is not None
    return False


def graph(req,node='64', minsago='1440',duration='1440', debug=None, fmt='bo', typ='0'):

    try:
        session = Session()
        plotLines=False

        try:
            minsago_i = timedelta(minutes=int(minsago))
        except Exception:
            minsago_i = timedelta(minutes=1)

        try:
            duration_i = timedelta(minutes=int(duration))
        except Exception:
            duration_i = timedelta(minutes=1)

        debug = (debug is not None)
        week = timedelta(minutes=int(_periods["week"]))
        startts = datetime.utcnow() - minsago_i
        deltats = (datetime.utcnow() - minsago_i) - week

        endts = startts + duration_i

        qry = session.query(Reading.time,Reading.value).filter(
            and_(Reading.nodeId == int(node),
                 Reading.typeId == int(typ),
                 Reading.time >= startts,
                 Reading.time <= endts)).order_by(Reading.time)


        t = []
        dt = []
        v = []
        last_value=None
        for qt, qv in qry:
            dt.append(qt)
            t.append(matplotlib.dates.date2num(qt))
            v.append(qv)
            last_value=float(qv)

        v = _calibrate(session, v, node, typ)


        req.content_type = "image/png"

        #will need a flag in the db saying if an SI node so can force a splinePlot if t == 0
        nid=int(node)
        if len(t) == 0:  
            res=_plot(typ, t, v, startts, endts, debug, fmt, req)
            return res[1]
        elif _isPlotSpline(session, int(node), int(typ), startts, endts):
            res = _plotSplines(nid, typ, type_delta[int(typ)], startts, endts, debug, fmt, req)
        else:
            res=_plot(typ, t, v, startts, endts, debug, fmt, req)

        req.content_type=res[0]
        return res[1]
    finally:
        session.close()



def bathElecImg(req,house='', minsago='1440',duration='1440', debug=None):

    try:
        session = Session()


        try:
            minsago_i = timedelta(minutes=int(minsago))
        except Exception:
            minsago_i = timedelta(minutes=1)

        try:
            duration_i = timedelta(minutes=int(duration))
        except Exception:
            duration_i = timedelta(minutes=1)

        debug = (debug is not None)

        startts = datetime.utcnow() - minsago_i
        endts = startts + duration_i

        # find all the electricity readings for House n for the required period

        nodesInHouse = session.query(Node.id).join(Location, House).filter(House.id==int(house)).all()
        nodesInHouse = [a for (a,) in nodesInHouse]


        (elec_node) = session.query(Reading.nodeId).filter(
            and_(Reading.nodeId.in_(nodesInHouse),
                 Reading.typeId == 11,
                 Reading.time >= startts,
                 Reading.time <= endts)).first()

        t = []
        v = []
        if elec_node is not None:
            qry = session.query(Reading.time,Reading.value).filter(
                and_(Reading.nodeId == elec_node,
                     Reading.typeId == 11,
                     Reading.time >= startts,
                     Reading.time <= endts))

        
            for qt, qv in qry:
                t.append(matplotlib.dates.date2num(qt))
                v.append(qv)

            v = _calibrate(session, v, elec_node, 11)

        (bathroomNode) = session.query(Node.id).join(Location, House, Room).filter(and_(House.id==int(house), Room.name=="Bathroom")).first()

        t2 = []
        v2 = []
        if bathroomNode is not None:
            qry2 = session.query(Reading.time, Reading.value).filter(
                and_(Reading.nodeId == bathroomNode,
                     Reading.typeId == 2,
                     Reading.time >= startts,
                     Reading.time <= endts))

            for qt, qv in qry2:
                t2.append(matplotlib.dates.date2num(qt))
                v2.append(qv)

            v2 = _calibrate(session, v2, bathroomNode, 2)


        #t,v = zip(*(tuple (row) for row in cur))
        #    ax.plot(t,v,fmt)

        if not debug:
            with _lock:
                fig = plt.figure()
                fig.set_size_inches(7,4)
                ax = fig.add_subplot(111)
                ax.set_autoscalex_on(False)
                ax.set_xlim((matplotlib.dates.date2num(startts),
                         matplotlib.dates.date2num(endts)))
                
                if len(t) > 0:
                    ax.plot_date(t, v, 'r-')

                fig.autofmt_xdate()
                ax.set_xlabel("Date")
                try:
                    thistype = session.query(SensorType.name, SensorType.units).filter(SensorType.id==int(11)).one()
                    ax.set_ylabel("%s (%s)" % tuple(thistype))
                except:
                    pass

                if len(t2) > 0:
                    ax2 = ax.twinx()
                    ax2.plot_date(t2, v2, 'b-')
                    ax2.set_ylabel('Bathroom humidity')


                image = cStringIO.StringIO()
                fig.savefig(image)

            req.content_type = "image/png"

            return image.getvalue()
        else:
            req.content_type = "text/plain"
            return str(t)
    finally:
        session.close()


