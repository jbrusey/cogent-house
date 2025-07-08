"""Fridge should be less than 10 degrees

"""

THRESHOLD = 10

from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from cogent.base.model import (Node,
                               Room,
                               Location,
                               Reading,
                               LastReport
                               )

def fridge_open(session,
                end_t=datetime.utcnow(),
                start_t=(datetime.utcnow() - timedelta(hours=4))):
    html = []

    fridge_temperature = (session.query(Reading.time, Reading.value)
                       .join(Location, Node, Room)
                       .filter(and_(Reading.time >= start_t,
                                    Reading.time <= end_t,
                                    Reading.typeId == 0,
                                    Room.name == "fridge"
                       ))
                       .order_by(Reading.time.desc())
                       .first())

    if fridge_temperature is not None:
        (qt, qv) = fridge_temperature
        if qv > THRESHOLD:
            html.append('<p><b>Fridge temperature is {} at {}</b></p>'
                        .format(qv, qt))
    else:
        html.append('<p><b>Missing fridge temperature reading </b></p>')
    return html
