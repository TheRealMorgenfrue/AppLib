"""
A basic binary tree implementation

Courtesy of https://opendatastructures.org/
"""

from typing import Self

from .arrayqueue import ArrayQueue


class BinaryTree:
    class Node:
        def __init__(self):
            self.left = None  # type: Self
            self.right = None  # type: Self
            self.parent = None  # type: Self

    def __init__(self):
        super().__init__()
        self._nil = None
        self._r = None  # type: BinaryTree.Node

    def __size(self, u: Node) -> int:
        if u == self._nil:
            return 0
        return 1 + self.__size(u.left) + self.__size(u.right)

    def _height(self, u: Node) -> int:
        if u == self._nil:
            return 0
        return 1 + max(self._height(u.left), self._height(u.right))

    def _size(self) -> int:
        return self.__size(self._r)

    def _size2(self) -> int:
        u = self._r
        prv = self._nil
        n = 0
        while u != self._nil:
            if prv == u.parent:
                n += 1
                if u.left != self._nil:
                    nxt = u.left
                elif u.right != self._nil:
                    nxt = u.right
                else:
                    nxt = u.parent
            elif prv == u.left:
                if u.right != self._nil:
                    nxt = u.right
                else:
                    nxt = u.parent
            else:
                nxt = u.parent
            prv = u
            u = nxt
        return n

    def _traverse(self, u: Node):
        if u == self._nil:
            return
        self._traverse(u.left)
        self._traverse(u.right)

    def _traverse2(self):
        u = self._r
        prv = self._nil
        while u != self._nil:
            if prv == u.parent:
                if u.left != self._nil:
                    nxt = u.left
                elif u.right != self._nil:
                    nxt = u.right
                else:
                    nxt = u.parent
            elif prv == u.left:
                if u.right != self._nil:
                    nxt = u.right
                else:
                    nxt = u.parent
            else:
                nxt = u.parent
            prv = u
            u = nxt

    def _bf_traverse(self):
        q = ArrayQueue()
        if self._r != self._nil:
            q.add(self._r)
        while q._size() > 0:
            u = q.remove()  # type: BinaryTree.Node
            if u.left != self._nil:
                q.add(u.left)
            if u.right != self._nil:
                q.add(u.right)

    def _first_node(self) -> Node:
        """Find the first node in an in-order traversal"""
        w = self._r
        if w == self._nil:
            return self._nil
        while w.left != self._nil:
            w = w.left
        return w

    def _next_node(self, w: Node) -> Node:
        """Find the node that follows w in an in-order traversal"""
        if w.right != self._nil:
            w = w.right
            while w.left != self._nil:
                w = w.left
        else:
            while w.parent != self._nil and w.parent.left != w:
                w = w.parent
            w = w.parent
        return w

    def depth(self, u: Node) -> int:
        d = 0
        while u != self._r:
            u = u.parent
            d += 1
        return d

    def height(self):
        return self._height(self._r)
