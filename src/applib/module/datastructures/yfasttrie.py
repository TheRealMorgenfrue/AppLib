"""
An implementation of Willard's Y-Fast tries

This structure is able to store w-bit integers with O(log w) time searches,
additions, and removals.

D. E. Willard. Log-logarithmic worst-case range queries are possible in
  space Theta(n). Information Processing Letters, 17, 81-84. 1984.

Courtesy of https://opendatastructures.org/
"""

import random
from typing import Self
from numpy import _ConvertibleToInt

from .base import BaseSet
from .treap import Treap
from .xfasttrie import XFastTrie
from .utils import w


class STreap(Treap):
    """A Treap that implements the split/absorb functionality"""

    def split(self, x):
        """Remove all values <= x and return a STreap containing these values"""
        u = self._find_last(x)
        s = self._new_node(None)
        if u.right is self.nil:
            u.right = s
        else:
            u = u.right
            while u.left is not self.nil:
                u = u.left
            u.left = s
        s.parent = u
        s.p = -1
        self._bubble_up(s)
        self.r = s.right
        if self.r is not self.nil:
            self.r.parent = self.nil
        ret = STreap()
        ret.r = s.left
        if ret.r is not ret.nil:
            ret.r.parent = ret.nil
        return ret

    def absorb(self, t: Self):
        """Absorb the treap t (which must only contain smaller values)"""
        s = self._new_node(None)
        s.right = self.r
        if self.r is not self.nil:
            self.r.parent = s
        s.left = t.r
        if t.r is not t.nil:
            t.r.parent = s
        self.r = s
        t.r = t.nil
        self._trickle_down(s)
        self._splice(s)

    def size(self):
        """Raise an error because our implementation is only half-assed"""
        raise AttributeError(
            self.__class__.__name__ + "does not correctly maintain size()"
        )


class Pair(tuple):
    @property
    def t(self):
        return self[1]

    @property
    def x(self):
        return self[0]

    def __new__(cls, x, y=None):
        return super().__new__(cls, (x, y))

    def __int__(self):
        return int(self[0])


class YFastTrie(BaseSet):
    def __init__(self):
        """
        A trie is a specialized search tree particularly effective
        for tasks such as autocomplete and spell checking.

        This is an implementation of Willard's Y-Fast tries.
        This structure is able to store w-bit integers with O(log w) time searches,
        additions, and removals. It has a space complexity of O(n).

        D. E. Willard. Log-logarithmic worst-case range queries are possible in
        space Theta(n). Information Processing Letters, 17, 81-84. 1984.
        """
        super().__init__()
        self._initialize()

    def __iter__(self):
        # self._xft is a bunch of pairs
        for p in self._xft:
            # the one'th element of each pair is an STreap
            for x in p[1]:
                yield x

    def _initialize(self):
        self._xft = XFastTrie()
        self._xft.add(Pair((1 << w) - 1, STreap()))
        self._n = 0

    def add(self, x: _ConvertibleToInt) -> bool:
        ix = int(x)
        t = self._xft.find(Pair(ix))[1]
        if t.add(x):
            self._n += 1
            if random.randrange(w) == 0:
                t1 = t.split(x)
                self._xft.add(Pair(ix, t1))
            return True
        return False

    def find(self, x: _ConvertibleToInt) -> _ConvertibleToInt | None:
        return self._xft.find(Pair(int(x)))[1].find(x)

    def remove(self, x: _ConvertibleToInt) -> bool:
        ix = int(x)
        u = self._xft._find_node(ix)
        ret = u.x[1].remove(x)
        if ret:
            self._n -= 1
        if u.x[0] == ix and ix != (1 << w) - 1:
            t2 = u.next.x[1]
            t2.absorb(u.x[1])
            self._xft.remove(u.x)
        return ret

    def clear(self):
        self._initialize()
