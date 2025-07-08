from cogent.sip.sipsim import (
    PartSplineReconstruct,
    SipPhenom,
    )

from sqlalchemy import create_engine, and_, distinct, func
from sqlalchemy.orm import aliased
from sqlalchemy.orm.exc import NoResultFound


def get_value_and_delta(session,
                        node_id,
                        reading_type,
                        delta_type,
                        sd,
                        ed):
    """ get values and deltas given a node id, type, delta type, start
    and end date.
    """
    # make sure that time period is covered by the data
    try:
        (sd1, ) = (session.query(func.max(Reading.time))
                          .filter(and_(Reading.nodeId == node_id,
                                       Reading.typeId == reading_type,
                                       Reading.time < sd))
                          .one())
        if sd1 is not None:
            sd = sd1
    except NoResultFound:
        pass

    try:
        (ed1, ) = (session.query(func.min(Reading.time))
                          .filter(and_(Reading.nodeId == node_id,
                                       Reading.typeId == reading_type,
                                       Reading.time > ed))
                          .one())
        if ed1 is not None:
            ed = ed1
    except NoResultFound:
        pass

    s2 = aliased(Reading)
    return (session.query(Reading.time,
                          Reading.value,
                          s2.value,
                          NodeState.seq_num)
                   .join(s2, and_(Reading.time == s2.time,
                                  Reading.nodeId == s2.nodeId))
                   .join(NodeState,
                         and_(Reading.time == NodeState.time,
                              Reading.nodeId == NodeState.nodeId))
                   .filter(and_(Reading.typeId == reading_type,
                                s2.typeId == delta_type,
                                Reading.nodeId == node_id,
                                Reading.time >= sd,
                                Reading.time <= ed
                                ))
                   .order_by(Reading.time))


def predict(sip_tuple, end_time, restrict=timedelta(hours=7)):
    """ takes in a sip_tuple containing:
    (datetime, value, delta, seq)
    and predicts the value at time end_time. returns a tuple
    with the same elements.
    Restrict forward prediction to 7 hours
    """
    (oldt, value, delta, seq) = sip_tuple
    deltat = end_time - oldt
    if deltat > restrict:
        deltat = restrict
        end_time = oldt + deltat
    return (end_time,
            (end_time - oldt).total_seconds() * delta + value)


def estimate_current_value(session, node_id, type_id, delta_id, endts=datetime.utcnow()):

    # get the last hours data
    last_readings = list(get_value_and_delta(session,
                                             node_id,
                                             type_id,
                                             delta_id,
                                             endts - timedelta(hours=1),
                                             endts))

    if len(last_readings) > 0:
        return predict(last_readings[-1], endts)
    else:
        return None
