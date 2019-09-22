"""Pantry should have a humidity less than 80%

"""


from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from cogent.base.model import (Node,
                               Room,
                               Location,
                               Reading,
                               LastReport
                               )

def pantry_humid(session,
                 end_t=datetime.utcnow(),
                 start_t=(datetime.utcnow() - timedelta(hours=4))):
    html = []

    pantry_humidity = (session.query(Reading.time, Reading.value)
                       .join(Location, Node, Room)
                       .filter(and_(Reading.time >= start_t,
                                    Reading.time <= end_t,
                                    Reading.typeId == 2,
                                    Room.name == "pantry"
                       ))
                       .order_by(Reading.time.desc())
                       .first())

    if pantry_humidity is not None:
        (qt, qv) = pantry_humidity
        if qv > 80:
            html.append('<p><b>Pantry humidity is {} at {}</b></p>'
                        .format(qv, qt))

    return html
