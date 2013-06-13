"""
Class to compare dictionary objects.

Allows comparison of two dictionary objects to identify

  *  Added Items,  Items with no key in the second dictionary
  *  Deleted Items,  Items that are in the second dictionary, but not the first
  *  Changed Items, Where the same key returns a differnt item.

.. codeauthor Daniel Goldsmith <djgoldsmith@googlemail.com>
.. version:: 0.0.2

.. note::

    This code relies on the __eq__ method(s) of objects in the dictionary being
    defined, to make comparisons between items.  If undefined, then there are
    no guarantees on the results of the comparison.
"""

__version__ = "0.0.2"

class DictDiff(object):
    """
    Check two dictionarys and calculate differences between them.
    """
    def __init__(self, mine, other):
        """
        Create a diff dict object.

        ..param mine::  The base dictionary
        ..param other:: Dictionary to compare to
        """

        self.mine, self.other = mine, other
        #Set of keys in each dict
        self.set_mine = set(mine.keys())
        self.set_other = set(other.keys())
        #Intersection between keys
        self.intersect = self.set_mine.intersection(self.set_other)

    def added(self):
        """Find items added to the second dictionary.

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
        """Return items that have changed between dictionarys

        :return: Set of items where the key,value pairs differ.
        """
        changed = [x for x in self.intersect if self.other[x] != self.mine[x]]
        return set(changed)

    def unchanged(self):
        """Return items that are the same between dictionarys

        :return: Set of items where the key,value pairs are the same
        """
        unchanged = [x for x in self.intersect if self.other[x] == self.mine[x]]
        return set(unchanged)
