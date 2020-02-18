"""
Classes to initialise the SQL and populate with default Sensors

..version::    0.4
..codeauthor:: Dan Goldsmith
..date::       Feb 2012

..since 0.4:: 
    Models updated to use Mixin Class, This should ensure all
    new tables are created using INNODB
"""

from . import meta

#Namespace Mangling
from .Bitset import Bitset
from .deployment import Deployment
from .deploymentmetadata import DeploymentMetadata
from .host import Host
from .house import House
from .lastreport import LastReport
from .location import Location
from .node import Node
from .nodehistory import NodeHistory
from .nodestate import NodeState
from .nodetype import NodeType
from .nodeboot import NodeBoot
from .occupier import Occupier
from .rawmessage import RawMessage
from .reading import Reading
from .room import Room
from .roomtype import RoomType
from .sensor import Sensor
from .sensortype import SensorType
from .weather import Weather
from .event import Event
from .timings import Timings
from .user import User
from .server import Server
from .pushstatus import PushStatus
from . import populateData

import json

#Setup Logging
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)

TABLEMAP = {}

from .util import (init_model,
                   initialise_sql,
                   findClass,
                   newClsFromJSON,
                   clsFromJSON)

