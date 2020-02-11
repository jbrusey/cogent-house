"""
.. codeauthor::  Ross Wiklins
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>

"""

import logging
LOG = logging.getLogger(__name__)

from . import meta

from sqlalchemy import Column, Integer, ForeignKey, DateTime, BigInteger, Index

#from Bitset import Bitset


class NodeState(meta.Base, meta.InnoDBMix):
    """
    This table holds the state of any nodes.

    :var DateTime time: Timestamp of state
    :var Integer nodeId: :class:`cogentviewer.models.node.Node`
    :var Integer parent: Parent node in the routing tree?
    :var BigInteger localtime: Local time of the node (in unix time??)
    :var Integer seq_num: packet sequence number
    :var Integer rssi: received signal strength indicator
    """

    __tablename__ = "NodeState"

    time = Column(DateTime,
                  primary_key=True,
                  nullable=False,
                  autoincrement=False,
                  index=True)
    nodeId = Column(Integer,
                    ForeignKey('Node.id'),
                    primary_key=True,
                    nullable=False,
                    autoincrement=False,
                    index=True)
    parent = Column(Integer)
    localtime = Column(BigInteger)
    seq_num = Column(Integer,
                     primary_key=True,
                     nullable=False,
                     autoincrement=False,
                     index=True)
    rssi = Column(Integer)

    #Add a named index
    __table_args__ = (Index('ns_1',
                            'time',
                            'nodeId',
                            'localtime'),
                      )

    def __repr__(self):
        return ("NodeState(" +
                str(self.time) + "," +
                str(self.nodeId) + "," +
                str(self.parent) + "," +
                str(self.localtime) + ")")

    def __eq__(self, other):
        return ((self.time, self.nodeId, self.parent) ==
                (other.time, other.nodeId, other.parent))

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return ((self.time, self.nodeId, self.parent) <
                (other.time, other.nodeId, other.parent))


    def pandas(self):
        """Return this object as something suitable for pandas"""
        
        #Igonre parent / rssi as we dont really use them
        return {"localtime":self.localtime,
                "nodeId":self.nodeId,
                "seq_num":self.seq_num,
                "rssi": self.rssi,
                "parent": self.parent,
                "time":self.time}
                
