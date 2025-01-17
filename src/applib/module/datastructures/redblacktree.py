"""
An implementation of Guibas and Sedgewick's red-black trees

This is an implementation of left-leaning red-black trees.  The best
documentation for this implementation is available in Chapter 9 of
Open Data Structures.

Leonidas J. Guibas, Robert Sedgewick: A Dichromatic Framework for Balanced
   Trees. FOCS 1978: 8-21

Courtesy of https://opendatastructures.org/
"""

from typing import Iterable

from .binarysearchtree import BinarySearchTree

red = 0
black = 1


class RedBlackTree(BinarySearchTree):
    class Node(BinarySearchTree.Node):
        def __init__(self, x):
            super().__init__(x)
            self.colour = black

    def _new_node(self, x) -> Node:
        u = RedBlackTree.Node(x)
        u.left = u.right = u.parent = self.nil
        return u

    def __init__(self, iterable: Iterable = []):
        self.nil = RedBlackTree.Node(None)
        self.nil.right = self.nil.left = self.nil.parent = self.nil
        super().__init__([], self.nil)
        self.r = self.nil
        self.add_all(iterable)

    def _push_black(self, u: Node):
        u.colour -= 1
        u.left.colour += 1
        u.right.colour += 1

    def _pull_black(self, u: Node):
        u.colour += 1
        u.left.colour -= 1
        u.right.colour -= 1

    def _flip_left(self, u: Node):
        self._swap_colours(u, u.right)
        self._rotate_left(u)

    def _flip_right(self, u: Node):
        self._swap_colours(u, u.left)
        self._rotate_right(u)

    def _swap_colours(self, u: Node, w: Node):
        (u.colour, w.colour) = (w.colour, u.colour)

    def _add_fixup(self, u: Node):
        while u.colour == red:
            if u == self.r:
                u.colour = black
            w = u.parent
            if w.left.colour == black:
                self._flip_left(w)
                u = w
                w = u.parent
            if w.colour == black:
                return  # red-red edge is eliminated - done
            g = w.parent
            if g.right.colour == black:
                self._flip_right(g)
                return
            self._push_black(g)
            u = g

    def _remove_fixup(self, u: Node):
        while u.colour > black:
            if u == self.r:
                u.colour = black
            elif u.parent.left.colour == red:
                u = self._remove_fixup_case1(u)
            elif u == u.parent.left:
                u = self._remove_fixup_case2(u)
            else:
                u = self._remove_fixup_case3(u)
        if u != self.r:  # restore left-leaning property, if needed
            w = u.parent
            if w.right.colour == red and w.left.colour == black:
                self._flip_left(w)

    def _remove_fixup_case1(self, u: Node) -> Node:
        self._flip_right(u.parent)
        return u

    def _remove_fixup_case2(self, u: Node) -> Node:
        w = u.parent
        v = w.right
        self._pull_black(w)
        self._flip_left(w)
        q = w.right
        if q.colour == red:
            self._rotate_left(w)
            self._flip_right(v)
            self._push_black(q)
            if v.right.colour == red:
                self._flip_left(v)
            return q
        else:
            return v

    def _remove_fixup_case3(self, u: Node) -> Node:
        w = u.parent
        v = w.left
        self._pull_black(w)
        self._flip_right(w)  # w is now red
        q = w.left
        if q.colour == red:  # q-w is red-red
            self._rotate_right(w)
            self._flip_left(v)
            self._push_black(q)
            return q
        else:
            if v.left.colour == red:
                self._push_black(v)
                return v
            else:  # ensure left-leaning
                self._flip_left(v)
                return w

    def remove(self, x) -> bool:
        u = self._find_last(x)
        if u == self.nil or u.x != x:
            return False
        w = u.right
        if w == self.nil:
            w = u
            u = w.left
        else:
            while w.left != self.nil:
                w = w.left
            u.x = w.x
            u = w.right
        self._splice(w)
        u.colour += w.colour
        u.parent = w.parent
        self._remove_fixup(u)
        return True

    def add(self, x) -> bool:
        u = self._new_node(x)
        u.colour = red
        if self._add_node(u):
            self._add_fixup(u)
            return True
        return False
