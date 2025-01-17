"""
An implementation of Treaps/Cartesian trees

This is an implementation of the data structure called a Treap by Aragon
and Seidel:

C. R. Aragon and R. Seidel. Randomized Search Trees. In Algorithmica,
   Vol. 16, Number 4/5, pp. 464-497, 1996.

Pretty-much the same structure was discovered earlier by Vuillemin:

J. Vuillemin. A unifying look at data structures.
   Communications of the ACM, 23(4), 229-239, 1980.

Courtesy of https://opendatastructures.org/
"""

import random
from typing import Iterable

from .binarysearchtree import BinarySearchTree


class Treap(BinarySearchTree):
    class Node(BinarySearchTree.Node):
        def __init__(self, x):
            super().__init__(x)
            self.p = random.random()

        def __str__(self):
            return f"[{self.x},{self.p}]"

    def __init__(self, iterable: Iterable = []):
        super().__init__(iterable)

    def _new_node(self, x) -> Node:
        return Treap.Node(x)

    def _bubble_up(self, u: Node):
        while u != self.r and u.parent.p > u.p:
            if u.parent.right == u:
                self._rotate_left(u.parent)
            else:
                self._rotate_right(u.parent)

        if u.parent == self.nil:
            self.r = u

    def _trickle_down(self, u: Node):
        while u.left is not None or u.right is not None:
            if u.left is None:
                self._rotate_left(u)
            elif u.right is None:
                self._rotate_right(u)
            elif u.left.p < u.right.p:
                self._rotate_right(u)
            else:
                self._rotate_left(u)
            if self.r == u:
                self.r = u.parent

    def add(self, x) -> bool:
        u = self._new_node(x)
        if self._add_node(u):
            self._bubble_up(u)
            return True
        return False

    def remove(self, x) -> bool:
        u = self._find_last(x)
        if u is not None and u.x == x:
            self._trickle_down(u)
            self._splice(u)
            return True
        return False
