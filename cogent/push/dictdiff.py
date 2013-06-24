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

Example Use
-------------

>>> basedict = {1:"foo", 2:"bar", 3:"baz"}
>>> otherdict = {1:"foo", 2:"bar", 3:"baz"}
>>> dd = DictDiff(basedict, otherdict)
>>> dd.added()
set([])
>>> dd.removed()
set([])
>>> dd.changed()
set([])
>>> dd.unchanged()
set([1, 2, 3])
>>> 


"""

__version__ = "0.0.2"

import logging
log = logging.getLogger("DiffDict")

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
        #log.debug("==== DiffDict Created ====")
        self.mine, self.other = mine, other
        #Set of keys in each dict
        self.set_mine = set(mine.keys())
        self.set_other = set(other.keys())
        #Intersection between keys
        self.intersect = self.set_mine.intersection(self.set_other)
        #log.debug("===SET Mine {0}".format(self.set_mine))
        #log.debug("===SET Other {0}".format(self.set_other))
        #log.debug("===Intersect {0}".format(self.intersect))

    def added(self):
        """Find items added to the base dictionary.

        This will return a set of keys for items that are in "mine",
        that are not in "other"

        :return: set of new items

        >>> basedict = {1:"foo", 2:"bar", 3:"baz"}
        >>> otherdict = {1:"foo", 2:"bar"}
        >>> dd = DictDiff(basedict,otherdict)
        >>> dd.added()
        set([3])


        """
        return self.set_mine - self.intersect


    def removed(self):
        """Return items that have been removed from the dictionary base dictionary.

        This will return a set of keys for items that are in "other",
        that are not in "mine"

        :return: set of removed keys for items

        >>> basedict = {1:"foo", 2:"bar"}
        >>> otherdict = {1:"foo", 2:"bar", 3:"baz"}
        >>> dd = DictDiff(basedict,otherdict)
        >>> dd.removed()
        set([3])
        """
        return self.set_other - self.intersect

    def changed(self):
        """Return items that have changed between dictionarys

        :return: Set of items where the key,value pairs differ.

        >>> basedict = {1:"foo", 2:"bar", 3:"baz"}
        >>> otherdict = {1:"foo", 2:"bar", 3:"bleh"}
        >>> dd = DictDiff(basedict,otherdict)

        >>> #Added will not show any values as the set of keys match
        >>> dd.added()
        set([])

        >>> # Neither will removed
        >>> dd.removed()
        set([])
        
        >>> #However Changed will show where the values have changed
        >>> dd.changed()
        set([3])


        """
        #Lets do this bit by bit:
        changed = []
        #for x in self.intersect:
        #    match = not self.other[x] == self.mine[x]
        #    log.debug("Compare {0} == {1} # {2}".format(self.other[x],self.mine[x],match))
        #    if match:
        #        changed.append(x)
        changed = [x for x in self.intersect if self.other[x] != self.mine[x]]
        #log.debug("CHANGED ==== {0}".format(changed))
        return set(changed)

    def unchanged(self):
        """Return items that are the same between dictionarys

        :return: Set of items where the key,value pairs are the same
        """
        unchanged = [x for x in self.intersect if self.other[x] == self.mine[x]]
        return set(unchanged)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
