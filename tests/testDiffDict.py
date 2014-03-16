import unittest2 as unittest
# import cogent
# import cogent.base.model as models

# import cogent.push.dictdiff as dictdiff

class testDiffDict(unittest.TestCase):
    """Test the Diff Dict functions work as expected"""

    pass
#     def testEqual(self):
#         """Compare to dictionarys that are the same"""
#         firstdict = {1:1, 2:2, 3:3}
#         seconddict = {1:1, 2:2, 3:3}

#         dd = dictdiff.DictDiff(firstdict, seconddict)

#         added = dd.added()
#         removed = dd.removed()
#         changed = dd.changed()
#         unchanged = dd.unchanged()

#         emptySet = set()
#         self.assertEqual(added, emptySet)
#         self.assertEqual(removed, emptySet)
#         self.assertEqual(changed, emptySet)

        
#     def testAdded(self):
#         """Added should give us items added to the FIRST set"""
#         firstdict = {1:1, 2:2, 3:3, 4:4}
#         seconddict = {1:1, 2:2, 3:3}

#         dd = dictdiff.DictDiff(firstdict, seconddict)

#         added = dd.added()
#         removed = dd.removed()
#         changed = dd.changed()
#         unchanged = dd.unchanged()

#         emptySet = set()
#         testSet = set([4])

#         self.assertEqual(added, testSet)
#         self.assertEqual(removed, emptySet)
#         self.assertEqual(changed, emptySet)


#     def testRemoved(self):
#         """Removed should be items in the second set that are not in the first"""
#         firstdict = {1:1, 2:2, 3:3}
#         seconddict = {1:1, 2:2, 3:3, 4:4}

#         dd = dictdiff.DictDiff(firstdict, seconddict)

#         added = dd.added()
#         removed = dd.removed()
#         changed = dd.changed()
#         unchanged = dd.unchanged()

#         emptySet = set()
#         testSet = set([4])

#         self.assertEqual(added, emptySet)
#         self.assertEqual(removed, testSet)
#         self.assertEqual(changed, emptySet)


#     def testChanged(self):
#         """Items whose value differes between keys"""
#         firstdict = {1:1, 2:2, 3:3, 4:5}
#         seconddict = {1:1, 2:2, 3:3, 4:4}

#         dd = dictdiff.DictDiff(firstdict,seconddict)

#         added = dd.added()
#         removed = dd.removed()
#         changed = dd.changed()
#         unchanged = dd.unchanged()

#         emptySet = set()
#         testSet = set([4])

#         self.assertEqual(added, emptySet)
#         self.assertEqual(removed, emptySet)
#         self.assertEqual(changed, testSet)        



# class testDiffDictClass(unittest.TestCase):
#     """Test the Diff Dict functions work as expected when we chuck model Classes into the mix"""
#     def testEqual(self):

#         modelOne = models.SensorType(id=1, name="foo", units="Co2")
#         modelTwo = models.RoomType(id=1, name="Bedroom")
#         modelThree = models.SensorType(id=2, name="bar")
#         modelFour = models.RoomType(id=2, name="Bathroom")

#         firstDict = {1: modelOne,
#                      2: modelTwo,
#                      3: modelThree,
#                      4: modelFour}

#         secondDict = {1: modelOne,
#                       2: modelTwo,
#                       3: modelThree,
#                       4: modelFour}
        
#         dd = dictdiff.DictDiff(firstDict, secondDict)
#         added = dd.added()
#         removed = dd.removed()
#         changed = dd.changed()
#         unchanged = dd.unchanged()

#         emptySet = set()
#         self.assertEqual(added, emptySet)
#         self.assertEqual(removed, emptySet)
#         self.assertEqual(changed, emptySet)
        
            
#     def testAdded(self):
#         """Added should give us items added to the FIRST set"""

#         modelOne = models.SensorType(id=1, name="foo", units="Co2")
#         modelTwo = models.RoomType(id=1, name="Bedroom")
#         modelThree = models.SensorType(id=2, name="bar")
#         modelFour = models.RoomType(id=2, name="Bathroom")

#         firstDict = {1: modelOne,
#                      2: modelTwo,
#                      3: modelThree,
#                      4: modelFour}

#         secondDict = {1: modelOne,
#                       2: modelTwo,
#                       3: modelThree}


#         dd = dictdiff.DictDiff(firstDict, secondDict)

#         added = dd.added()
#         removed = dd.removed()
#         changed = dd.changed()
#         unchanged = dd.unchanged()

#         emptySet = set()
#         testSet = set([4])

#         self.assertEqual(added, testSet)
#         self.assertEqual(removed, emptySet)
#         self.assertEqual(changed, emptySet)


#     def testRemoved(self):
#         """Removed should be items in the second set that are not in the first"""

#         modelOne = models.SensorType(id=1, name="foo", units="Co2")
#         modelTwo = models.RoomType(id=1, name="Bedroom")
#         modelThree = models.SensorType(id=2, name="bar")
#         modelFour = models.RoomType(id=2, name="Bathroom")

#         firstDict = {1: modelOne,
#                      2: modelTwo,
#                      3: modelThree,
#                      }

#         secondDict = {1: modelOne,
#                       2: modelTwo,
#                       3: modelThree,
#                       4: modelFour}


#         dd = dictdiff.DictDiff(firstDict, secondDict)

#         added = dd.added()
#         removed = dd.removed()
#         changed = dd.changed()
#         unchanged = dd.unchanged()

#         emptySet = set()
#         testSet = set([4])

#         self.assertEqual(added, emptySet)
#         self.assertEqual(removed, testSet)
#         self.assertEqual(changed, emptySet)


#     def testChanged(self):
#         """Items whose value differes between keys"""
#         modelOne = models.SensorType(id=1, name="foo", units="Co2")
#         modelTwo = models.RoomType(id=1, name="Bedroom")
#         modelThree = models.SensorType(id=2, name="bar")
#         modelFour = models.RoomType(id=2, name="Bathroom")

#         firstDict = {1: modelOne,
#                      2: modelTwo,
#                      3: modelThree,
#                      4: modelFour}

#         secondDict = {1: modelOne,
#                       2: modelTwo,
#                       3: modelThree,
#                       4: modelThree}


#         dd = dictdiff.DictDiff(firstDict, secondDict)

#         added = dd.added()
#         removed = dd.removed()
#         changed = dd.changed()
#         unchanged = dd.unchanged()

#         emptySet = set()
#         testSet = set([4])

#         self.assertEqual(added, emptySet)
#         self.assertEqual(removed, emptySet)
#         self.assertEqual(changed, testSet)   


#     def testChangedObject(self):
#         """Items whose value differes between keys"""
#         modelOne = models.SensorType(id=1, name="foo", units="Co2")
#         modelTwo = models.RoomType(id=1, name="Bedroom")
#         modelThree = models.SensorType(id=2, name="bar")

#         #RoomType eqality is based on the name not Id
#         #Thus these two models should be the same
#         modelFour = models.RoomType(id=2, name="Bathroom")
#         modelFive = models.RoomType(id=1, name="Bathroom")

#         self.assertEqual(modelFour, modelFive)


#         #So for this first test we expect that there will be NO
#         #Unchanged items.
#         firstDict = {1: modelOne,
#                      2: modelTwo,
#                      3: modelThree,
#                      4: modelFour}

#         secondDict = {1: modelOne,
#                       2: modelTwo,
#                       3: modelThree,
#                       4: modelFive}


#         dd = dictdiff.DictDiff(firstDict, secondDict)

#         added = dd.added()
#         removed = dd.removed()
#         changed = dd.changed()
#         unchanged = dd.unchanged()

#         emptySet = set()
#         testSet = set([4])

#         self.assertEqual(added, emptySet)
#         self.assertEqual(removed, emptySet)
#         self.assertEqual(changed, emptySet)   

#         #However lets run that again when the objects do not come out
#         #Equal

#         modelFive = models.RoomType(id=1, name="BathroomA")
#         self.assertNotEqual(modelFour, modelFive)
        
#         firstDict = {1: modelOne,
#                      2: modelTwo,
#                      3: modelThree,
#                      4: modelFour}

#         secondDict = {1: modelOne,
#                       2: modelTwo,
#                       3: modelThree,
#                       4: modelFive}


#         dd = dictdiff.DictDiff(firstDict, secondDict)

#         added = dd.added()
#         removed = dd.removed()
#         changed = dd.changed()
#         unchanged = dd.unchanged()

#         emptySet = set()
#         testSet = set([4])

#         self.assertEqual(added, emptySet)
#         self.assertEqual(removed, emptySet)
#         self.assertEqual(changed, testSet)   


