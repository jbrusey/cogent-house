from sqlalchemy import and_, distinct, func
from datetime import datetime, timedelta
from cogent.base.model import *

def nodesInSet(session, node_set):
    html = []
    html.append("<table border=\"1\">")
    html.append("<tr><th>Node</th><th>House</th><th>Room</th></tr>"  )
    for (r, addr, name) in session.query(Node.id, House.address, Room.name).filter(
            Node.id.in_(node_set)).join(Location, House,Room).order_by(House.address, Room.name).all():
        html.append("<tr><td>%d</td><td>%s</td><td>%s</td></tr>" % (r,addr,name))

    html.append("</table>")
    return html

def lowBat(session,
           bat_thresh=2.6,
           count_thresh=3,
           end_t=datetime.utcnow(),
           start_t=(datetime.utcnow() - timedelta(days=1))):
    html = []

    last_lowbat = session.query(LastReport).filter(LastReport.name=="low-bat-nodes").first()
    if last_lowbat is not None:
        last_lowbat_set = eval(last_lowbat.value)
        #set([int(x) for x in last_lowbat.value.split(',')])
    else:
        last_lowbat_set = set()

    lowBatHeader = True

    lowbat_set = set()
    for (n,c) in session.query(Reading.nodeId, func.count(Reading.nodeId).label('count')).filter(
        and_(Reading.typeId==6,
             Reading.time >= start_t,
             Reading.time < end_t,
             Reading.value < bat_thresh)).group_by(Reading.nodeId).all():

        if c >= count_thresh:
            lowbat_set.add(n)

    print "-"*80
    print "LOWBAT SET", lowbat_set
    print "LASTBAT SET", last_lowbat_set

    if lowbat_set != last_lowbat_set:

        gone_low = lowbat_set - last_lowbat_set
        gone_high = last_lowbat_set - lowbat_set

        if len(gone_low) > 0:
            html.append('<h3>Nodes that have started to report low battery</h3>')
            html.extend(nodesInSet(session, gone_low))

        if len(gone_high) > 0:
            html.append('<h3>Nodes no longer reporting low battery</h3>')
            html.extend(nodesInSet(session, gone_high))

        
        #        s = ','.join([str(a) for a in lowbat_set])
        
        if last_lowbat is None:
            last_lowbat = LastReport(name="low-bat-nodes", value=repr(lowbat_set))
            session.add(last_lowbat)
        else:
            last_lowbat.value = repr(lowbat_set)
        session.commit()

    return html
