from collections import deque
from typing import (
    Any,
    Generator,
    Any,
    Hashable,
    Iterable,
    Mapping,
    Self,
    TypeAlias,
    Union,
)

from .pure.meldableheap import MeldableHeap
from .pure.redblacktree import RedBlackTree
from .pure.skiplist import Skiplist

_rbtm_key: TypeAlias = tuple[Hashable, Hashable, bool]
_rbtm_item: TypeAlias = tuple[Hashable, Any, int, Iterable[Hashable]]
_rbtm_iterable: TypeAlias = Iterable[_rbtm_item]
_rbtm_mapping: TypeAlias = Union[Mapping, "RedBlackTreeMapping"]
_supports_rbtm_iter: TypeAlias = Union[_rbtm_iterable, _rbtm_mapping]


class RedBlackTreeMapping(RedBlackTree):
    class TreeNode:
        def __init__(
            self,
            k: Hashable,
            v: Any,
            pos: int,
            ps: Union[Hashable, Iterable[Hashable], None],
        ):
            self._idx = f"{k}".encode(errors="replace")
            self.keys = Skiplist([k])  # Keys are identical for each node
            self.values = Skiplist([v])
            self.position = Skiplist([pos])  # Restores order of keys when dumping data
            self.parents = Skiplist([ps])  # Uniquely identifies keys

        def __iter__(self) -> Generator[_rbtm_item, Any, None]:
            for i in range(len(self.keys)):
                yield (self.keys[i], self.values[i], self.position[i], self.parents[i])

        def __lt__(self, other):
            if isinstance(other, RedBlackTreeMapping.TreeNode):
                return self._idx < other._idx
            return NotImplemented

        def __gt__(self, other):
            if isinstance(other, RedBlackTreeMapping.TreeNode):
                self._idx > other._idx
            return NotImplemented

        def __str__(self) -> str:
            return f"keys: {self.keys}\n  values: {self.values}\n  parents: {self.parents}\n  position: {self.position}"

        def get_multi_index(
            self, p: Union[Hashable, Iterable[Hashable]], im: bool = False
        ) -> list[int]:
            """
            Return all possible indices given `p` + `im`

            If `p` is iterable, `im` is ignored.
            """
            if isinstance(p, Iterable):
                # TODO: Implement fuzzy matching of array values
                # E.g. ["a", "b", "c", "d"] == ["a", "b", "c"] iff im == False,
                #      ["a", "b", "c", "d"] == ["b", "c", "d"] iff im == True
                i = [self.parents.index(p)]  # Raises ValueError if not present
            else:
                if im:
                    i = [i for i, ps in enumerate(self.parents) if p == ps[-1]]
                else:
                    i = [i for i, ps in enumerate(self.parents) if p in ps]
            return i

        def get_index(
            self, p: Union[Hashable, Iterable[Hashable]], im: bool = False
        ) -> int:
            """
            Get index of `p`.

            NOTE
            ----
            If `p` is not an Iterable, it is in some cases not possible to uniquely identify a key based on `p` + `im`.
            In such cases `p` must be an Iterable of all parents of the key. However, for the average use-case, `p` + `im` is sufficient.

            Parameters
            ----------
            p : Hashable | Iterable[Hashable] | None, optional
                The parent of the key.
                By default None.

            im : bool, optional
                If True, `p` must be the direct predecessor of the key.
                If False, `p` must be an ancestor of the key.
                Is ignored if `p` is an Iterable.
                By default True.

            Raises
            ------
            ValueError
                If `p` does not exist.

            LookupError
                If `p` cannot be uniquely identified.
                Can happen if `p` is not an Iterable of all parents of the key.
            """
            i = self.get_multi_index(p, im)
            if len(i) > 1:
                raise LookupError("multiple possibilities for key")
            return i[0]

        def is_immediate_parent_of(
            self, p: Union[Hashable, Iterable[Hashable]]
        ) -> tuple[bool, int]:
            """`p` is a direct predecessor of `k`."""
            i = self.get_index(p, True)
            return (self.parents[i][-1] == p, i)

        def is_parent_of(
            self, p: Union[Hashable, Iterable[Hashable]]
        ) -> tuple[bool, int]:
            """`p` is an ancestor of `k`."""
            i = self.get_index(p, False)
            return (p in self.parents[i], i)

        def add(
            self,
            k: Hashable,
            v: Any,
            pos: int,
            ps: Iterable[Hashable],
        ):
            """
            Add objects to the list.

            If (`k`, `ps`) already exists, that entry is overwritten.
            """
            try:
                i = self.parents.index(ps)
                self.values[i] = v
                self.position[i] = pos
                self.parents[i] = ps
            except ValueError:
                self.keys.append(k)
                self.values.append(v)
                self.position.append(pos)
                self.parents.append(ps)

        def remove(self, i: int) -> _rbtm_item:
            """Remove and return objects at index `i`."""
            return (
                self.keys.pop(i),
                self.values.pop(i),
                self.position.pop(i),
                self.parents.pop(i),
            )

    class HeapNode:
        def __init__(self, k: Hashable, v: Any, pos: int, ps: Iterable[Hashable]):
            self.k = k
            self.v = v
            self.pos = pos
            self.ps = ps

        def __lt__(self, other):
            if isinstance(other, RedBlackTreeMapping.HeapNode):
                lps, los = len(self.ps), len(other.ps)
                if lps < los:
                    return True
                elif lps == los:
                    return self.pos < other.pos
                return False
            return NotImplemented

        def get(self) -> _rbtm_item:
            return (self.k, self.v, self.pos, self.ps)

    def __init__(
        self,
        iterable: Iterable[_supports_rbtm_iter] = [],
        name: str = "",
    ):
        """
        A variant of the red-black tree that maps keys to values while handling duplicate keys.
        Unlike Python's standard mapping, dict, it allows quick retrieval of deeply nested key-value pairs.

        This is achieved by using the parameter `parents`, a list containing the path of parents
        from key `k` to the root for any `k` in the tree. Thus, every key can be uniquely identified
        by combining (key, parents).

        This structure is able to store arbitrary objects with O(log n) worst-case time searches,
        additions, and removals. It has a space complexity of O(n).

        Parameters
        ----------
        iterable : Iterable[_supports_rbtm_iter], optional
            Add elements in `iterable` to the tree.

            `iterable` may contain any of:
            _rbt_iterable : Iterable[_rbtm_item]
                A tuple that must contain 3 or 4 items (`key`, `value`, `position`, `parents`), where `parents` may be omitted.
                    key : Hashable
                        Key to insert.
                    value : Any
                       Value mapped to `key`.
                    position : int
                        The index of `key` in the mapping. It must be unique for all keys k, where k.parents == `key`.`parents`.
                    parents : Iterable[Hashable], optional
                        Iterable of all `key`'s parents (a.k.a. ancestors).
                        May be omitted from the tuple, resulting in a "flat" tree.
            Mapping :
                Any class supporting the Mapping interface for providing key-value pairs.
            RedBlackTreeMapping :
                An instance of this class.

        name : str, optional
            Give the tree a name for easier identification.
            By default "".
        """
        super().__init__()
        self.name = name
        self._prefix_msg = f"{self.__class__.__name__} {self.name}:"
        self._top_nodes = 0
        self.add_all(iterable)

    def __iter__(
        self,
    ) -> Generator[_rbtm_item, Any, None]:
        for tn in super().__iter__():
            for item in tn:
                yield item

    def __or__(self, other):
        if not isinstance(other, (Mapping, RedBlackTreeMapping)):
            return NotImplemented
        new = RedBlackTreeMapping([self])
        new.add_all([other])
        return new

    def __ror__(self, other):
        if not isinstance(other, (Mapping, RedBlackTreeMapping)):
            return NotImplemented
        new = RedBlackTreeMapping([other])
        new.add_all([self])
        return new

    def __ior__(self, other):
        if not isinstance(other, (Mapping, RedBlackTreeMapping)):
            return NotImplemented
        self.add_all([other])
        return self

    def __getitem__(self, key):
        return self._convert_lookup_error(self.find, *self._check_key(key))

    def __setitem__(self, key, value):
        k, p, im = self._check_key(key)
        self._convert_lookup_error(self.update, k, value, p, im)

    def __delitem__(self, key):
        self._convert_lookup_error(self.remove, *self._check_key(key))

    def __contains__(self, item):
        try:
            self._find_index(*self._check_key(item))
            return True
        except (ValueError, KeyError):
            return False
        except LookupError:
            return True

    def _raise_key_error(self, k, p, from_none: bool = True):
        e = KeyError(f"{self._prefix_msg} Key ('{k}', '{p}') does not exist")
        if from_none:
            raise e from None
        else:
            raise e

    def _raise_lookup_error(self, k, p, tn, from_none: bool = True):
        e = LookupError(
            f"{self._prefix_msg} Cannot uniquely identify a value for (key '{k}', parent '{p}')"
        )
        e.add_note(f"{self._prefix_msg} Possible values:\n  {tn}")
        if from_none:
            raise e from None
        else:
            raise e

    def _convert_lookup_error(self, func, *args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except LookupError as e:
            k = KeyError()
            for n in e.__notes__:
                k.add_note(n)
            raise k from None

    def _check_key(self, key: Hashable | tuple) -> _rbtm_key:
        """
        Ensure `key` is a valid tuple for lookup in the tree.

        Parameters
        ----------
        key : Hashable | tuple
            The lookup key.

        Returns
        -------
        _rbtm_key
            A correct lookup key.

        Raises
        ------
        ValueError
            Key is invalid.
        """
        k, p, im = key, None, True
        if isinstance(key, (tuple)):
            try:
                if len(key) == 2:
                    k, p = key
                else:  # len(key) == 3
                    k, p, im = key
            except ValueError as e:
                e.add_note(
                    f"tuple must contain 1-3 items (key, parent, immediate), where key is required. "
                    + "Type: tuple[Hashable, Hashable, bool]"
                )
                raise e from None
        return k, p, im

    def _check_value(self, v) -> bool:
        return (
            isinstance(v, Iterable)
            and v
            and isinstance(v[0], tuple)
            and v[0]
            and isinstance(v[0][0], RedBlackTreeMapping.TreeNode)
        )

    def _find_index(
        self,
        key: Hashable,
        parent: Union[Hashable, Iterable[Hashable], None] = None,
        immediate: bool = True,
    ) -> tuple["RedBlackTreeMapping.TreeNode", int]:
        """
        Return the index of `key` in its TreeNode object.

        Parameters
        ----------
        key : Hashable
            The key to look for.

        parent : Hashable | Iterable[Hashable] | None, optional
            The parent of `key`.
            By default None.

        immediate : bool, optional
            If True, `parent` must be the direct predecessor of `key`.
            If False, `parent` must be an ancestor of `key`.
            Is ignored if `parent` is an Iterable.
            By default True.

        Returns
        -------
        tuple[RedBlackTreeMapping.TreeNode, int]
            The TreeNode which contains `key` at index.

        Raises
        ------
        KeyError
            If the combination of (`key`,`parent`) does not exist.

        LookupError
            If a key-value pair can not be uniquely identified from (`key`,`parent`).
            Can happen if `parent` information is insufficient.
        """
        tn = RedBlackTreeMapping.TreeNode(key, None, None, parent)
        u = self._find_node(tn)
        if u is None:
            self._raise_key_error(key, parent)

        tn = u.x  # type: RedBlackTreeMapping.TreeNode
        if parent is None:
            if len(tn.keys) > 1:
                self._raise_lookup_error(key, parent, tn)
            i = 0
        else:
            try:
                if immediate:
                    yes, i = tn.is_immediate_parent_of(parent)
                else:
                    yes, i = tn.is_parent_of(parent)
                if not yes:
                    self._raise_key_error(key, parent)
            except LookupError:
                self._raise_lookup_error(key, parent, tn)
            except ValueError:
                self._raise_key_error(key, parent)
        return (tn, i)

    def find(
        self,
        key: Hashable,
        parent: Union[Hashable, Iterable[Hashable], None] = None,
        immediate: bool = True,
    ) -> Any:
        """
        Return the value for `key`.

        Parameters
        ----------
        key : Hashable
            The key to look for.

        parent : Hashable | Iterable[Hashable] | None, optional
            The parent of `key`.
            By default None.

        immediate : bool, optional
            If True, `parent` must be the direct predecessor of `key`.
            If False, `parent` must be an ancestor of `key`.
            Is ignored if `parent` is an Iterable.
            By default True.

        Raises
        ------
        KeyError
            If the combination of (`key`,`parent`) does not exist.

        LookupError
            If a key-value pair can not be uniquely identified from (`key`,`parent`).
            Can happen if `parent` information is insufficient.
        """
        tn, i = self._find_index(key, parent, immediate)
        v = tn.values[i]
        return self._dump(v) if self._check_value(v) else v

    def add_all(self, iterable: Iterable[_supports_rbtm_iter]):
        """
        Add elements in `iterable` to the tree.

        Parameters
        ----------
        iterable : Iterable[_supports_rbtm_iter]
            `iterable` may contain any of:
            _rbt_iterable : Iterable[tuple[Hashable, Any, Iterable[Hashable]]]
                The tuple must contain 3 or 4 items (`key`, `value`, `position`, `parents`), where `parents` may be omitted.
                    key : Hashable
                        Key to insert.
                    value : Any
                        Value mapped to `key`.
                    position : int
                        The index of `key` in the mapping. It must be unique for all keys k, where k.parents == `key`.`parents`.
                    parents : Iterable[Hashable], optional
                        Iterable of all `key`'s parents (a.k.a. ancestors).
                        May be omitted from the tuple, resulting in a "flat" tree.
            Mapping :
                Any class supporting the Mapping interface for providing key-value pairs.
            RedBlackTreeMapping :
                An instance of this class.
        """
        for x in iterable:
            if isinstance(x, Mapping):
                self.add_mapping(x)
            elif isinstance(x, RedBlackTreeMapping):
                self.add_tree(x)
            else:
                for args in x:
                    self.add(*args)

    def _add(
        self, key: Hashable, value: Any, position: int, parents: Iterable[Hashable] = []
    ) -> "RedBlackTreeMapping.TreeNode":
        if len(parents) == 0:
            # Ensure position of top-level keys remain predictable during unions
            position += self._top_nodes
            self._top_nodes += 1

        tn = RedBlackTreeMapping.TreeNode(key, value, position, parents)
        u = self._find_node(tn)  # type: RedBlackTreeMapping.TreeNode
        if u is None:  # Object is new
            super().add(tn)
            return tn
        else:  # Append to existing node
            u.add(key, value, position, parents)
            self._n += 1  # Update size
            return u

    def add(
        self, key: Hashable, value: Any, position: int, parents: Iterable[Hashable] = []
    ):
        """
        Add key-value pair to the tree.

        Parameters
        ----------
        key : Hashable
            Key to insert.

        value : Any
            Map value to `key`.

        position : int
            The index of `key` in the mapping.
            It must be unique for all keys k, where k.parents == `key`.`parents`.

        parents : Iterable[Hashable], optional
            Iterable of all `key`'s parents (a.k.a. ancestors).
            May be omitted from the tuple, resulting in a "flat" tree.
        """
        self._add(key, value, position, parents)

    def add_mapping(self, m: Mapping):
        """
        Add all key-value pairs in `m` to this tree.

        Overwrites existing keys in this tree with keys from `m`.
        """
        if not m:
            return
        q = (
            deque()
        )  # type: deque[tuple[Mapping, list, tuple[RedBlackTreeMapping.TreeNode, list] | None]]
        q.append((m, [], None))
        while q:
            e, ps, tnp_tuple = q.popleft()
            for i, item in enumerate(e.items()):
                k, v = item

                # Add current key in mapping
                if isinstance(v, Mapping):
                    tn = self._add(k, [], i, ps)
                    q.append((v, [*ps, k], (tn, ps)))
                else:
                    tn = self._add(k, v, i, ps)

                # Add reference to parent node
                if tnp_tuple is not None:
                    tnp, tnp_ps = tnp_tuple
                    tnp.values[tnp.get_index(tnp_ps)].append((tn, ps))

    def add_tree(self, t: Self):
        """
        Add all key-value pairs in `t` to this tree.

        Overwrites existing keys in this tree with keys from `t`.
        """
        for args in t:
            self.add(*args)

    def remove(
        self,
        key: Hashable,
        parent: Union[Hashable, Iterable[Hashable], None] = None,
        immediate: bool = True,
    ) -> tuple[Hashable, Any, Hashable]:
        """
        Remove and return a key-value pair from this tree.

        Parameters
        ----------
        key : Hashable
            Key-value pair to remove.

        parent : Hashable | Iterable[Hashable] | None, optional
            The parent of `key`.
            By default `None`.

        immediate : bool, optional
            If True, `parent` must be the direct predecessor of `key`.
            If False, `parent` must be an ancestor of `key`.
            Is ignored if `parent` is an Iterable.
            By default True.

        Returns
        -------
        tuple[Hashable, Any, Hashable]
            A tuple of (`key`, `value`, `parents`).

        Raises
        ------
        KeyError
            If the combination of (`key`,`parent`) does not exist.

        LookupError
            If a key-value pair can not be uniquely identified from (`key`,`parent`).
            Can happen if `parent` information is insufficient.
        """
        tn, i = self._find_index(key, parent, immediate)
        if len(tn.values) <= 1:  # At most one key in node, remove node entirely
            super().remove(tn)
        else:
            self._n -= 1  # Update size

        # Remove parent node's reference to this node, if any.
        ps = tn.parents[i]
        if ps:
            tnp, ip = self._find_index(ps[-1], ps[:-2])
            tnp.values.remove(tn)

        return tn.remove(i)  # Remove key from the node's list

    def update(
        self,
        key: Hashable,
        value: Any,
        parent: Union[Hashable, Iterable[Hashable], None] = None,
        immediate: bool = True,
    ):
        """
        Update value of `key` with `value`.

        Parameters
        ----------
        key : Hashable
            The key to look for.

        value : Any
            Map value to `key`.

        parent : Hashable | Iterable[Hashable] | None, optional
            The parent of `key`.
            By default None.

        immediate : bool, optional
            If True, `parent` must be the direct predecessor of `key`.
            If False, `parent` must be an ancestor of `key`.
            Is ignored if `parent` is an Iterable.
            By default True.

        Raises
        ------
        KeyError
            If the combination of (`key`,`parent`) does not exist.

        LookupError
            If a key-value pair can not be uniquely identified from (`key`,`parent`).
            Can happen if `parent` information is insufficient.
        """
        tn, i = self._find_index(key, parent, immediate)
        tn.values[i] = value

    def _dump(self, items: Iterable[_rbtm_item]) -> dict[Hashable, Any]:
        dump = {}
        heap = MeldableHeap([RedBlackTreeMapping.HeapNode(*args) for args in items])
        while heap:
            node = heap.remove()  # type: RedBlackTreeMapping.HeapNode
            k, v, i, ps = node.get()
            if self._check_value(v):
                v = {}
            if ps:
                stack = [dump]
                for p in ps:
                    stack.append(stack[-1][p])
                stack[-1] |= {k: v}
            else:
                dump |= {k: v}
        return dump

    def tree_dump(self) -> dict[Hashable, Any]:
        """
        Generate a dictionary representation of the tree.

        Returns
        -------
        dict[Hashable, Any]
            A dictionary representation of the tree.
        """
        return self._dump(self)
