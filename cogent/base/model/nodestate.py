"""
.. codeauthor::  Ross Wiklins
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>

"""

import logging
LOG = logging.getLogger(__name__)

import meta

from sqlalchemy import Column, Integer, ForeignKey, DateTime, BigInteger, Index

#from Bitset import Bitset


class NodeState(meta.Base, meta.InnoDBMix):
    """
    It appears that this table holds the state of any nodes.

    :var Integer id: Id of NodeState
    :var DateTime time: Timestamp of state
    :var Integer nodeId: :class:`cogentviewer.models.node.Node`
    :var Integer parent: Parent node in the routing tree?
    :var BigInteger localtime: Local time of the node (in unix time??)
    """

    __tablename__ = "NodeState"

    id = Column(Integer,
                primary_key=True)
    time = Column(DateTime)
    nodeId = Column(Integer,
                    ForeignKey('Node.id'))
    parent = Column(Integer)
    localtime = Column(BigInteger)
    seq_num = Column(Integer)
    rssi = Column(Integer)

    #Add a named index
    __table_args__ = (Index('ns_1',
                            'time',
                            'nodeId',
                            'localtime'),
                      )

    def __repr__(self):
        return ("NodeState(" +
                str(self.id) + "," +
                str(self.time) + "," +
                str(self.nodeId) + "," +
                str(self.parent) + "," +
                str(self.localtime) + ")")


    def __cmp__(self, other):
        try:
            val = (self.time - other.time).seconds
            val += self.nodeId - other.nodeId
            val += self.parent - other.parent
            return val
        except TypeError, e:
            LOG.warning("Unable to Compare {0} {1} \n{2}".format(self, other, e))


    def pandas(self):
        """Return this object as something suitable for pandas"""
        
        #Igonre parent / rssi as we dont really use them
        return {"id":self.id,
                "localtime":self.localtime,
                "nodeId":self.nodeId,
                "seq_num":self.seq_num,
                "time":self.time}
                
