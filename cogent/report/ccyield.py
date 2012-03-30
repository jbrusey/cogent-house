from sqlalchemy import and_, distinct, func
from datetime import datetime, timedelta
from cogent.base.model import *



def ccYield(session, missed_thresh=10, end_t=datetime.utcnow(), start_t=(datetime.utcnow() - timedelta(days=1))):
    html = []

    last_lost_nodes = session.query(LastReport).filter(LastReport.name=="lost-cc-nodes").first()
    if last_lost_nodes is not None:
        last_lost_nodes_set = eval(last_lost_nodes.value)
    else:
        last_lost_nodes_set = set()

    q = session.query(
        Reading.nodeId,
        func.count(Reading.time),
        func.max(Reading.time),
        House.address,
        Room.name
        ).filter(
            and_(
                Reading.time >= start_t,
                Reading.time < end_t,
                Reading.typeId == 11,
                Node.nodeTypeId == 1,
                )).group_by(
                    Reading.nodeId
                ).join(
                    Node, Location, House, Room
                    ).order_by(
                        House.address, Room.name
                        ).all()

    low_nodes = set()
    ok_nodes = set()
    low_nodes_report = []
    # assumes 5 minute period
    expected_yield = (end_t - start_t).seconds / 300
    
    for (n, cnt, maxtime, hn, rn) in q:

        missed = expected_yield - cnt 
        y = (cnt * 100.) / expected_yield

        if missed > missed_thresh:
            low_nodes.add(n)
            low_nodes_report.append([n, hn, rn, cnt, maxtime, y])
        else:
            ok_nodes.add(n)

    all_set = set([int(x) for (x,) in session.query(Node.id).filter(
        and_(
            Node.locationId != None,
            Node.nodeTypeId == 1
            )).all()])

    lost_nodes = all_set - ok_nodes - low_nodes

    if last_lost_nodes is None:
        last_lost_nodes = LastReport(name="lost-cc-nodes", value=repr(lost_nodes))
        session.add(last_lost_nodes)
    else:
        last_lost_nodes.value = repr(lost_nodes)
    session.commit()


    if len(low_nodes) > 0:
        html.append('<h3>Low yield current-cost nodes</h3>')
        html.append('<table border="1">')
        html.append("<tr>")
        headings = ["Node", "House", "Room", "Message count", "Last heard", "Yield"]
        html.extend(["<th>%s</th>" % x for x in headings])
        html.append("</tr>")
        fmt = ['%d', '%s', '%s', '%d', '%s', '%8.2f']
        for values in low_nodes_report:
            html.append("<tr>")
            html.extend([("<td>" + f + "</td>") % v for (f,v) in zip(fmt, values)])
            html.append("</tr>")
            
        html.append('</table>')


    just_lost_nodes = lost_nodes - last_lost_nodes_set

    recovered_nodes = last_lost_nodes_set - lost_nodes

    if len(just_lost_nodes) > 0:
        html.append('<h3>Current-cost nodes recently lost</h3>')
        html.append('<table border="1">')
        html.append("<tr>")
        headings = ["Node", "House", "Room"]
        html.extend(["<th>%s</th>" % x for x in headings])
        html.append("</tr>")
        fmt = ['%d', '%s', '%s']
        for values in session.query(Node.id, House.address, Room.name).filter(
            Node.id.in_(just_lost_nodes)).join(Location, House, Room).all():
            html.append("<tr>")
            html.extend([("<td>" + f + "</td>") % v for (f,v) in zip(fmt, values)])
            html.append("</tr>")
        html.append('</table>')

    if len(recovered_nodes) > 0:
        recovered_list = session.query(Node.id, House.address, Room.name).filter(
            Node.id.in_(recovered_nodes)).join(Location, House, Room).all()
        if len(recovered_list) > 0:
            html.append('<h3>Current Cost nodes recently recovered</h3>')
            html.append('<table border="1">')
            html.append("<tr>")
            headings = ["Node", "House", "Room"]
            html.extend(["<th>%s</th>" % x for x in headings])
            html.append("</tr>")
            fmt = ['%d', '%s', '%s']
            for values in recovered_list:
                recovered_nodes.remove(values[0])
                html.append("<tr>")
                html.extend([("<td>" + f + "</td>") % v for (f,v) in zip(fmt, values)])
                html.append("</tr>")
            html.append('</table>')

        if len(recovered_nodes) > 0:
            # these nodes must have been unregistered
            html.append('<h3>Current Cost nodes recently unregistered</h3><p>')
            html.append(', '.join([str(x) for x in recovered_nodes]))
            html.append('</p>')
        
    return html
