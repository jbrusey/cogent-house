"""The application's model objects"""
from cogent.base.model.meta import Session, Base

from cogent.base.model.Bitset import Bitset
from cogent.base.model.deployment import Deployment
from cogent.base.model.deploymentmetadata import DeploymentMetadata
from cogent.base.model.house import House
from cogent.base.model.housemetadata import HouseMetadata
from cogent.base.model.lastreport import LastReport
from cogent.base.model.location import Location
from cogent.base.model.node import Node
from cogent.base.model.nodehistory import NodeHistory
from cogent.base.model.nodestate import NodeState
from cogent.base.model.nodetype import NodeType
from cogent.base.model.occupier import Occupier
from cogent.base.model.reading import Reading
from cogent.base.model.room import Room
from cogent.base.model.roomtype import RoomType
from cogent.base.model.sensor import Sensor
from cogent.base.model.sensortype import SensorType
from cogent.base.model.weather import Weather


def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine)
