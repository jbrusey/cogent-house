from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref
import sqlalchemy.types as types

import unittest2 as unittest
from datetime import datetime, timedelta

#Original Version used this namespace,
#So I will too.
#from cogent.base.model.Bitset import Bitset

try:
    import cogent
except ImportError:
    #Assume we are running from the test directory
    print "Unable to Import Cogent Module Appending Path"
    import sys
    sys.path.append("../")


from cogent.base.model import *

#from cogent.base.model.meta import Session, Base

DBURL="sqlite:///:memory:"

import base

@unittest.skip
class TestNodeType(base.BaseTestCase):

    # @classmethod
    # def setUpClass(cls):
    #     print "Setting up testing database"
    #     from sqlalchemy import create_engine

    #     engine = create_engine(DBURL, echo=False)
    #     engine.execute("pragma foreign_keys=on")
        
    #     init_model(engine)
    #     metadata = Base.metadata
    #     metadata.create_all(engine)
    #     cls.engine = engine
    #     cls.metadata = metadata


    # def setUp(self):
    #     session = Session()
    #     engine = session.get_bind(mapper=None)
    #     session.close()
    #     Base.metadata.create_all(engine)

    # def tearDown(self):
    #     session = Session()
    #     engine = session.get_bind(mapper=None)
    #     session.close()
    #     Base.metadata.drop_all(engine)

        
    def test1(self):
        session = Session()
        b = Bitset(size=20)
        b[3] = True
        b[13] = True

        r = NodeType(time=datetime.utcnow(),
                     id=0,
                     name="base",
                     seq=1,
                     updated_seq=1,
                     period=1024*300,
                     configured=b)
        try:
            session.add(r)
            session.commit()
            self.assertTrue( r.configured[3] and r.configured[13] )
        except Exception,e:
            print e
            session.rollback()
        finally:
            session.close()


    def test2(self):
        session = Session()
        b = Bitset(size=20)
        b[3] = True
        b[13] = True

        r = NodeType(time=datetime.utcnow(),
                     id=0,
                     name="base",
                     seq=1,
                     updated_seq=1,
                     period=1024*300,
                     configured=b)
        try:
            session.add(r)
            session.commit()
        except Exception,e:
            print e
            session.rollback()
        finally:
            session.close()

        session = Session()
        try:
            r = session.query(NodeType).get(0)

            self.assertTrue( r.name == "base" )

            
            self.assertTrue( r.configured[3] and r.configured[13] )
        finally:
            session.close()

    def test3(self):
        session = Session()
        try:
            r = session.query(NodeType).get(0)
            self.assertTrue( r )
        finally:
            session.close()
        
@unittest.skip    
class TestSchema(base.BaseTestCase):
    
    # @classmethod
    # def setUpClass(cls):
    #     print "Setting up testing database"
    #     from sqlalchemy import create_engine

    #     engine = create_engine(DBURL, echo=False)
    #     engine.execute("pragma foreign_keys=on")
    #     init_model(engine)
    #     metadata = Base.metadata
    #     metadata.create_all(engine)
    #     cls.engine = engine
    #     cls.metadata = metadata


    # def setUp(self):
    #     session = Session()
    #     engine = session.get_bind(mapper=None)
    #     session.close()
    #     Base.metadata.create_all(engine)
    #     #self.metadata.create_all(engine)

    # def tearDown(self):
    #     session = Session()
    #     engine = session.get_bind(mapper=None)
    #     session.close()
    #     Base.metadata.drop_all(engine)
    
    
    def test1(self):
        session = Session()

        #Add a deployment


        dep = Deployment(name="TestDep",
                         description="Does this work",
                         startDate=datetime.utcnow()
                         , endDate=None)
        session.add(dep)
        session.commit()
        depid = dep.id

        #Add a room type

        rt = RoomType(name="Bedroom")
        session.add(rt)
        session.commit()


        #Add Deployment Meta data
        dm = DeploymentMetadata(deploymentId=depid,
                                 name="Manual Reading",
                                 description="Read something",
                                 units="kwh",
                                 value="99999")
        session.add(dm)
        session.commit()


        #Add a house
        h = House(deploymentId=1,
                  address = "1 Sampson",
                  startDate=datetime.utcnow())

        session.add(h)
        session.commit()


        #Add house metadata

        hm = HouseMetadata(houseId=1,
                                 name="Manual Reading",
                                 description="Read something",
                                 units="kwh",
                                 value="99999")
        session.add(hm)
        session.commit()


        #Add Occupier

        occ=Occupier(houseId=1,
                     name="Mr Man",
                     contactNumber="01212342345",
                     startDate=datetime.utcnow()
                     )

        session.add(occ)
        session.commit()

        #Add rooms
        rt_bedroom = RoomType(name="Bedroom")
        session.add(rt_bedroom)
        session.commit()
        
        r=Room(roomTypeId=rt_bedroom.id,
               name="BedroomA")
        

        session.add(r)
        session.commit()

        #Add a node
        configured = Bitset(size=14)
        configured[0] = True
        configured[2] = True
        configured[4] = True
        configured[5] = True
        configured[6] = True
        configured[13] = True
        configured1 = Bitset(size=14)
        configured1[13] = True
        # session.add_all(
        #     [
        #         # NodeType(time=datetime.utcnow(),
        #         #          id=0,
        #         #          name="base",
        #         #          seq=1,
        #         #          updated_seq=0,
        #         #          period=15*1024,
        #         #          configured=configured),
        #         # NodeType(time=datetime.utcnow(),
        #         #          id=1,
        #         #          name="cc",
        #         #          seq=1,
        #         #          updated_seq=0,
        #         #          period=15*1024,
        #         #          configured=configured1),
        #         ])                    

        # session.commit()

        #Add sensors

        #Add sensor types

        #Add readings

        ll = Location(houseId=h.id,
                      roomId=r.id)
        session.add(ll)

        n = Node(id=63,
                 locationId=ll.id,
                 nodeTypeId=0)
        session.add(n)

        st = SensorType(id=0,
                        name="Temperature",
                        code="Tmp",
                        units="deg.C")

        session.add(st)
        session.commit()

        tt = datetime.utcnow() - timedelta(minutes=(500))
        
        for i in range(100):

            ll = session.query(Node).filter(Node.id==63).one().locationId
            
            r = Reading(time=tt,
                        nodeId=63,
                        typeId=0,
                        locationId=ll,
                        value=i/1000.)
            session.add(r)
            ns = NodeState(time=tt,
                           nodeId=63,
                           parent=64,
                           localtime=( (1<<32) - 50 + i)) # test large integers
            session.add(ns)
            tt = tt + timedelta(minutes=5)
        session.commit()

        session.close()
        session = Session()

        loctimes = [x[0] for x in session.query(NodeState.localtime).all()]
        #print max(loctimes) - min(loctimes)
        self.assertTrue(max(loctimes) - min(loctimes) == 99) 


if __name__ == "__main__":
    from sqlalchemy import create_engine
    # from sqlalchemy.orm import sessionmaker

  

    engine = create_engine(DBURL, echo=False)
    engine.execute("pragma foreign_keys=on")
    init_model(engine)
    metadata = Base.metadata
    metadata.create_all(engine)

    unittest.main()
