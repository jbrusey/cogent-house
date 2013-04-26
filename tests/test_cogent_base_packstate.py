import unittest

from cogent.node import Packets
from cogent.base.packstate import PackState
from cogent.base.model import Bitset

class Msg(object):
    def __init__(self, d):
        b = Bitset(size=Packets.SC_SIZE)
        for i in d.keys():
            b[i] = True
        self.mask = b.a
        self.p = []
        for i in sorted(d.keys()):
            self.p.append(d[i])

    def get_packed_state_mask(self):
        return self.mask

    def totalSizeBits_packed_state_mask(self):
        return len(self.mask) * 8

    def getElement_packed_state(self, i):
        return self.p[i]

class TestPackState(unittest.TestCase):
    def test___getitem__(self):
        pack_state = PackState({6:3.0, 23:1.0})
        self.assertEqual(1.0, pack_state[23])

    def test___init__(self):
        pack_state = PackState({6:3.0})
        self.assertEqual({6:3.0}, pack_state.d)

    def test___repr__(self):
        pack_state = PackState({5:1.1})
        self.assertEqual("PackState({5: 1.1})", repr(pack_state))

    def test___str__(self):
        pack_state = PackState({5:1.1})
        self.assertEqual('{5: 1.1}', str(pack_state))

    def test_from_message(self):
        msg = Msg({5:1.1, 23:2.0})
        pack_state = PackState.from_message(msg)
        self.assertEqual('PackState({5: 1.1, 23: 2.0})', repr(pack_state))

    def test_size(self):
        pack_state = PackState({6:3.0, 23:1.0})
        self.assertEqual(2, pack_state.size())

if __name__ == '__main__':
    unittest.main()
