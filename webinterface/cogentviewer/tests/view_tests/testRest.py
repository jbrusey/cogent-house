"""
Test REST interface functionality
"""

import datetime
import unittest2 as unittest

from cogentviewer.views import homepage
import cogentviewer.tests.base as base
import cogentviewer.models as models

NAVBAR = homepage.NAVBAR


class RestTest(base.FunctionalTest):
    def test_get_deployment(self):
        """Test our get functionality for Deployments"""
        theqry = self.session.query(models.Deployment)
        qryresult = [x.dict() for x in theqry]
        res = self.testapp.get("/rest/deployment/")
        self.assertEqual(res.json, qryresult)

        #And with caplitalisation
        res = self.testapp.get("/rest/Deployment/")
        self.assertEqual(res.json, qryresult)

    def test_get_house(self):
        """Test our get functionality for houses"""
        theqry = self.session.query(models.House)
        qryresult = [x.dict() for x in theqry]
        res = self.testapp.get("/rest/house/")
        self.assertEqual(res.json, qryresult)

        #Capitals
        res = self.testapp.get("/rest/House/")
        self.assertEqual(res.json, qryresult)

    def test_get_room(self):
        """Test our get functionality for rooms"""
        theqry = self.session.query(models.Room)
        qryresult = [x.dict() for x in theqry]
        res = self.testapp.get("/rest/room/")
        self.assertEqual(res.json, qryresult)

    def test_get_node(self):
        """Test our get functionality for nodes"""
        theqry = self.session.query(models.Node)
        qryresult = [x.dict() for x in theqry]
        res = self.testapp.get("/rest/node/")
        self.assertEqual(res.json, qryresult)

    def test_get_roomtype(self):
        """Test our get functionality for roomtypes"""
        theqry = self.session.query(models.RoomType)
        qryresult = [x.dict() for x in theqry]
        res = self.testapp.get("/rest/roomtype/")
        self.assertEqual(res.json, qryresult)

    def test_get_location(self):
        """Test our get functionality for locations"""
        theqry = self.session.query(models.Location)
        qryresult = [x.dict() for x in theqry]
        res = self.testapp.get("/rest/location/")
        self.assertEqual(res.json, qryresult)

    def test_get_sensortype(self):
        """Test our get functionality for sensortypes"""
        theqry = self.session.query(models.SensorType)
        qryresult = [x.dict() for x in theqry]
        res = self.testapp.get("/rest/sensortype/")
        self.assertEqual(res.json, qryresult)


    def test_get_ids(self):
        """does requesting objects with Ids work correctly"""
        theqry = self.session.query(models.Room).filter_by(id=1).first()
        res = self.testapp.get("/rest/room/1")
        #Dont forget all REST will return as list
        self.assertEqual(res.json, [theqry.dict()])

        theqry = self.session.query(models.Room).filter_by(id=4).first()
        res = self.testapp.get("/rest/room/4")
        self.assertEqual(res.json, [theqry.dict()])

        #And test against a static version of what I expect
        roomdict = {"id":4,
                    "__table__":"Room",
                    "roomTypeId":2,
                    "name":"Living Room"}
        self.assertEqual(res.json, [roomdict])


        #And lets try with another object type
        theqry = self.session.query(models.SensorType).filter_by(id=5).first()
        res = self.testapp.get("/rest/sensortype/5")
        self.assertEqual(res.json, [theqry.dict()])


    def test_get_ids_missing(self):
        """What happens if we ask for an Id that doesnt exist"""
        res = self.testapp.get("/rest/deployment/5")
        #self.assertEqual(res.status_int, 404)
        self.assertFalse(res.json)

        res = self.testapp.get("/rest/house/5")
        self.assertFalse(res.json)

    def test_get_reading(self):
        """Ask for all the readings in the database"""
        res = self.testapp.get("/rest/reading/")

        #Should be a list and have 2*288*10
        #And also (288/2)*10 = 1440  (Every Over)
        #And 9*24*10 = 1920 (Every 3rd missing)
        #
        thedata = res.json
        self.assertEqual(len(thedata), 9120)

        #First and last reading dates
        first_date = thedata[0]["time"]
        first_iso = datetime.datetime(2013, 01, 01).isoformat()
        last_date = thedata[-1]["time"]
        last_iso = datetime.datetime(2013, 01, 10, 23, 55).isoformat()
        self.assertEqual(first_date, first_iso)
        self.assertEqual(last_date, last_iso)

    def test_ranges(self):
        """If getting readings works correctly we should be able
        to get ranges too"""

        #Try with a simple room object first
        res = self.testapp.get("/rest/room/", headers={"Range":"items=0-5"})
        thedata = res.json
        self.assertEqual(len(thedata), 5)

        #Then we move onto more complex readings and fetch the first day
        # (288 *2 <sensors>)
        res = self.testapp.get("/rest/reading/",
                               headers={"Range":"items=0-576"})
        thedata = res.json
        self.assertEqual(len(thedata), 576)
        first_date = thedata[0]["time"]
        first_iso = datetime.datetime(2013, 01, 01).isoformat()
        self.assertEqual(first_date, first_iso)

        #What about the second day
        res = self.testapp.get("/rest/reading/",
                               headers={"Range":"items=576-1152"})
        thedata = res.json
        self.assertEqual(len(thedata), 576)

        #what about if a bad range string is used
        res = self.testapp.get("/rest/reading/",
                               headers={"Range":"item=0:576"})
        thedata = res.json
        self.assertEqual(len(thedata), 9120)

    def test_query_equals(self):
        """Test the query engine Equals function"""

        theqry = self.session.query(models.Room).filter_by(id=4).first()

        #Fetch by Id
        res = self.testapp.get("/rest/room/", {"id":4})
        self.assertEqual(res.json, [theqry.dict()])

        #Fetch by Name
        res = self.testapp.get("/rest/room/", {"name":"Living Room"})
        self.assertEqual(res.json, [theqry.dict()])

        #Fetch by room type
        res = self.testapp.get("/rest/room/", {"roomTypeId":3})
        self.assertEqual(len(res.json), 3)


        #Test Readings / Dates
        res = self.testapp.get("/rest/reading/",
                               {"time":datetime.datetime(2013,01,01)})

        self.assertEqual(len(res.json), 2)
        for item in res.json:
            self.assertEqual(item["time"],
                             datetime.datetime(2013,01,01).isoformat())


        #Test if multiple values work as expected
        res = self.testapp.get("/rest/reading/",
                               {"time":datetime.datetime(2013,01,02),
                                "nodeId":838},
                               )

        self.assertEqual(len(res.json), 1)
        self.assertEqual(res.json[0]["time"],
                         datetime.datetime(2013,01,02).isoformat())

        self.assertEqual(res.json[0]["nodeId"], 838)

        #Other types of datestring
        res = self.testapp.get("/rest/reading/",
                               {"time":"2013-01-02",
                                "nodeId":838},
                               )

        self.assertEqual(len(res.json), 1)
        self.assertEqual(res.json[0]["time"],
                         datetime.datetime(2013,01,02).isoformat())

        self.assertEqual(res.json[0]["nodeId"], 838)


    def test_query_greater(self):
        """Test Query Greater that / Greater equals"""
        res = self.testapp.get("/rest/room/",
                               {"id":"gt_6"})
        #Should return another 6 readings (ids 7-12 inclusibe)
        thedata = res.json
        self.assertEqual(len(thedata), 6)
        self.assertEqual(thedata[0]["id"], 7)
        self.assertEqual(thedata[0]["name"], "WC")

        res = self.testapp.get("/rest/room/",
                               {"id":"ge_6"})
        #Should return another 7 readings (ids 6-12 inclusibe)
        thedata = res.json
        self.assertEqual(len(thedata), 7)
        self.assertEqual(thedata[0]["id"], 6)
        self.assertEqual(thedata[0]["name"], "Bathroom")

        #And lets do the same with readings
        res = self.testapp.get("/rest/reading/",
                              { "time":"gt_2013-01-05"})

        #Remember that dates are converted to datetimes
        #So we actually get the next reading
        thedata = res.json
        self.assertEqual(thedata[0]["time"],
                         datetime.datetime(2013,01,05,00,05).isoformat())


        #And lets do the same with readings
        res = self.testapp.get("/rest/reading/",
                              { "time":"ge_2013-01-05"})
        #Days 6-10 of data
        thedata = res.json
        self.assertEqual(thedata[0]["time"],
                         datetime.datetime(2013,01,05).isoformat())


    def test_query_less(self):
        res = self.testapp.get("/rest/room/",
                               {"id":"lt_6"})
        #Should ids 1-5 inclusive
        thedata = res.json
        self.assertEqual(len(thedata), 5)
        self.assertEqual(thedata[-1]["id"], 5)
        self.assertEqual(thedata[-1]["name"], "Dining Room")

        res = self.testapp.get("/rest/room/",
                               {"id":"le_6"})
        #Should return another 6 readings (ids 1-6 inclusibe)
        thedata = res.json
        self.assertEqual(len(thedata), 6)
        self.assertEqual(thedata[-1]["id"], 6)
        self.assertEqual(thedata[-1]["name"], "Bathroom")

        #And lets do the same with readings
        res = self.testapp.get("/rest/reading/",
                              { "time":"lt_2013-01-05"})
        #Days 6-10 of data
        thedata = res.json
        self.assertEqual(thedata[-1]["time"],
                         datetime.datetime(2013,01,04,23,55).isoformat())


        #And lets do the same with readings
        res = self.testapp.get("/rest/reading/",
                              { "time":"le_2013-01-05"})
        #Days 6-10 of data
        thedata = res.json
        self.assertEqual(thedata[-1]["time"],
                         datetime.datetime(2013,01,05).isoformat())


    def test_query_combined(self):
        """Combined gt / lt queries"""

        #All data beteen the 4-6 (3 days)

        #Fake a multidict
        res = self.testapp.get("/rest/room/",
                               {"id":["ge_4","le_6"]},
                               )
        thedata = res.json
        self.assertEqual(len(thedata), 3)
        self.assertEqual(thedata[0]["name"], "Living Room")
        self.assertEqual(thedata[-1]["name"], "Bathroom")


        #Data between the 4th and 6th (ie all day 4th, all day 5th)
        res = self.testapp.get("/rest/reading/",
                               {"time": ["ge_2013-01-04",
                                         "lt_2013-01-06"]})
        thedata = res.json
        print
        print "="*40
        print len(thedata)
        print thedata[0]
        print thedata[-1]
        self.assertEqual(len(thedata), (576+144+192)*2)
        self.assertEqual(thedata[0]["time"],
                         datetime.datetime(2013, 01, 04).isoformat())
        self.assertEqual(thedata[-1]["time"],
                         datetime.datetime(2013, 01, 05, 23, 55).isoformat())


        res = self.testapp.get("/rest/reading/",
                               {"time": ["ge_2013-01-04",
                                         "lt_2013-01-06"],
                                "nodeId": 838})
        thedata = res.json
        self.assertEqual(len(thedata), (288*2))
        self.assertEqual(thedata[0]["time"],
                         datetime.datetime(2013, 01, 04).isoformat())
        self.assertEqual(thedata[-1]["time"],
                         datetime.datetime(2013, 01, 05, 23, 55).isoformat())

    def test_query_wildcard(self):
        pass

    def test_query_sort(self):
        """ Test Sorting Functionaltioy"""

        #Should sort decending on ID
        res = self.testapp.get("/rest/room/",
                               {"sort(-id)":None})
        thedata = res.json

        self.assertEqual(thedata[0]["id"], 12)
        self.assertEqual(thedata[-1]["id"], 1)

        #What about by Name (Decending)
        res = self.testapp.get("/rest/room/",
                               {"sort(-name)":None})
        thedata = res.json
        self.assertEqual(thedata[0]["name"], "WC")
        self.assertEqual(thedata[-1]["name"], "Bathroom")

        #(Ascending)
        res = self.testapp.get("/rest/room/",
                               {"sort(+name)":None})
        thedata = res.json
        self.assertEqual(thedata[0]["name"], "Bathroom")
        self.assertEqual(thedata[-1]["name"], "WC")


        res = self.testapp.get("/rest/room/",
                               {"sort(-roomTypeId)":None})
        thedata = res.json
        self.assertEqual(thedata[0]["name"], "Spare Room")
        self.assertEqual(thedata[1]["name"], "Utility Room")

        #And by a couple of things (a different sort order to above)
        res = self.testapp.get("/rest/room/",
                               {"sort(-roomTypeId,+name)":None})
        thedata = res.json
        self.assertEqual(thedata[0]["name"], "Hallway")
        self.assertEqual(thedata[2]["name"], "Upstairs Hallway")

    @unittest.skip
    def test_getversion(self):
        """Check REST supplies the correct versions"""
        res = self.testapp.get("/rest/version/")

        #Check against the version in setup.py
        import pkg_resources
        version = pkg_resources.require("cogent-viewer")[0].version
        self.assertEqual(res.json, version)

        #And check againstst a hardcoded version
        self.assertEqual(res.json, "0.4.3")

    def test_gethouserooms(self):
        """Does the houserooms function (called by export javascript)
        work correctly"""

        req = self.testapp.get("/rest/houserooms/1", {"id":1})
        jsonreq = req.json
        #There should be Master bedroom (1) and Bathroom (2)
        self.assertEqual(jsonreq, [{"id":1, "name":"Master Bedroom"},
                                   {"id":2, "name":"Bathroom"}])

        #And for something that doesnt exist
        req = self.testapp.get("/rest/houserooms/1", {"id":3})
        self.assertFalse(req.json)

    def test_lastSync(self):

        res = self.testapp.get("/rest/lastsync/")
        #Currently this should fail if we do not supply a house
        self.assertFalse(res.json)

        session = self.session

        res = self.testapp.get("/rest/lastsync/", {"house":"testing house"})
        #Final date will be
        finaldate = datetime.datetime(2013,01,10,23,55)
        self.assertEqual(res.json, finaldate.isoformat())

        #And a place that doesnt exist
        res = self.testapp.get("/rest/lastsync/", {"house":"testing house fail"})
        self.assertFalse(res.json)
