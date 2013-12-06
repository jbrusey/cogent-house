"""
.. codeauthor::  Ross Wiklins
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>

"""

import meta

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime


class NodeHistory(meta.Base, meta.InnoDBMix):
    """
    Class to hold history of the node

    :var Integer nodeId: Id of :class:`cogentviewer.models.node.Node`
        this history belogs to
    :var DateTime startDate:
    :var DateTime endDate:
    :var String houseAddress:
    :var String roomType:
    :var String roomName:
    """

    __tablename__ = "NodeHistory"

    nodeId = Column(Integer, ForeignKey('Node.id'), primary_key=True)
    startDate = Column(DateTime, primary_key=True)
    endDate = Column(DateTime)
    houseAddress = Column(String(255))
    roomType = Column(String(255))
    roomName = Column(String(255))
