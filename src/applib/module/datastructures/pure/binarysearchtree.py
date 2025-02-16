"""
An implementation of a binary search tree

Courtesy of https://opendatastructures.org/
"""

from typing import Any, Iterable, Union

from .base import BaseSet
from .binarytree import BinaryTree


class BinarySearchTree(BinaryTree, BaseSet):
    """Base class for all our binary search trees"""

    class Node(BinaryTree.Node):
        def __init__(self, x):
            super().__init__()
            self.x = x

    def _new_node(self, x: Node) -> Node:
        u = BinarySearchTree.Node(x)
        u.left = u.right = u.parent = self._nil
        return u

    def __init__(self, iterable: Iterable = [], nil=None):
        super().__init__()
        self._initialize(nil)
        self.add_all(iterable)

    def __iter__(self):
        u = self._first_node()
        while u != self._nil:
            yield u.x
            u = self._next_node(u)

    def _initialize(self, nil):
        self._n = 0
        self._nil = nil

    def _find_last(self, x) -> Union[Node, Any]:
        w = self._r
        prev = self._nil
        while w is not self._nil:
            prev = w
            if x < w.x:
                w = w.left
            elif x > w.x:
                w = w.right
            else:
                return w
        return prev

    def _add_child(self, p: Node, u: Node) -> bool:
        if p == self._nil:
            self._r = u  # inserting into empty tree
        else:
            if u.x < p.x:
                p.left = u
            elif u.x > p.x:
                p.right = u
            else:
                return False  # u.x is already in the tree
            u.parent = p
        self._n += 1
        return True

    def _remove_node(self, u: Node):
        if u.left == self._nil or u.right == self._nil:
            self._splice(u)
        else:
            w = u.right
            while w.left != self._nil:
                w = w.left
            u.x = w.x
            self._splice(w)

    def _rotate_left(self, u: Node):
        w = u.right
        w.parent = u.parent
        if w.parent != self._nil:
            if w.parent.left == u:
                w.parent.left = w
            else:
                w.parent.right = w
        u.right = w.left
        if u.right != self._nil:
            u.right.parent = u
        u.parent = w
        w.left = u
        if u == self._r:
            self._r = w
            self._r.parent = self._nil

    def _rotate_right(self, u: Node):
        w = u.left
        w.parent = u.parent
        if w.parent != self._nil:
            if w.parent.left == u:
                w.parent.left = w
            else:
                w.parent.right = w
        u.left = w.right
        if u.left != self._nil:
            u.left.parent = u
        u.parent = w
        w.right = u
        if u == self._r:
            self._r = w
            self._r.parent = self._nil

    def _find_eq(self, x) -> Any | None:
        w = self._r
        while w != self._nil:
            if x < w.x:
                w = w.left
            elif x > w.x:
                w = w.right
            else:
                return w.x
        return None

    def _add_node(self, u: Node) -> bool:
        p = self._find_last(u.x)
        return self._add_child(p, u)

    def _splice(self, u: Node):
        if u.left != self._nil:
            s = u.left
        else:
            s = u.right
        if u == self._r:
            self._r = s
            p = self._nil
        else:
            p = u.parent
            if p.left == u:
                p.left = s
            else:
                p.right = s
        if s != self._nil:
            s.parent = p
        self._n -= 1

    def _find_node(self, x) -> Node | None:
        w = self._r
        z = self._nil
        while w != self._nil:
            if x < w.x:
                z = w
                w = w.left
            elif x > w.x:
                w = w.right
            else:
                return w.x
        return None

    def find(self, x) -> Any | None:
        """
        Find object in the tree.

        Returns None if not found.
        """
        u = self._find_node(x)
        return u.x if u else None

    def clear(self):
        self._r = self._nil
        self._n = 0

    def add(self, x) -> bool:
        p = self._find_last(x)
        return self._add_child(p, self._new_node(x))

    def remove(self, x) -> bool:
        u = self._find_last(x)
        if u != self._nil and x == u.x:
            self._remove_node(u)
            return True
        return False
