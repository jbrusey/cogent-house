import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import meta as meta

Base = meta.Base
#DBSession = meta.Session()

import populateData
import cogentviewer.models as models
from ..models import (
    deployment,
    deploymentmetadata,
    host,
    house,
    housemetadata,
    lastreport,
    location,
    node,
    nodehistory,
    nodestate,
    nodetype,
    occupier,
    rawmessage,
    reading,
    room,
    roomtype,
    sensor,
    sensortype,
    weather,
    uploadurl,
    event,
    #DBSession,
    #Base,
    #user,
    #deployment,
    )



def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    meta.Session.configure(bind=engine)
    Base.metadata.bind = engine

    DBSession = meta.Session()
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    populateData.init_data(DBSession)
