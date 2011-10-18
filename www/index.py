#
# mod_python web server for simple display of cogenthouse node status
#
# author: J. Brusey, May 2011
#
from __future__ import with_statement
import cStringIO
import time
from datetime import datetime, timedelta
# set the home to a writable directory
import os
os.environ['HOME']='/tmp'
from threading import Lock
_lock = Lock()

# do this before importing pylab or pyplot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from cogent.base.model import *
from sqlalchemy import create_engine, and_, or_, distinct, func
from sqlalchemy.orm import sessionmaker


_DBURL = "mysql://chuser@localhost/ch?connect_timeout=1"

engine = create_engine(_DBURL, echo=False, pool_recycle=60)
#engine.execute("pragma foreign_keys=on")
Session = sessionmaker(bind=engine)



_periods = {
    "hour" : 60,
    "day" : 1440,
    "week" : 1440*7,
    "month" : 1440 * 7 * 52 / 12}

_navs = [
    ("Home", "index.py")
    ]

_sidebars = [
    ("Temperature", "allGraphs?typ=0"),
    ("Humidity", "allGraphs?typ=2"),
    ("CO2", "allGraphs?typ=8"),
    ("AQ", "allGraphs?typ=9"),
    ("VOC", "allGraphs?typ=10"),
    ("Electricity", "allGraphs?typ=11"),
    ("Battery", "allGraphs?typ=6"),
    ("Duty cycle", "allGraphs?typ=13"),

    ("Network tree", "treePage"),
    ("Missing and extra nodes", "missing"),
    ("Packet yield", "yield24"),
    ("Low batteries", "lowbat"),
    ("View log", "viewLog"),
    ("Export data", "exportDataForm"),

     ]

def _main(html):
    return '<div id="main">' + html + '</div>';

def _wrap(html):
    return '<div id="wrap">' + html + '</div>';

def _nav():
    return ('<div id="nav">' +
            '<ul>' + 
            ''.join(['<li><a href="%s">%s</a></li>' % (b,a) for (a,b) in _navs]) +
            '</ul>' +
            '</div>')

def _sidebar():
    return ('<div id="sidebar">' +
            '<ul>' + 
            ''.join(['<li><a href="%s">%s</a></li>' % (b,a) for (a,b) in _sidebars]) +
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
            '<script type="text/javascript" src="../scripts/datePicker.js"></script>' +
            '<body>')

def _foot():
    return '</body></html>'
            
def _header(title):
    return ('<div id="header"><h1>%s</h1></div>' % (title))

def _footer():
    return '<div id="footer">CogentHouse &copy; <a href="http://cogentcomputing.org">Cogent Computing Applied Research Centre</a></div>'

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

        t = datetime.now() - timedelta(minutes=mins)

        p = Popen("dot -Tsvg", shell=True, bufsize=4096,
#        p = Popen("cat", shell=True, bufsize=4096,
              stdin=PIPE, stdout=PIPE, close_fds=True)
        (child_stdin, child_stdout) = (p.stdin, p.stdout)
        
        with p.stdin as dotfile:
            dotfile.write("digraph {");
            for (ni,pa) in session.query(NodeState.nodeId,
                                            NodeState.parent
                                            ).group_by(NodeState.nodeId, NodeState.parent).filter(NodeState.time>t):
                
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
            s.append(" <a href=\"treePage?period=%s\">%s</a> " % (k, k))

    s.append('<p>')
    s.append('<img src="tree?period=%s" alt="network tree diagram"></a></p>' % (period))

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
    s.append('<p><a href="lastreport">Last Report</a></p>')
    s.append('<p><a href="dataYield">Yield since first heard</a></p>')
    return _page('Home page', ''.join(s))



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
                s.append(" <a href=\"allGraphs?typ=%s&period=%s\">%s</a> " % (typ, k, k))
        s.append("</p>")
        
        is_empty = True
        for (i, h, r) in session.query(Node.id, House.address, Room.name).join(House, Room).order_by(House.address, Room.name):
            is_empty = False

            fr = session.query(Reading).filter(and_(Reading.nodeId==i,
                                                    Reading.typeId==typ)).first()
            if fr is not None:
                s.append('<p><a href=\"nodeGraph?node=%d&typ=%s&period=%s\"><div id="grphtitle">%s</div><img src=\"graph?node=%d&typ=%s&minsago=%d&duration=%d\" alt=\"graph for node %d\" width=\"700\" height=\"400\"></a></p>' % (i,typ,period,h + ": " + r + " (" + str(i) + ")", i,typ,mins,mins,i))

        if is_empty:
            s.append("<p>No nodes have reported yet.</p>")


        return _page('Time series graphs', ''.join(s))
    finally:
        session.close()

def exportDataForm():
    try:
        session = Session()
        s = []
        s.append("<form action=\"getData\">")

        s.append("<p>Sensor Type: <select name=\"sensorType\">")
        for st in session.query(SensorType):
            s.append("<option value=\"%d\">%s</option>" % (st.id, st.name))
        s.append("</select></p>")

        s.append("<table border=\"0\" width=\"650\" cellpadding=\"5\"><tr><td>")
        s.append("Start Date: <input type=\"text\" name=\"StartDate\" value=\"\" />")
        s.append("<input type=button value=\"select\" onclick=\"displayDatePicker('StartDate');\"></td><td>") 

        s.append("End Date: <input type=\"text\" name=\"EndDate\" value=\""+(datetime.now()).strftime("%d/%m/%Y")+"\" />")
        s.append("<input type=button value=\"select\" onclick=\"displayDatePicker('EndDate');\"><br/></td><tr></table>") 

        s.append("<p><input type=\"submit\" value=\"Get Data\"></p>")

        s.append("</form>")

        return _page('Export data', ''.join(s))
        
    finally:
        session.close()

def getData(req,sensorType=None, StartDate=None, EndDate=None):
	 
    req.content_type = "text/csv"
    try:
        session = Session()
        time_format = "%d/%m/%Y"	 
 

        #Param validation
        if sensorType==None:
            raise Exception("No sensor type specified")
        st=int(sensorType)
        if StartDate==None:
            raise Exception("No Start Date specified")
        try:
            sd=datetime.fromtimestamp(time.mktime(time.strptime(StartDate, time_format)))
        except:
            raise Exception("Start date is not in correct format")
        if EndDate==None:
            raise Exception("No End Date specified")
        try:
            ed=datetime.fromtimestamp(time.mktime(time.strptime(EndDate, time_format)))  
        except:
            raise Exception("End date is not in correct format")


        #construct query
        exportData = session.query(Reading.nodeId,Reading.time,Reading.value).filter(and_(Reading.typeId==st,
                                                                                         Reading.time>sd,
                                                                                         Reading.time<ed)).order_by(Reading.nodeId,Reading.time);
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
            
        s = ['<p>']
        for k in sorted(_periods, key=lambda k: _periods[k]):
            if k == period:
                s.append(" %s " % k)
            else:
                s.append(" <a href=\"nodeGraph?node=%s&typ=%s&period=%s\">%s</a> " % (node, typ, k, k))
        s.append("</p>")
        
        s.append("<p><img src=\"graph?node=%s&typ=%s&minsago=%d&duration=%d\" alt=\"graph for node %s\" width=\"700\" height=\"400\"></p>" % (node,typ,mins,mins,node))

        return _page('Time series graph', ''.join(s))
    finally:
        session.close()




def viewLog(req):
    with open("/var/log/ch/BaseLogger.log") as f:
        req.content_type = "text/plain"
        return f.read()

def missing():
    try:
        t = datetime.now() - timedelta(hours=1)
        session = Session()
        s = ['<p>']

        report_set = set([int(x) for (x,) in session.query(distinct(NodeState.nodeId)).filter(NodeState.time > t).all()])
        all_set = set([int(x) for (x,) in session.query(Node.id).filter(and_(Node.houseId != None,Node.roomId != None)).all()])
        missing_set = all_set - report_set
        extra_set = report_set - all_set

        if len(missing_set) == 0:
            s.append("No nodes missing")
        else:
            s.append("</table><p><p><h3>Registered nodes not reporting in last hour</h3><p>")

            s.append("<table border=\"1\">")
            s.append("<tr><th>Node</th><th>House</th><th>Room</th><th>Last Heard</th><th></th></tr>"  )

            for (ns, maxtime) in session.query(NodeState,func.max(NodeState.time)).filter(NodeState.nodeId.in_(missing_set)).group_by(NodeState.nodeId).join(Node,House,Room).order_by(House.address, Room.name).all():
                n = ns.node
                room = "unknown"
                if n.room is not None:
                    room = n.room.name
                s.append("<tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td><a href=\"unregisterNode?node=%d\">(unregister)</a></tr>" % (ns.nodeId, n.house.address, room, str(maxtime), ns.nodeId))
                  

            s.append("</table>")

        if len(extra_set) > 0:
            s.append("</p><h2>Extra nodes that weren't expected</h2><p>")
            for i in sorted(extra_set):
                s.append("%d <a href=\"registerNode?node=%d\">(register)</a><br/>" % (i, i))

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
        headings = ["Node", "House", "Room", "Message count", "Last heard", "Yield"]
        s.extend(["<th>%s</th>" % x for x in headings])
        s.append("</tr>")

        t = datetime.now() - timedelta(days=1)

        nodestateq = session.query(
            NodeState,
            func.count(NodeState),
            func.max(NodeState.time)
            ).filter(NodeState.time > t
                     ).group_by(NodeState.nodeId
                                ).join(Node,House,Room).order_by(House.address, Room.name).all()

        for (ns, cnt, maxtime) in nodestateq:

            n = ns.node
            if n.house is not None:
                yield_secs = (1 * 24 * 3600)

                y = (cnt) / (yield_secs / 300.0) * 100.0


                room = 'unknown'
                if n.room is not None:
                    room = n.room.name
                
                values = [ns.nodeId, n.house.address, room, cnt, maxtime, y]
                fmt = ['%d', '%s', '%s', '%d', '%s', '%8.2f']
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

        s.append("<table border=\"1\">")
        s.append("<tr><th>Node</th><th>House</th><th>Room</th><th>Message Count</th><th>First heard</th><th>Last heard</th><th>Yield</th></tr>")

        for nid, cnt, mintime, maxtime in session.query(
            
            NodeState.nodeId,
            func.count(NodeState),
            func.min(NodeState.time),
            func.max(NodeState.time)).group_by(NodeState.nodeId).all():

            try:
                n = session.query(Node).filter(Node.id == nid).one()
                try:
                    house = n.house.address
                except:
                    house = '-'
                try:
                    room = n.room.name
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
        s.append("<h3>Yield in last 24 hours</h3>")

        s.append("<table border=\"1\">")
        s.append("<tr><th>Node</th><th>Message Count</th><th>Yield</th></tr>")

        t = datetime.now() - timedelta(days=1)

        for nid, cnt in session.query(
            NodeState.nodeId,
            func.count(NodeState)
            ).filter(NodeState.time > t).group_by(NodeState.nodeId).all():
            
            yield_secs = (1 * 24 * 3600)

            y = (cnt) / (yield_secs / 300.0) * 100.0
                
            s.append("<tr><td>%d</td><td>%d</td><td>%8.2f</td></tr>" % (nid, cnt, y))

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
        s.append('<a href="addNewHouse">(add new house)</a></p>')
        s.append("<p>Room: <select name=\"room\">")
        for r in session.query(Room):
            s.append("<option value=\"%d\">%s</option>" % (r.id, r.name))
        s.append("</select>")
        s.append('<a href="addNewRoom">(add new room)</a></p>')
        s.append("<p><input type=\"submit\" value=\"Register\"></p>")
        
        s.append("</form>")

        return _page(''.join(s))
        
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

        n.houseId = None
        n.roomId = None
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

        n.houseId = int(house)
        n.roomId = int(room)
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

        n.houseId = None
        n.roomId = None
        session.commit()
        return _redirect("missing")
    
    except:
        session.rollback()
    finally:
        session.close()
    
def addNewHouse(regnode=None):
    try:
        session = Session()

        s.append("<form action=\"addNewHouseSubmit\">")
        s.append('<input type="hidden" name="regnode" value="%s" />' % (regnode))

        s.append('<p>Address: <input type="text" name="address" /></p>')
        

        s.append('<p>Deployment: <select name="deployment">')
        for d in session.query(Deployment):
            s.append('<option value="%d">%s</option>' % (d.id, d.name))
        s.append('</select>')
        
        s.append("<p><input type=\"submit\" value=\"Register\"></p>")
        
        s.append("</form>")

        return _page('Add new house', ''.join(s))
    finally:
        session.close()

def addNewHouseSubmit(regnode=None, address=None, deployment=None ):
    try:
        session = Session()

        if address is None:
            raise Exception("no address specified")

        address = address.strip().lower()

        h = session.query(House).filter(House.address==address).first()
        if h is not None:
            return _redirect("error")

        h = House(address=address, deploymentId=deployment)
        session.add(h)
        session.commit()
        return _redirect("registerNode?node=%s&house=%d" % (regnode,h.id))
    except Exception, e:
        session.rollback()
        return page('Add new house error', '<p>%s</p>' % str(e))
    finally:
        session.close()
        

def lowbat(bat="2.6"):
    try:
        try:
            batlvl = float(bat)
        except:
            batlvl = 2.6
        t = datetime.now() - timedelta(hours=1)
        session = Session()
        s = []
        empty = True
        for r in session.query(distinct(Reading.nodeId)).filter(and_(Reading.typeId==6,
                                                     Reading.value<=batlvl,
                                                     Reading.time > t)).order_by(Reading.nodeId):
            r = r[0]
            
            s.append("<p><a href=\"graph?node=%d&typ=%s&minsago=%d&duration=%d\">%d</a></p>" % (r,6,60,60,r))
            empty = False

        if empty:
            s.append("<p>No low batteries found</p>")

        return _page('Low batteries', ''.join(s))
    finally:
        session.close()
            

def graph(req,node='64', minsago='1440',duration='1440', debug=None, fmt='bo', typ='0'):

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

        startts = datetime.now() - minsago_i
        endts = startts + duration_i

        qry = session.query(Reading.time,Reading.value).filter(
            and_(Reading.nodeId == int(node),
                 Reading.typeId == int(typ),
                 Reading.time >= startts,
                 Reading.time <= endts))
        #cur.execute("select time, value from reading where type=? and node=? and time <= ? and time >= ?", [int(typ), int(node), endts, startts] )
        t = []
        v = []
        for qt, qv in qry:
            t.append(matplotlib.dates.date2num(qt))
            v.append(qv)



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
                    ax.plot_date(t, v, fmt)

                fig.autofmt_xdate()
                # labels = ax.get_xticklabels()
                # for label in labels:
                #     label.set_rotation(30)

                # try:
                #     thisnode = session.query(Node).filter(Node.id==int(node)).one()
                #     title = "Unknown room " + node
                #     room = "unknown"
                #     if thisnode.room is not None:
                #         room = thisnode.room.name 

                #     house = "unknown"
                #     if thisnode.house is not None:
                #         house = thisnode.house.address

                #     ax.set_title("%s/%s (%s)" % (house, room, node))
                # except ValueError:
                #     pass

                ax.set_xlabel("Date")
                try:
                    thistype = session.query(SensorType.name, SensorType.units).filter(SensorType.id==int(typ)).one()
                    ax.set_ylabel("%s (%s)" % tuple(thistype))
                except:
                    pass


                image = cStringIO.StringIO()
                fig.savefig(image)

            req.content_type = "image/png"

            return image.getvalue()
        else:
            req.content_type = "text/plain"
            return str(t)
    finally:
        session.close()
