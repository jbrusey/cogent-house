from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from cogent.base.model import (Node,
                               House,
                               Room,
                               Location,
                               LastReport,
                               NodeState)
from cogent.sip.calc_yield import calc_missed_and_yield

def table_with_nodes(session, html, node_set):
    """ produce an html table listing a set of nodes
    """
    html.append('<table border="1">')
    html.append("<tr>")
    headings = ["Node", "House", "Room"]
    html.extend(["<th>%s</th>" % x for x in headings])
    html.append("</tr>")
    fmt = ['%d', '%s', '%s']
    for values in (session.query(Node.id, House.address, Room.name)
                   .filter(Node.id.in_(node_set))
                   .join(Location, House, Room)
                   .all()):
        html.append("<tr>")
        html.extend([("<td>" + f + "</td>") % v
                     for (f, v) in zip(fmt, values)])
        html.append("</tr>")
    html.append('</table>')


def packetYield(session,
                missed_thresh=5,
                end_t=datetime.utcnow(),
                start_t=(datetime.utcnow() - timedelta(days=1))):
    """ report on percentage of packets received over packets transmitted.
    """
    html = []

    last_lost_nodes = (session.query(LastReport)
                       .filter(LastReport.name == "lost-nodes").first())
    if last_lost_nodes is not None:
        last_lost_nodes_set = eval(last_lost_nodes.value)
    else:
        last_lost_nodes_set = set()

    # next get the count per node
    seqcnt_q = (session.query(NodeState.nodeId.label('nodeId'),
                              func.count(NodeState.seq_num).label('cnt'))
                    .filter(and_(NodeState.time >= start_t,
                                 NodeState.time <= end_t))
                    .group_by(NodeState.nodeId)
                    .subquery(name='seqcnt'))

    # next get the first occurring sequence number per node
    selmint_q = (session.query(NodeState.nodeId.label('nodeId'),
                               func.min(NodeState.time).label('mint'))
                        .filter(NodeState.time >= start_t)
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
                        .filter(NodeState.time >= start_t)
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
               .filter(or_(House.endDate == None,
                           House.endDate >= start_t))
               .order_by(House.address, Room.name))

    low_nodes = set()
    ok_nodes = set()
    low_nodes_report = []
    
    for (node_id, maxseq, minseq, seqcnt, last_heard,
         house_name, room_name) in yield_q.all():

        (missed, yld) = calc_missed_and_yield(seqcnt,
                                            minseq,
                                            maxseq)

        if missed > missed_thresh:
            low_nodes.add(node_id)
            low_nodes_report.append([node_id, house_name, room_name,
                                     seqcnt, last_heard, yld])
        else:
            ok_nodes.add(node_id)

    all_set = set([int(x) for (x,) in session.query(Node.id).filter(
        Node.locationId != None).all()])

    lost_nodes = all_set - ok_nodes - low_nodes

    if last_lost_nodes is None:
        last_lost_nodes = LastReport(name="lost-nodes", value=repr(lost_nodes))
        session.add(last_lost_nodes)
    else:
        last_lost_nodes.value = repr(lost_nodes)
    session.commit()


    if len(low_nodes) > 0:
        html.append('<h3>Low yield nodes</h3>')
        html.append('<table border="1">')
        html.append("<tr>")
        headings = ["Node", "House", "Room", "Message count",
                    "Last heard", "Yield"]
        html.extend(["<th>%s</th>" % x for x in headings])
        html.append("</tr>")
        fmt = ['%d', '%s', '%s', '%d', '%s', '%8.2f']
        for values in low_nodes_report:
            html.append("<tr>")
            html.extend([("<td>" + f + "</td>") % v
                         for (f, v) in zip(fmt, values)])
            html.append("</tr>")

        html.append('</table>')


    just_lost_nodes = lost_nodes - last_lost_nodes_set

    recovered_nodes = last_lost_nodes_set - lost_nodes

    still_lost_nodes = last_lost_nodes_set & lost_nodes

    if len(still_lost_nodes) > 0:
        html.append('<h3>These nodes are still lost</h3>')
        table_with_nodes(session, html, still_lost_nodes)

    if len(just_lost_nodes) > 0:
        html.append('<h3>Nodes recently lost</h3>')
        table_with_nodes(session, html, just_lost_nodes)

    if len(recovered_nodes) > 0:
        recovered_list = (session.query(Node.id, House.address, Room.name)
                                 .filter(Node.id.in_(recovered_nodes))
                                 .join(Location, House, Room).all())
        if len(recovered_list) > 0:
            html.append('<h3>Nodes recently recovered</h3>')
            html.append('<table border="1">')
            html.append("<tr>")
            headings = ["Node", "House", "Room"]
            html.extend(["<th>%s</th>" % x for x in headings])
            html.append("</tr>")
            fmt = ['%d', '%s', '%s']
            for values in recovered_list:
                recovered_nodes.remove(values[0])
                html.append("<tr>")
                html.extend([("<td>" + f + "</td>") % v
                             for (f, v) in zip(fmt, values)])
                html.append("</tr>")
            html.append('</table>')

        if len(recovered_nodes) > 0:
            # these nodes must have been unregistered
            html.append('<h3>Nodes recently unregistered</h3><p>')
            html.append(', '.join([str(x) for x in recovered_nodes]))
            html.append('</p>')

    return html
