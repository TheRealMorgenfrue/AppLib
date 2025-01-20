"""
Some base classes inherited by others

Courtesy of https://opendatastructures.org/
"""

from copy import copy
from typing import Any, Iterable, Self


class BaseCollection:
    """Base class for everything"""

    def __init__(self):
        super().__init__()

    def __len__(self):
        return self._size()

    def __str__(self):
        return "[" + ", ".join([f"{x}" for x in self]) + "]"

    def __repr__(self):
        return self.__class__.__name__ + "([" + ",".join([repr(x) for x in self]) + "])"

    def _size(self):
        """This implementation works for almost every class in ODS"""
        return self._n


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
            yield (self._get(i))

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
        if isinstance(key, slice):
            item = []
            for i in range(key.indices(self._size())):
                item.append(self._get(i))
            return item
        elif isinstance(key, int):
            return self._get(key)  # IndexError
        else:
            emsg = (
                f"invalid index '{type(key).__name__}'. Expected an integer or a slice"
            )
            raise TypeError(emsg)

    def __setitem__(self, key, value):
        return self._set(key, value)

    def __delitem__(self, item):
        self._remove(item)

    def __contains__(self, item):
        try:
            self.index(item)
            return True
        except ValueError:
            return False

    def _add_first(self, x):
        return self._add(0, x)

    def _remove_first(self):
        return self._remove(0)

    def _add_last(self, x):
        return self._add(self._size(), x)

    def _remove_last(self):
        return self._remove(self._size() - 1)

    def clear(self):
        """This can be overridden with more efficient implementations"""
        while self._size() > 0:
            self._remove(self._size() - 1)

    def insert(self, index: int, object):
        """Insert object before index."""
        self._add(index, object)

    def index(self, object) -> int:
        """
        Return first index of value.

        Raises ValueError if the value is not present.
        """
        i = 0
        for y in self:
            if y == object:
                return i
            i += 1
        raise ValueError(f"'{object}' is not in the list")

    def remove(self, object) -> None:
        """
        Remove first occurrence of value.

        Raises ValueError if the value is not present.
        """
        self._remove(self.index(object))

    def pop(self, index: int = -1) -> Any:
        """
        Remove and return item at index (default last).

        Raises IndexError if list is empty or index is out of range.
        """
        if self._size() == 0:
            raise IndexError("pop from empty list")
        if index < 0:
            index = self._size() + index
        return self._remove(index)

    def append(self, object: Any) -> None:
        """Append object to the end of the list."""
        self._add(self._size(), object)

    def extend(self, a: Iterable) -> None:
        """Extend list by appending elements from the iterable."""
        for x in a:
            self.append(x)

    def copy(self) -> Self:
        """Return a shallow copy of the list."""
        return copy(self)

    def count(self, value: Any) -> int:
        """Return number of occurrences of value."""
        count = 0
        for y in self:
            if y == value:
                count += 1
        return count
