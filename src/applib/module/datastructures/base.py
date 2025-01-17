"""Some base classes inherited by others"""

from typing import Iterable


class BaseCollection:
    """Base class for everything"""

    def __init__(self):
        super().__init__()

    def __len__(self):
        return self.size()

    def __str__(self):
        return "[" + ",".join([str(x) for x in self]) + "]"

    def __repr__(self):
        return self.__class__.__name__ + "([" + ",".join([repr(x) for x in self]) + "])"

    def size(self):
        """This implementation works for almost every class in ODS"""
        return self.n


class BaseSet(BaseCollection):
    """Base class for Set implementations"""

    def __init__(self):
        super().__init__()

    def __in__(self, x):
        return self.find(x) is not None

    def __eq__(self, a):
        if len(a) != len(self):
            return False
        for x in self:
            if not x in a:
                return False
        for x in a:
            if not x in self:
                return False
        return True

    def __ne__(self, a):
        return not self == a

    def add_all(self, a: Iterable):
        for x in a:
            self.add(x)


class BaseList(BaseCollection):
    """Base class for List implementations"""

    def __init__(self):
        super().__init__()

    def __iter__(self):
        """This implementation is good enough for array-based lists"""
        for i in range(len(self)):
            yield (self.get(i))

    def __eq__(self, a):
        if len(a) != len(self):
            return False
        it1 = iter(a)
        it2 = iter(self)
        for i in range(len(a)):
            if it1.next() != it2.next():
                return False
        return True

    def __ne__(self, a):
        return not self == a

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.set(key, value)

    def __delitem__(self, i):
        self.remove(i)

    def append(self, x):
        self.add(self.size(), x)

    def add_all(self, a: Iterable):
        for x in a:
            self.append(x)

    def clear(self):
        """This can be overridden with more efficient implementations"""
        while self.size() > 0:
            self.remove(self.size() - 1)

    def add_first(self, x):
        return self.add(0, x)

    def remove_first(self):
        return self.remove(0)

    def add_last(self, x):
        return self.add(self.size(), x)

    def remove_last(self):
        return self.remove(self.size() - 1)

    def insert(self, i: int, x):
        self.add(i, x)

    def index(self, x):
        i = 0
        for y in self:
            if y == x:
                return i
            i += 1
        raise ValueError(f"{x} is not in the list")

    def remove_value(self, x):
        try:
            return self.remove(self.index(x))
        except ValueError:
            return False
