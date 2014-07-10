"""

Class to hold details of servers that have been deployed

"""

import sqlalchemy
from sqlalchemy.orm import relationship

import meta

class Server(meta.Base, meta.InnoDBMix):
    """
    Table to hold information about Servers

    :var integer id: id (pk)
    :var string servername: name
    :var integer baseid: Id of Base Node
    :var integer houseid: Id of house this node is deployed in
    """


    __tablename__ = "Server"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    hostname = sqlalchemy.Column(sqlalchemy.String(255))

    baseid = sqlalchemy.Column(sqlalchemy.Integer, 
                               sqlalchemy.ForeignKey("Node.id"))
    #houseid = sqlalchemy.Column(sqlalchemy.Integer,
    #                            sqlalchemy.ForeignKey("House.id"))

    rpc = sqlalchemy.Column(sqlalchemy.Integer) #Store RPC values as a bitmask
    #node = relationship("Node", "Server")
    houses = relationship("House", backref="server")
