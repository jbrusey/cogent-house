"""
Testing for the Diff Dict.
"""



#from datetime import datetime
import datetime

#Python Module Imports
import sqlalchemy.exc


import json
#import cogentviewer.models as models
import cogentviewer.tests.base as base

import cogentviewer.models as models
import cogentviewer.models.dictdiff as dictdiff

class DiffTest(base.BaseTestCase):
    def testunchanged(self):
        """Test the Unchanged Method

        Test that we dont have any items reported as the same
        """

        dict1 = {1:1,2:2,3:3,4:"foo",5:"bar"}
        dict2 = {1:1,2:2,3:3,4:"foo",5:"bar"}

        dd = dictdiff.DictDiff(dict1,dict2)
        added = dd.added()
        removed = dd.removed()
        changed = dd.changed()
        unchanged = dd.unchanged()

        #So nothing should have changed:
        expected = set(dict1.keys())
        self.assertEqual(unchanged,expected)

        emptySet = set([])
        self.assertEqual(added,emptySet)
        self.assertEqual(removed,emptySet)
        self.assertEqual(changed,emptySet)


    def testchanged(self):
        """
        Test the changed method

        Test that we dont have any items reported as the same

        Items with a different 'value' are classed as changed        
        This should only show changed items, no added or removed
        """


        #Change keys 2,4 
        dict1 = {1:1,2:2,3:3,4:"foo",5:"bar"}
        dict2 = {1:1,2:3,3:3,4:"bar",5:"bar"}

        dd = dictdiff.DictDiff(dict1,dict2)
        added = dd.added()
        removed = dd.removed()
        changed = dd.changed()
        unchanged = dd.unchanged()

        #So nothing should have changed:
        #expected = set(dict1.keys())
        unchangedSet = set([1,3,5])
        changed = set([2,4])
        emptyset = set([])

        
        self.assertEqual(added,emptyset)
        self.assertEqual(removed,emptyset)
        self.assertEqual(changed,changed)
        self.assertEqual(unchanged,unchangedSet)

    def testAdded(self):
        """
        Test the Added method

        An Item is added if a new <key>,<value> pair is in the dict
        """

        dict1 = {1:1,2:2,3:3,4:"foo",5:"bar"}
        dict2 = {1:1,2:2,3:3,4:"foo",5:"bar",6:"^_^"}

        dd = dictdiff.DictDiff(dict1,dict2)
        added = dd.added()
        removed = dd.removed()
        changed = dd.changed()
        unchanged = dd.unchanged()

        # Nothing should have changed
        addedset = set([6])
        emptyset = set([])
        unchangedset = set([1,2,3,4,5])
        
        
        self.assertEqual(added,addedset)
        self.assertEqual(removed,emptyset)
        self.assertEqual(changed,emptyset)
        self.assertEqual(unchanged,unchangedset)


    def testRemoved(self):
        """
        Test the Removed Method
        """

        dict1 = {1:1,2:2,3:3,4:"foo",5:"bar",6:"^_^"}
        dict2 = {1:1,2:2,3:3,4:"foo",5:"bar"}


        dd = dictdiff.DictDiff(dict1,dict2)
        added = dd.added()
        removed = dd.removed()
        changed = dd.changed()
        unchanged = dd.unchanged()

        #So nothing should have changed:
        removedset = set([6])
        emptyset = set([])
        unchangedset = set([1,2,3,4,5])
        
        self.assertEqual(added,emptyset)
        self.assertEqual(removed,removedset)
        self.assertEqual(changed,emptyset)
        self.assertEqual(unchanged,unchangedset)
        
    


#Fake Class to test the "Classy" version of the Dict
class FakeItem(object):
    def __init__(self,var1,var2):
        self.var1 = var1
        self.var2 = var2


    def __eq__(self,other):
        return self.var1 == other.var1 and self.var2 == other.var2

    def __ne__(self,other):
        return not(self.var1 == other.var1 and self.var2 == other.var2)


class ClassyDiffTest(base.BaseTestCase):
    """Test with clases"""

    def testunchanged(self):
        """Test the Unchanged Method

        Test that we dont have any items reported as the same
        """

        obj1 = FakeItem(1,"Hello")
        obj2 = FakeItem(2,"World")

        dict1 = {1:obj1,"2":obj2}
        dict2 = {1:obj1,"2":obj2}

        dd = dictdiff.DictDiff(dict1,dict2)
        added = dd.added()
        removed = dd.removed()
        changed = dd.changed()
        unchanged = dd.unchanged()

        #So nothing should have changed:
        expected = set([1,"2"])
        self.assertEqual(unchanged,expected)

        emptySet = set([])
        self.assertEqual(added,emptySet)
        self.assertEqual(removed,emptySet)
        self.assertEqual(changed,emptySet)

    def testchanged(self):
        """
        Test the changed method

        Test that we dont have any items reported as the same

        Items with a different 'value' are classed as changed        
        This should only show changed items, no added or removed
        """

        obj1 = FakeItem(1,"Foo")
        obj2 = FakeItem(1,"Foo")  #Same but differnt "Object"
        obj3 = FakeItem(2,"Foo")  #Different Element 1
        obj4 = FakeItem(1,"Bar")  #Different Text Element

        dict1 = {1:obj1,2:obj1,3:obj1,4:obj1}
        dict2 = {1:obj1,2:obj2,3:obj3,4:obj4}

        dd = dictdiff.DictDiff(dict1,dict2)
        added = dd.added()
        removed = dd.removed()
        changed = dd.changed()
        unchanged = dd.unchanged()

        unchangedSet = set([1,2])
        changedSet = set([3,4])
        emptySet = set([])
       
        self.assertEqual(added,emptySet)
        self.assertEqual(removed,emptySet)
        self.assertEqual(changed,changedSet)
        self.assertEqual(unchanged,unchangedSet)



    def testAdded(self):
        """
        Test the Added method

        An Item is added if a new <key>,<value> pair is in the dict
        """
        obj1 = FakeItem(1,"Foo")
        obj2 = FakeItem(2,"Bar")  #Same but differnt "Object"
        obj3 = FakeItem(3,"Baz")  #Different Element 1

        dict1 = {1:obj1,2:obj2}
        dict2 = {1:obj1,2:obj2,3:obj3}
        

        dd = dictdiff.DictDiff(dict1,dict2)
        added = dd.added()
        removed = dd.removed()
        changed = dd.changed()
        unchanged = dd.unchanged()

        addedset = set([3])
        emptyset = set([])
        unchangedset = set([1,2])
        
        self.assertEqual(added,addedset)
        self.assertEqual(removed,emptyset)
        self.assertEqual(changed,emptyset)
        self.assertEqual(unchanged,unchangedset)


    def testRemoved(self):
        """
        Test the Removed Method
        """
        obj1 = FakeItem(1,"Foo")
        obj2 = FakeItem(2,"Bar")  #Same but differnt "Object"
        obj3 = FakeItem(3,"Baz")  #Different Element 1

        dict1 = {1:obj1,2:obj2,3:obj3}
        dict2 = {1:obj1,2:obj2}
        

        dd = dictdiff.DictDiff(dict1,dict2)
        added = dd.added()
        removed = dd.removed()
        changed = dd.changed()
        unchanged = dd.unchanged()

        removedset = set([3])
        emptyset = set([])
        unchangedset = set([1,2])
        
        self.assertEqual(added,emptyset)
        self.assertEqual(removed,removedset)
        self.assertEqual(changed,emptyset)
        self.assertEqual(unchanged,unchangedset)
       

    #     dd = dictdiff.DictDiff(dict1,dict2)
    #     added = dd.added()
    #     removed = dd.removed()
    #     changed = dd.changed()
    #     unchanged = dd.unchanged()

    #     #So nothing should have changed:
    #     removedset = set([6])
    #     emptyset = set([])
    #     unchangedset = set([1,2,3,4,5])
        
    #     self.assertEqual(added,emptyset)
    #     self.assertEqual(removed,removedset)
    #     self.assertEqual(changed,emptyset)
    #     self.assertEqual(unchanged,unchangedset)
        
    
