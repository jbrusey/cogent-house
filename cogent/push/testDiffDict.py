import unittest
import cogent
import cogent.base.model as models


import RestPusher


class testDiffDict(unittest.TestCase):
    """Test the Diff Dict functions work as expected"""

    def testEqual(self):
        """Compare to dictionarys that are the same"""
        firstdict = {1:1,2:2,3:3}
        seconddict = {1:1,2:2,3:3}

        dd = RestPusher.DictDiff(firstdict,seconddict)

        added = dd.added()
        removed = dd.removed()
        changed = dd.changed()
        unchanged = dd.unchanged()

        emptySet = set()
        self.assertEqual(added, emptySet)
        self.assertEqual(removed, emptySet)
        self.assertEqual(changed, emptySet)

        
    def testAdded(self):
        """Added should give us items added to the FIRST set"""
        firstdict = {1:1,2:2,3:3,4:4}
        seconddict = {1:1,2:2,3:3}

        dd = RestPusher.DictDiff(firstdict,seconddict)

        added = dd.added()
        removed = dd.removed()
        changed = dd.changed()
        unchanged = dd.unchanged()

        emptySet = set()
        testSet = set([4])

        self.assertEqual(added, testSet)
        self.assertEqual(removed, emptySet)
        self.assertEqual(changed, emptySet)


    def testRemoved(self):
        """Removed should be items in the second set that are not in the first"""
        firstdict = {1:1,2:2,3:3}
        seconddict = {1:1,2:2,3:3,4:4}

        dd = RestPusher.DictDiff(firstdict,seconddict)

        added = dd.added()
        removed = dd.removed()
        changed = dd.changed()
        unchanged = dd.unchanged()

        emptySet = set()
        testSet = set([4])

        self.assertEqual(added, emptySet)
        self.assertEqual(removed, testSet)
        self.assertEqual(changed, emptySet)


    def testChanged(self):
        """Items whose value differes between keys"""
        firstdict = {1:1,2:2,3:3,4:5}
        seconddict = {1:1,2:2,3:3,4:4}

        dd = RestPusher.DictDiff(firstdict,seconddict)

        added = dd.added()
        removed = dd.removed()
        changed = dd.changed()
        unchanged = dd.unchanged()

        emptySet = set()
        testSet = set([4])

        self.assertEqual(added, emptySet)
        self.assertEqual(removed, emptySet)
        self.assertEqual(changed, testSet)        


class testDiffDictClass(unittest.TestCase):
    """Test the Diff Dict functions work as expected when we chuck model Classes into the mix"""


    def testEqual(self):

        modelOne = models.SensorType(id=1,name="foo",units="Co2")
        modelTwo = models.RoomType(id=1,name="Bedroom")
        modelThree = models.SensorType(id=2,name="bar")
        modelFour = models.RoomType(id=2,name="Bathroom")

        firstDict = {1: modelOne,
                     2: modelTwo,
                     3: modelThree,
                     4: modelFour}

        secondDict = {1: modelOne,
                      2: modelTwo,
                      3: modelThree,
                      4: modelFour}
        
        dd = RestPusher.DictDiff(firstDict,secondDict)
        added = dd.added()
        removed = dd.removed()
        changed = dd.changed()
        unchanged = dd.unchanged()

        emptySet = set()
        self.assertEqual(added, emptySet)
        self.assertEqual(removed, emptySet)
        self.assertEqual(changed, emptySet)
        
            
    def testAdded(self):
        """Added should give us items added to the FIRST set"""

        modelOne = models.SensorType(id=1,name="foo",units="Co2")
        modelTwo = models.RoomType(id=1,name="Bedroom")
        modelThree = models.SensorType(id=2,name="bar")
        modelFour = models.RoomType(id=2,name="Bathroom")

        firstDict = {1: modelOne,
                     2: modelTwo,
                     3: modelThree,
                     4: modelFour}

        secondDict = {1: modelOne,
                      2: modelTwo,
                      3: modelThree}


        dd = RestPusher.DictDiff(firstDict,secondDict)

        added = dd.added()
        removed = dd.removed()
        changed = dd.changed()
        unchanged = dd.unchanged()

        emptySet = set()
        testSet = set([4])

        self.assertEqual(added, testSet)
        self.assertEqual(removed, emptySet)
        self.assertEqual(changed, emptySet)


    def testRemoved(self):
        """Removed should be items in the second set that are not in the first"""

        modelOne = models.SensorType(id=1,name="foo",units="Co2")
        modelTwo = models.RoomType(id=1,name="Bedroom")
        modelThree = models.SensorType(id=2,name="bar")
        modelFour = models.RoomType(id=2,name="Bathroom")

        firstDict = {1: modelOne,
                     2: modelTwo,
                     3: modelThree,
                     }

        secondDict = {1: modelOne,
                      2: modelTwo,
                      3: modelThree,
                      4: modelFour}


        dd = RestPusher.DictDiff(firstDict,secondDict)

        added = dd.added()
        removed = dd.removed()
        changed = dd.changed()
        unchanged = dd.unchanged()

        emptySet = set()
        testSet = set([4])

        self.assertEqual(added, emptySet)
        self.assertEqual(removed, testSet)
        self.assertEqual(changed, emptySet)


    def testChanged(self):
        """Items whose value differes between keys"""
        modelOne = models.SensorType(id=1,name="foo",units="Co2")
        modelTwo = models.RoomType(id=1,name="Bedroom")
        modelThree = models.SensorType(id=2,name="bar")
        modelFour = models.RoomType(id=2,name="Bathroom")

        firstDict = {1: modelOne,
                     2: modelTwo,
                     3: modelThree,
                     4: modelFour}

        secondDict = {1: modelOne,
                      2: modelTwo,
                      3: modelThree,
                      4: modelThree}


        dd = RestPusher.DictDiff(firstDict,secondDict)

        added = dd.added()
        removed = dd.removed()
        changed = dd.changed()
        unchanged = dd.unchanged()

        emptySet = set()
        testSet = set([4])

        self.assertEqual(added, emptySet)
        self.assertEqual(removed, emptySet)
        self.assertEqual(changed, testSet)   


    def testChangedObject(self):
        """Items whose value differes between keys"""
        modelOne = models.SensorType(id=1,name="foo",units="Co2")
        modelTwo = models.RoomType(id=1,name="Bedroom")
        modelThree = models.SensorType(id=2,name="bar")
        modelFour = models.RoomType(id=2,name="Bathroom")
        modelFive = models.RoomType(id=1,name="Bathroom")

        firstDict = {1: modelOne,
                     2: modelTwo,
                     3: modelThree,
                     4: modelFour}

        secondDict = {1: modelOne,
                      2: modelTwo,
                      3: modelThree,
                      4: modelFive}


        dd = RestPusher.DictDiff(firstDict,secondDict)

        added = dd.added()
        removed = dd.removed()
        changed = dd.changed()
        unchanged = dd.unchanged()

        emptySet = set()
        testSet = set([4])

        self.assertEqual(added, emptySet)
        self.assertEqual(removed, emptySet)
        self.assertEqual(changed, testSet)   
        

