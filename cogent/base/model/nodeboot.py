"""
.. codeauthor::  Ross Wiklins
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>

"""

import logging
LOG = logging.getLogger(__name__)

import meta

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, BigInteger, Index, Boolean

#from Bitset import Bitset


class NodeBoot(meta.Base, meta.InnoDBMix):
    """
    It appears that this table holds the state of any nodes.

    :var DateTime time: Timestamp of boot
    :var Integer nodeId: :class:`cogentviewer.models.node.Node`
    :var Integer parent: True if running clustered
    :var String version: Version of the tinyos code being ran from mercurial
    """

    __tablename__ = "NodeBoot"

    time = Column(DateTime,
                primary_key=True)
    nodeId = Column(Integer,
                    ForeignKey('Node.id'))
    clustered = Column(Boolean)
    version = Column(String(20))

    #Add a named index
    __table_args__ = (Index('time',
                            'nodeId'),
                      )

    def __repr__(self):
        return ("NodeBoot(" +
                str(self.time) + "," +
                str(self.nodeId) + "," +
                str(self.clustered) + "," +
                str(self.version) + ")")


    def __cmp__(self, other):
        try:
            val = (self.time - other.time).seconds
            val += self.nodeId - other.nodeId
            return val
        except TypeError, e:
            LOG.warning("Unable to Compare {0} {1} \n{2}".format(self, other, e))


    def pandas(self):
        """Return this object as something suitable for pandas"""
        
        #Igonre parent / rssi as we dont really use them
        return {"time":self.time,
                "nodeId":self.nodeId}                
