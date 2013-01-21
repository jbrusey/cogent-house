#import unittest

class Bitset(object):
    @staticmethod
    def fromstring(s):
        return Bitset(value=[int(i) for i in s.split(',')])

    def __init__(self, size=0, value=None):
        if value is not None:
            self.a = value
        else:
            self.a = [0 for i in range((size + 7)/8)]

    def size(self):
        return len(self.a)

    def __str__(self):
        return ','.join([str(i) for i in self.a])

    def __repr__(self):
        return 'Bitset(' + str(self) + ')'
    
    def toString(self):
        s = ''
        for i in self.a:
            s += chr(i)
        return s

    def __getitem__(self, i):
        return (self.a[i / 8] & (1 << (i % 8))) != 0    

    def __setitem__(self, i, v):
        if v:
            self.a[i / 8] |= (1 << (i % 8))
        else:
            self.a[i / 8] &= ~(1 << (i % 8))
