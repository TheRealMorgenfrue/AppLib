"""A basic binary tree implementation"""

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
        self.nil = None
        self.r = None
        self.initialize()

    def _size(self, u: Node) -> int:
        if u == self.nil:
            return 0
        return 1 + self._size(u.left) + self._size(u.right)

    def _height(self, u: Node) -> int:
        if u == self.nil:
            return 0
        return 1 + max(self._height(u.left), self._height(u.right))

    def initialize(self):
        self.r = None  # type: BinaryTree.Node

    def depth(self, u: Node) -> int:
        d = 0
        while u != self.r:
            u = u.parent
            d += 1
        return d

    def size(self) -> int:
        return self._size(self.r)

    def size2(self) -> int:
        u = self.r
        prv = self.nil
        n = 0
        while u != self.nil:
            if prv == u.parent:
                n += 1
                if u.left != self.nil:
                    nxt = u.left
                elif u.right != self.nil:
                    nxt = u.right
                else:
                    nxt = u.parent
            elif prv == u.left:
                if u.right != self.nil:
                    nxt = u.right
                else:
                    nxt = u.parent
            else:
                nxt = u.parent
            prv = u
            u = nxt
        return n

    def height(self):
        return self.height_r(self.r)

    def traverse(self, u: Node):
        if u == self.nil:
            return
        self.traverse(u.left)
        self.traverse(u.right)

    def traverse2(self):
        u = self.r
        prv = self.nil
        while u != self.nil:
            if prv == u.parent:
                if u.left != self.nil:
                    nxt = u.left
                elif u.right != self.nil:
                    nxt = u.right
                else:
                    nxt = u.parent
            elif prv == u.left:
                if u.right != self.nil:
                    nxt = u.right
                else:
                    nxt = u.parent
            else:
                nxt = u.parent
            prv = u
            u = nxt

    def bf_traverse(self):
        q = ArrayQueue()
        if self.r != self.nil:
            q.add(self.r)
        while q.size() > 0:
            u = q.remove()  # type: BinaryTree.Node
            if u.left != self.nil:
                q.add(u.left)
            if u.right != self.nil:
                q.add(u.right)

    def first_node(self) -> Node:
        """Find the first node in an in-order traversal"""
        w = self.r
        if w == self.nil:
            return self.nil
        while w.left != self.nil:
            w = w.left
        return w

    def next_node(self, w: Node) -> Node:
        """Find the node that follows w in an in-order traversal"""
        if w.right != self.nil:
            w = w.right
            while w.left != self.nil:
                w = w.left
        else:
            while w.parent != self.nil and w.parent.left != w:
                w = w.parent
            w = w.parent
        return w
