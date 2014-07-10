#from pyramid import testing

import pandas
import datetime

#from cogentviewer.views import homepage
from cogentviewer.views import export
import base

#Lookups for pandas indexes
LOC1 = "Node 837: Master Bedroom Temperature"
LOC2 = "Node 838: Bathroom Temperature"

class TestExport(base.FunctionalTest):
    #Makes use of the teting database to exammine the export script functionality

    def test_fetchall(self):
        """Fetch data from a house"""
        result = export.processExport(houseId=1)
        #We should have 2 locations * 1 sensor * 10 days of data here
        # 2 * 1 * (288 * 10) == 5670
        #print result.shape

        #result.to_csv("temp.csv")
        #Do we get the right object
        self.assertEqual(type(result), pandas.DataFrame)
        #And is it the right size
        self.assertEqual(result.shape, (2880, 2)) #So 2880 samples from two sensors
        #And the right range of data
        self.assertEqual(result.index[0], datetime.datetime(2013, 01, 01))
        self.assertEqual(result.index[-1], datetime.datetime(2013, 01, 10, 23, 55))

    def test_fetchlocation(self):
        """Fetch data from a given location"""
        result = export.processExport(houseId=1,
                                      locationIds = [1,],
                                      )

        self.assertEqual(result.shape, (2880, 1))
        self.assertEqual(result.columns[0], LOC1)

        result = export.processExport(houseId=1,
                                      locationIds = [2,],
                                      )

        self.assertEqual(result.shape, (2880, 1))
        self.assertEqual(result.columns[0], LOC2)


    def test_typeids(self):
        """Fetch by a given type"""
        result = export.processExport(houseId=1,
                                      locationIds = [1,],
                                      typeIds = [0],
                                      )

        self.assertEqual(result.shape, (2880, 1))

        #Without a location
        result = export.processExport(houseId=1,
                                      typeIds = [0],
                                      )

        self.assertEqual(result.shape, (2880, 2))

        result = export.processExport(houseId=1,
                                      locationIds = [1,],
                                      typeIds = [2],
                                      )

        #We should get an emppty object here
        self.assertEqual(result, {})


    def test_dates(self):
        """What about if date ranges are given"""
        result = export.processExport(houseId=1,
                                      startDate = datetime.datetime(2013, 01, 06) #5 Days
                                      )

        self.assertEqual(result.shape, (1440, 2))
        self.assertEqual(result.index[0], datetime.datetime(2013, 01, 06))
        self.assertEqual(result.index[-1], datetime.datetime(2013, 01, 10, 23, 55))


        #Stop at 00:00 on the 5th
        result = export.processExport(houseId=1,
                                      endDate = datetime.datetime(2013, 01, 05, 23, 55) #5 Days
                                      )

        self.assertEqual(result.shape, (1440, 2))
        self.assertEqual(result.index[0], datetime.datetime(2013, 01, 01))
        self.assertEqual(result.index[-1], datetime.datetime(2013, 01, 05, 23, 55))


    def test_aggregate(self):
        """Does aggregation work as expected"""

        #10 Minute sampleing
        result = export.processExport(houseId=1,
                                      aggregate="10Min")

        self.assertEqual(result.shape, (1440, 2))
        #And the second sample should be 10 minutes in
        self.assertEqual(result.index[1], datetime.datetime(2013, 01, 01, 0, 10, 00))

        #1/2 hourly
        result = export.processExport(houseId=1,
                                      aggregate="30Min")

        #2 * 24 * 10 = 480
        self.assertEqual(result.shape, (480, 2))
        #And the second sample should be 10 minutes in
        self.assertEqual(result.index[1], datetime.datetime(2013, 01, 01, 0, 30, 00))

        #Hourly
        result = export.processExport(houseId=1,
                                      aggregate="1H")

        self.assertEqual(result.shape, (240, 2))
        #And the second sample should be 10 minutes in
        self.assertEqual(result.index[1], datetime.datetime(2013, 01, 01, 1, 00, 00))


        #daily
        result = export.processExport(houseId=1,
                                      aggregate="1D")

        self.assertEqual(result.shape, (10, 2))
        #And the second sample should be 10 minutes in
        self.assertEqual(result.index[1], datetime.datetime(2013, 01, 02, 0, 00, 00))

    def test_aggregateby(self):
        """Cqn we add summary statistics?"""
        result = export.processExport(houseId=1,
                                      aggregate="1D",
                                      aggregateby=["min"])

        #So this will just show the minimum value
        self.assertEqual(result.shape, (10, 2))



        result = export.processExport(houseId=1,
                                      aggregate="1D",
                                      aggregateby=["min","mean","max"])

        print result.head()
        #So this will have 3 readings for each location (6 in total()
        self.assertEqual(result.shape, (10, 6))
        #And the second sample should be 10 minutes in
        #self.assertEqual(result.index[1], datetime.datetime(2013, 01, 01, 1, 00, 00))
