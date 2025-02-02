"""
A skiplist implementation of the List interface

W. Pugh. Skip Lists: A probabilistic alternative to balanced trees.
  In Communications of the ACM, 33(6), pp. 668-676, June 1990.

W. Pugh. A skip list cookbook. CS-TR-2286.1, University of Maryland,
  College Park, 1990.

Courtesy of https://opendatastructures.org/
(Called SkiplistList)
"""

import random
from typing import Any, Iterable, override

import numpy

from .base import BaseList
from .utils import new_array


class Skiplist(BaseList):
    class Node(object):
        """A node in a skiplist"""

        def __init__(self, x, h):
            self.x = x
            self.next = new_array(h + 1)
            self.length = numpy.ones(h + 1, dtype=int)

        def height(self):
            return len(self.next) - 1

    def _new_node(self, x, h):
        return Skiplist.Node(x, h)

    def __init__(self, iterable: Iterable = []):
        """
        A skiplist is a probabilistic data structure made up of a sequence of singly-linked lists.
        It can get the best features of a sorted array (for fast searching) while maintaining a linked
        list-like structure that allows fast insertion, which is not possible with a static array.

        This implementation follows most of Python's list interface (incl. slicing and negative indexing).
        It allows O(log n) average time searches, additions, and removals.

        W. Pugh. Skip Lists: A probabilistic alternative to balanced trees.
        In Communications of the ACM, 33(6), pp. 668-676, June 1990.

        W. Pugh. A skip list cookbook. CS-TR-2286.1, University of Maryland,
        College Park, 1990.

        Parameters
        ----------
        iterable : Iterable, optional
            Add elements from `iterable` to the skiplist.
            By default `[]`.
        """
        super().__init__()
        self._initialize()
        self.extend(iterable)

    def _initialize(self):
        self._h = 0
        self._n = 0
        self._sentinel = self._new_node(None, 32)

    def __iter__(self):
        u = self._sentinel.next[0]
        while u is not None:
            yield u.x
            u = u.next[0]

    def __add(self, i, w):
        u = self._sentinel
        k = w.height()
        r = self._h
        j = -1
        while r >= 0:
            while u.next[r] is not None and j + u.length[r] < i:
                j += u.length[r]
                u = u.next[r]
            u.length[r] += 1
            if r <= k:
                w.next[r] = u.next[r]
                u.next[r] = w
                w.length[r] = u.length[r] - (i - j)
                u.length[r] = i - j
            r -= 1
        self._n += 1
        return u

    def _pick_height(self):
        z = random.getrandbits(32)
        k = 0
        while z & 1:
            k += 1
            z = z // 2
        return k

    def _find_pred(self, i):
        u = self._sentinel
        r = self._h
        j = -1
        while r >= 0:
            while u.next[r] is not None and j + u.length[r] < i:
                j += u.length[r]
                u = u.next[r]  # go right in list r
            r -= 1  # go down into list r-1
        return u

    def _get(self, i):
        if i < 0 or i > self._n - 1:
            raise IndexError()
        return self._find_pred(i).next[0].x

    def _set(self, i, x):
        if i < 0 or i > self._n - 1:
            raise IndexError()
        u = self._find_pred(i).next[0]
        y = u.x
        u.x = x
        return y

    def _add(self, i, x):
        if i < 0 or i > self._n:
            raise IndexError()
        w = self._new_node(x, self._pick_height())
        if w.height() > self._h:
            self._h = w.height()
        self.__add(i, w)

    def _remove(self, i) -> Any:
        if i < 0 or i > self._n - 1:
            raise IndexError()
        u = self._sentinel
        r = self._h
        j = -1
        while r >= 0:
            while u.next[r] is not None and j + u.length[r] < i:
                j += u.length[r]
                u = u.next[r]
            u.length[r] -= 1
            if j + u.length[r] + 1 == i and u.next[r] is not None:
                x = u.next[r].x
                u.length[r] += u.next[r].length[r]
                u.next[r] = u.next[r].next[r]
                if u == self._sentinel and u.next[r] is None:
                    self._h -= 1
            r -= 1
        self._n -= 1
        return x

    @override
    def clear(self) -> None:
        """ """
        self._initialize()
