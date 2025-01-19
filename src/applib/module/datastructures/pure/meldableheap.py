"""
An implementation of Gambin and Malinowsky's randomized meldable heaps

A. Gambin and A. Malinowski. Randomized meldable priority queues.
  Proceedings of the XXVth Seminar on Current Trends in Theory and Practice
  of Informatics (SOFSEM'98), pp. 344-349, 1998

Courtesy of https://opendatastructures.org/
"""

import random
from typing import Any, Iterable

from .base import BaseSet
from .binarytree import BinaryTree


def random_bit() -> bool:
    return random.getrandbits(1) == 0


class MeldableHeap(BinaryTree, BaseSet):
    class Node(BinaryTree.Node):
        def __init__(self, x):
            super().__init__()
            self.x = x

    def _new_node(self, x) -> Node:
        return MeldableHeap.Node(x)

    def __init__(self, iterable: Iterable[Any] = []):
        """
        A Randomized Meldable Heap is a priority queue where the underlying structure
        is also a heap-ordered binary tree. However, there are no restrictions on the shape
        of the underlying binary tree.

        This is an implementation of Gambin and Malinowsky's randomized meldable heaps.
        This datastructure allows additions and removals in O(log n) average time.

        A. Gambin and A. Malinowski. Randomized meldable priority queues.
        Proceedings of the XXVth Seminar on Current Trends in Theory and Practice
        of Informatics (SOFSEM'98), pp. 344-349, 1998

        Parameters
        ----------
        iterable : Iterable[Any], optional
            Add elements in `iterable` to the heap.
            By default `[]`.
        """
        super().__init__()
        self._n = 0
        self.add_all(iterable)

    def __iter__(self):
        u = self._first_node()
        while u != self._nil:
            yield u.x
            u = self._next_node(u)

    def _find_min(self) -> Any:
        if self._n == 0:
            raise IndexError("find_min on empty queue")
        return self._r.x

    def _merge(self, h1: Node, h2: Node) -> Node:
        if h1 == self._nil:
            return h2
        if h2 == self._nil:
            return h1
        if h2.x < h1.x:
            (h1, h2) = (h2, h1)
        if random_bit():
            h1.left = self._merge(h1.left, h2)
            h1.left.parent = h1
        else:
            h1.right = self._merge(h1.right, h2)
            h1.right.parent = h1
        return h1

    def add(self, object):
        """
        Add object to heap.

        NOTE: Object must support comparison operator `<`, e.g., by implementing `__lt__`.
        """
        u = self._new_node(object)
        self._r = self._merge(u, self._r)
        self._r.parent = self._nil
        self._n += 1

    def remove(self) -> Any:
        """
        Remove and return element with the highest priority.

        Raises IndexError on empty heap.
        """
        if self._n == 0:
            raise IndexError("remove from empty heap")
        x = self._r.x
        self._r = self._merge(self._r.left, self._r.right)
        if self._r != self._nil:
            self._r.parent = self._nil
        self._n -= 1
        return x
