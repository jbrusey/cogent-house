"""
Class's to define and create a Remote Database

:author: Dan Goldsmith <djgoldsmith@googlemail.com>
:date: March 2012
"""
#from pyramid import testing
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper

#RemoteBase = declarative_base()
# #engine = sqlalchemy.create_engine("mysql+mysqldb://root:Ex3lS4ga@127.0.0.1/ch")
# #REMOTESESSION = sqlalchemy.orm.sessionmaker(bind=engine)

#Globals
#Session = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker())
RemoteSession = sqlalchemy.orm.sessionmaker()
RemoteMetadata = sqlalchemy.MetaData()

class RemoteDeployment(object):
    pass

class RemoteHouse(object):
    pass

class RemoteNode(object):
    pass
# class RemoteHouse(RemoteBase):
#     __tablename__ = "House"
#    __table__ =  sqlalchemy.Table("House")
#                                  RemoteBase.metadata,
#                                  autoload=True,
#                                  autoload_with=engine)

def reflectTables(engine):
    print "Reflecting Tables"
    deployment = sqlalchemy.Table('Deployment',
                                  RemoteMetadata,
                                  autoload=True,
                                  autoload_with=engine)

    mapper(RemoteDeployment,deployment)

    house = sqlalchemy.Table('House',
                             RemoteMetadata,
                             autoload=True,
                             autoload_with=engine)
    mapper(RemoteHouse,house)

    node = sqlalchemy.Table('Node',
                            RemoteMetadata,
                            autoload=True,
                            autoload_with=engine)
    mapper (RemoteNode,node)
    pass

def initialise_sql(engine):
    """Intialise a connection to the database and reflect all Remote Tables

    :param String engine: Database String of Engine to Connect to
    """
    #print "Initalising Engine"
    RemoteSession.configure(bind=engine)
    #Metadata.bind = engine
    #Reflect Tables
    reflectTables(engine)
    pass


# if __name__ == "__main__":
#     print "Testing Remote Models"

#     #Create an Engine
#     #engine = sqlalchemy.create_engine("sqlite:///:memory:")
#     engine = sqlalchemy.create_engine("mysql+mysqldb://root:Ex3lS4ga@127.0.0.1/ch")

#     initialise_sql(engine)

#     session = Session()
#     theQry = session.query(RemoteNode).all()
#     for item in theQry:
#         print item

        
