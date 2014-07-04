"""Class to populate the testing DB based on the Owls Servers"""

#DEPLOYMENTS = 

import datetime

import cogentviewer.models as models

import logging


def cleardb(session):
    """Class to remove all test data"""
    session.execute("DELETE FROM Deployment")
    session.execute("DELETE FROM Server")
    session.execute("DELETE FROM House")
    session.execute("DELETE FROM Node")
    session.execute("DELETE FROM Location")
    session.execute("DELETE FROM PushStatus")
    session.execute("DELETE FROM NodeState")
    session.execute("DELETE FROM Reading")
    #session.execute("DELETE FROM Room")

    
    #session.execute("DELETE FROM LastReport")
    session.flush()
    session.commit()

def populatedata(session):
    """Populate with some testing data"""

    now = datetime.datetime.utcnow()
    startdate = now - datetime.timedelta(days=14)
    cutdate = now - datetime.timedelta(days=7)
    enddate  = now - datetime.timedelta(hours=1)

    #Add A Deployment
    thedeployment = models.Deployment(id=1, name="Testing Deployments")
    session.add(thedeployment)
    session.flush()

    #And three servers (However only two are actually deployed)
    theserver = models.Server(id=1, hostname="server1", baseid=41)
    session.add(theserver)
    theserver = models.Server(id=2, hostname="server2", baseid=42)
    session.add(theserver)
    theserver = models.Server(id=3, hostname="server3", baseid=44)
    session.add(theserver)
    session.flush()
    
    #Add some houses
    thehouse = models.House(id=1, address="address1", deploymentId = 1, serverid=1)
    session.add(thehouse)
    thehouse = models.House(id=2, address="address2", deploymentId = 1, serverid=1)
    session.add(thehouse)
    thehouse = models.House(id=3, address="address3", deploymentId = 1, serverid=1)
    session.add(thehouse)
    thehouse = models.House(id=4, address="address4", deploymentId = 1, serverid=2)
    session.add(thehouse)
    #House that is out of date
    thehouse = models.House(id=5, address="address5", deploymentId = 1)
    session.add(thehouse)

    #Next nodes and locations (two for each house)
    locidx = 1
    allnodes = []
    for house in range(4):
        for room in range(2):
            thisloc = models.Location(id = locidx, houseId = house+1, roomId = room+1)
            session.add(thisloc)
            nid = house*10 + room
            thisnode = models.Node(id=nid, locationId = locidx)
            session.add(thisnode)
            allnodes.append(nid)
            session.flush()
            locidx += 1

    nidx = 1000
    for x in range(2):
        thisnode = models.Node(id = nidx)
        session.add(thisnode)
        nidx+=1


    session.flush()
    session.commit()
    

    #STUFF FOR PUSH STATUS
    currenttime = startdate
    while currenttime <= cutdate:
        for server in ["server1", "server2", "server3"]:
            pstat = models.PushStatus(time = currenttime,
                                      hostname=server)
            session.add(pstat)
            currenttime += datetime.timedelta(hours = 2)

    session.flush()
    session.commit()
    while currenttime <= enddate:
        for server in ["server1", "server2"]:
            pstat = models.PushStatus(time = currenttime,
                                      hostname=server)
            session.add(pstat)
            currenttime += datetime.timedelta(hours = 2)
  

    #Add readings / nodestates every two hours for two weeks 
    #But stop 3 days ago
    currenttime = startdate
    seq_num = 1
    while currenttime <= cutdate:
        for nid in allnodes:
            thereading = models.Reading(time = currenttime, 
                                        nodeId = nid, 
                                        typeId = 0, 
                                        value = 0)
            
            thestate = models.NodeState(time = currenttime,
                                        nodeId = nid,
                                        seq_num = seq_num)
        
            session.add(thereading)
            session.add(thestate)
        session.flush()
        currenttime = currenttime + datetime.timedelta(hours=2)
        seq_num += 1
        
    session.flush()
    session.commit()

    logging.debug("ALL NODES {0}".format(allnodes))
    #And then for all but the nodes assocated with house 1
    while currenttime <= enddate:
        for nid in allnodes[2:]:
            thereading = models.Reading(time = currenttime, 
                                        nodeId = nid, 
                                        typeId = 0, 
                                        value = 0)
            
            thestate = models.NodeState(time = currenttime,
                                        nodeId = nid,
                                        seq_num = seq_num)

            session.add(thereading)
            session.add(thestate)
        session.flush()
        currenttime = currenttime + datetime.timedelta(hours=2)
        seq_num += 1

    session.flush()
    session.commit()
        

    #STUFF FOR PUSLE COUNT
    currenttime = startdate
    pcount = 0

    qry = session.query(models.SensorType).filter_by(name="Gas Pulse Count")
    gas_sensor = qry.first()

    while currenttime <= cutdate:
        #Let node 10, 11 work
        thereading = models.Reading(time=currenttime,
                                     nodeId = 20,
                                     typeId = gas_sensor.id,
                                     value = pcount)
        session.add(thereading)
        thereading = models.Reading(time=currenttime,
                                     nodeId = 21,
                                     typeId = gas_sensor.id,
                                     value = pcount)

        session.add(thereading)
        pcount += 1
        currenttime += datetime.timedelta(hours=2)

    while currenttime <= enddate:
        thereading = models.Reading(time=currenttime,
                                     nodeId = 20,
                                     typeId = gas_sensor.id,
                                     value = pcount)
        session.add(thereading)
        thereading = models.Reading(time=currenttime,
                                     nodeId = 21,
                                     typeId = gas_sensor.id,
                                     value = 100)

        session.add(thereading)
        pcount += 1
        currenttime += datetime.timedelta(hours=2)
        
    session.flush()
    session.commit()
    
