"""Server is likely to be down if no nodes have responded in last X hours

Assume X to be 4 hours
"""


from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from cogent.base.model import (Node,
                               House,
                               Room,
                               Location,
                               LastReport,
                               NodeState)

def server_down(session,
                end_t=datetime.utcnow(),
                start_t=(datetime.utcnow() - timedelta(hours=4))):
    html = []
    node_state = (session.query(NodeState.nodeId.label('nodeId'))
                  .filter(and_(NodeState.time >= start_t,
                               NodeState.time <= end_t))
                  .first())

    if node_state is None:
        html.append('<p><b>No nodes have reported between {} and {}</b></p>'
                    .format(start_t, end_t))

    return html
