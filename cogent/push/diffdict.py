"""
Class to compare dictionary objects
"""


class DictDiff(object):
    """
    Check two dictionarys and calculate differences between them
    """
    def __init__(self,mine,other):
        self.mine, self.other = mine,other 
        #Set of keys in each dict
        self.set_mine = set(mine.keys())
        self.set_other = set(other.keys())
        #Intersection between keys
        self.intersect = self.set_mine.intersection(self.set_other)
    
    def added(self):
        """Find items added to the dictionary.

        This will return a set of items that are in "other", 
        that are not in "mine"

        :return: set of new items
        """
        return self.set_mine - self.intersect 


    def removed(self):
        """Return items that have been removed from the dictionary.
        Will return a set of items that are in "mine" but not in "other"
        :return: set of removed items
        """
        return self.set_other - self.intersect
   
    def changed(self):
        """Return items that have changed between dictionarys"""
        changed = [x for x in self.intersect if self.other[x] != self.mine[x]]
        #print changed
        return set(changed)

    def unchanged(self):
        """Return items that are the same between dictionarys"""
        unchanged = [x for x in self.intersect if self.other[x] == self.mine[x]]
        return set(unchanged)
        
