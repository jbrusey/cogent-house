from cogent.node import Packets
from cogent.base.model import Bitset

class PackState(object):
    """ simplified version of the packstate object that supports
    decoding it from a state msg structure
    """
    
    @staticmethod
    def from_message(msg):
        """ static method for generating a PackState object from the state msg
        """
        mask = Bitset(value=msg.get_packed_state_mask())
        d = dict()
        j = 0
        for i in range(msg.totalSizeBits_packed_state_mask()):
            if mask[i]:
                if j >= Packets.SC_PACKED_SIZE:
                    raise Error("too many values stuffed into packed state")
                d[i] = msg.getElement_packed_state(j)
                j = j + 1

        return PackState(d)

    def __init__(self, map):
        self.d = map

    def size(self):
        return len(self.d)

    def __str__(self):
        return str(self.d)

    def __repr__(self):
        return 'PackState(' + str(self) + ')'
    
    def __getitem__(self, i):
        return self.d[i]
    
