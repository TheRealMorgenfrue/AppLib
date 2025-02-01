from collections import deque
from typing import Any, Generator, Hashable, Iterable, Mapping, Self, TypeAlias, Union

from .pure.meldableheap import MeldableHeap
from .pure.redblacktree import RedBlackTree
from .pure.skiplist import Skiplist

_rbtm_key: TypeAlias = tuple[Hashable, Hashable, bool]
_rbtm_item: TypeAlias = tuple[Hashable, Any, Iterable[int], Iterable[Hashable]]
_rbtm_iterable: TypeAlias = Iterable[_rbtm_item]
_rbtm_mapping: TypeAlias = Union[Mapping, "RedBlackTreeMapping"]
_supports_rbtm_iter: TypeAlias = Union[_rbtm_iterable, _rbtm_mapping]


class RedBlackTreeMapping(RedBlackTree):
    class TreeNode:
        def __init__(
            self,
            k: Hashable,
            v: Any,
            pos: Iterable[int],
            ps: Union[Hashable, Iterable[Hashable], None],
        ):
            self._idx = f"{k}".encode(errors="replace")
            self._parent_nodes = Skiplist([None])  # Pointer to this node's parent
            self.keys = Skiplist([k])  # Keys are identical for each node
            self.values = Skiplist([v])
            self.position = Skiplist([pos])  # Tracks the order of keys
            self.parents = Skiplist([ps])  # Uniquely identifies keys

        def __iter__(self) -> Generator[_rbtm_item, Any, None]:
            attr = [
                v
                for k, v in self.__dict__.items()
                if k[:2].count("_") == 0
                and k[-2:].count("_") == 0
                and isinstance(v, Iterable)
            ]
            for i in range(len(self.keys)):
                yield tuple([l[i] for l in attr])

        def __len__(self):
            return len(self.keys)

        def __lt__(self, other):
            if not isinstance(other, RedBlackTreeMapping.TreeNode):
                return NotImplemented
            return self._idx < other._idx

        def __gt__(self, other):
            if not isinstance(other, RedBlackTreeMapping.TreeNode):
                return NotImplemented
            return self._idx > other._idx

        def __str__(self) -> str:
            values = ", ".join(
                [
                    f"{k}: {v}"
                    for k, v in self.__dict__.items()
                    if k[:2].count("_") == 0 and k[-2:].count("_") == 0
                ]
            )
            return f"{self.__class__.__name__} -> ({values})"

        def get_multi_index(
            self, p: Union[Hashable, Iterable[Hashable]], im: bool = False
        ) -> list[int]:
            """
            Return all possible indices given `p` + `im`.

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
            pos: Iterable[int],
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
                self._parent_nodes.append(None)

        def remove(self, i: int) -> _rbtm_item:
            """Remove and return objects at index `i`."""
            # Do not return internal tree data
            self._parent_nodes.pop(i)
            return (
                self.keys.pop(i),
                self.values.pop(i),
                self.position.pop(i),
                self.parents.pop(i),
            )

    class HeapNode:
        def __init__(
            self,
            k: Hashable,
            v: Any,
            pos: Iterable[int],
            ps: Iterable[Hashable],
            _reversed_=False,
        ):
            self.k = k
            self.v = v
            self.pos = pos
            self.ps = ps
            self._ppos = dict(
                zip([*ps, k], pos, strict=True)
            )  # Restores order of keys when sorting data
            self._reversed_ = _reversed_

        def __lt__(self, other):
            if not isinstance(other, RedBlackTreeMapping.HeapNode):
                return NotImplemented

            lps, lops = len(self.ps), len(other.ps)
            if lps < lops:
                # Node's parent path is shorter
                return self._is_reverse(True)
            elif lps == lops:
                # Check positions of nodes' parents, starting from the root
                for spos, opos in zip(self._ppos.items(), other._ppos.items()):
                    sp, si = spos  # self
                    op, oi = opos  # other
                    if sp != op:  # Nodes' common ancestor is diverging
                        # Check which of the nodes' ancestors are closest to the root
                        return self._is_reverse(si < oi)
            # Node's parent path is longer
            return self._is_reverse(False)

        def __gt__(self, other):
            if not isinstance(other, RedBlackTreeMapping.HeapNode):
                return NotImplemented
            return not self < other

        def _is_reverse(self, val: bool) -> bool:
            """Reverse value. For use with a reverse iterator."""
            if self._reversed_:
                return not val
            return val

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
            _rbtm_iterable : Iterable[_rbtm_item]
                A tuple that must contain 3 or 4 items (`key`, `value`, `position`, `parents`), where `parents` may be omitted.
                    key : Hashable
                        Key to insert.
                    value : Any
                       Value mapped to `key`.
                    position : Iterable[int]
                        The index of `key` and all its parents in the mapping.
                        The last element of the iterable must be unique for all keys k, where k.parents == `key`.`parents`.
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
        self._prefix_msg = f"{self.__class__.__name__} '{self.name}'"
        self._key_count = 0
        self._structure_tracker = {}  # type: dict[str, tuple[str, list]]
        self._position_tracker = []
        self._modified = False
        self._dump_cache = None
        self.add_all(iterable)

    def __iter__(self) -> Generator[_rbtm_item, Any, None]:
        heap = MeldableHeap()
        for tn in super().__iter__():
            heap.add_all([RedBlackTreeMapping.HeapNode(*item) for item in tn])
        while heap:
            yield heap.remove().get()

    def __reversed__(self) -> Generator[_rbtm_item, Any, None]:
        heap = MeldableHeap(
            [RedBlackTreeMapping.HeapNode(*item, _reversed_=True) for item in self]
        )
        while heap:
            yield heap.remove().get()

    def __or__(self, other):
        if not isinstance(other, (Mapping, RedBlackTreeMapping)):
            return NotImplemented
        new = self.__new__(type(self))
        new.name = f"{self.name}-union"
        new.add_all([self, other])
        return new

    def __ror__(self, other):
        if not isinstance(other, Mapping):
            return NotImplemented
        new = self.__new__(type(self))
        new.name = f"{self.name}-union"
        new.add_all([other, self])
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
        except (ValueError, KeyError, LookupError):
            return False

    def __str__(self):
        return f"{self._prefix_msg} :-> (\n  nodes: {len(self)},\n  keys: {self._key_count},\n  positions: {self._position_tracker},\n  structure: {self._structure_tracker}\n)"

    def _create_node(self, *args, **kwargs) -> "RedBlackTreeMapping.TreeNode":
        return RedBlackTreeMapping.TreeNode(*args, **kwargs)

    def _raise_key_error(self, k, p, from_none: bool = True):
        e = KeyError(f"{self._prefix_msg}: Key ('{k}', '{p}') does not exist")
        if from_none:
            raise e from None
        else:
            raise e

    def _raise_lookup_error(self, k, p, tn, from_none: bool = True):
        e = LookupError(
            f"{self._prefix_msg}: Cannot uniquely identify a value for (key '{k}', parent '{p}')"
        )
        e.add_note(f"{self._prefix_msg}: Possible values are '{tn}'")
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
        """Returns True if `v` is nesting child nodes and thus should be serialized as a dict."""
        return (
            isinstance(v, Iterable)
            and v
            and isinstance(v[0], tuple)
            and v[0]
            and isinstance(v[0][0], RedBlackTreeMapping.TreeNode)
        )

    def _update_position(
        self,
        idx: int,
        key: Hashable,
        position: Iterable[int],
        parents: Iterable[Hashable],
    ) -> Iterable[int]:
        try:
            self._position_tracker[idx] += 1
        except IndexError:
            self._position_tracker.append(0)
        position[idx] = self._position_tracker[idx]
        pos_i = "".join([f"{v}" for v in position])
        self._structure_tracker[pos_i] = (key, parents)

    def _normalize_position(
        self, key: Hashable, position: Iterable[int], parents: Iterable[Hashable]
    ) -> Iterable[int]:
        """Ensure position of keys remain predictable during unions"""
        pos_i = "".join([f"{v}" for v in position])
        updated = False
        if pos_i in self._structure_tracker:
            key_i, ps_i = self._structure_tracker[pos_i]
            if len(parents) == len(ps_i) == 0:
                if key != key_i:
                    self._update_position(0, key, position, parents)
                    updated = True
            else:
                for i, p_i in enumerate(ps_i):
                    if parents[i] != p_i:
                        self._update_position(i, key, position, parents)
                        updated = True
                        break
        else:
            pos_len = len(position)
            current_pos = ""
            for j in range(pos_len - 1 if pos_len > 1 else pos_len):
                current_pos += f"{position[j]}"
                if current_pos in self._structure_tracker:
                    key_j, ps_j = self._structure_tracker[current_pos]
                    if key_j != parents[j]:
                        self._update_position(j, key, position, parents)
                        updated = True
                        break
                else:
                    self._update_position(j, key, position, parents)
                    updated = True
                    break
        # NOTE: If key is in _structure_tracker but their positions are different, position tracker will increment
        # E.g. key = (General, [1]), _structure_tracker = (General, [0]) | We do not check all positions in _structure_tracker for the key
        # This causes position tracker to become incorrect during unions, but does not affect tree operations (nor multiple unions)
        if not updated:
            self._update_position(len(parents), key, position, parents)

    def _find_index(
        self,
        key: Hashable,
        parent: Union[Hashable, Iterable[Hashable], None] = None,
        immediate: bool = False,
    ) -> tuple["RedBlackTreeMapping.TreeNode", int]:
        """
        Return the index of `key` and its TreeNode object.

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
            By default False.

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
            if len(tn) > 1:
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
                # Convert generic LookupError to informative version
                self._raise_lookup_error(key, parent, tn)
            except ValueError:
                self._raise_key_error(key, parent)
        return (tn, i)

    def find(
        self,
        key: Hashable,
        parent: Union[Hashable, Iterable[Hashable], None] = None,
        immediate: bool = False,
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
            By default False.

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
        return self._tree_dump(v) if self._check_value(v) else v

    def add_all(self, iterable: Iterable[_supports_rbtm_iter]):
        """
        Add elements in `iterable` to the tree.

        Parameters
        ----------
        iterable : Iterable[_supports_rbtm_iter]
            `iterable` may contain any of:
            _rbtm_iterable : Iterable[_rbtm_item]
                The tuple must contain 3 or 4 items (`key`, `value`, `position`, `parents`), where `parents` may be omitted.
                    key : Hashable
                        Key to insert.
                    value : Any
                        Value mapped to `key`.
                    position : Iterable[int]
                        The index of `key` and all its parents in the mapping.
                        The last element of the iterable must be unique for all keys k, where k.parents == `key`.`parents`.
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
                    self._add(*args)

    def _add(
        self,
        key: Hashable,
        value: Any,
        position: Iterable[int],
        parents: Iterable[Hashable] = [],
        *args,
        **kwargs,
    ) -> "RedBlackTreeMapping.TreeNode":
        self._modified = True
        self._normalize_position(key, position, parents)
        self._key_count += 1  # Update size
        tn = self._create_node(key, value, position, parents, *args, **kwargs)
        u = self._find_node(tn)  # type: RedBlackTreeMapping.TreeNode
        if u is None:  # Object is new
            super().add(tn)
            return tn
        else:  # Append to existing node
            u.add(key, value, position, parents)
            return u

    def add(
        self,
        key: Hashable,
        value: Any,
        position: Iterable[int],
        parents: Iterable[Hashable] = [],
        *args,
        **kwargs,
    ):
        """
        Add key-value pair to the tree.

        Parameters
        ----------
        key : Hashable
            Key to insert.

        value : Any
            Map value to `key`.

        position : Iterable[int]
            The index of `key` and all its parents in the mapping.
            The last element of the iterable must be unique for all keys k, where k.parents == `key`.`parents`.

        parents : Iterable[Hashable], optional
            Iterable of all `key`'s parents (a.k.a. ancestors).
            May be omitted from the tuple, resulting in a "flat" tree.
        """
        self._add(key, value, position, parents, *args, **kwargs)

    def _add_nested_mapping(
        self,
        key: Hashable,
        value: Any,
        position: Iterable[int],
        parents: Iterable[Hashable],
        *args,
        **kwargs,
    ) -> "RedBlackTreeMapping.TreeNode":
        """Change behavior of adding nested mappings in subclasses"""
        return self._add(
            key=key, value=[], position=position, parents=parents, *args, **kwargs
        )

    def add_mapping(self, m: Mapping):
        """
        Add all key-value pairs in `m` to this tree.

        Overwrites existing keys in this tree with keys from `m`.
        """
        if not m:
            return
        q = (
            deque()
        )  # type: deque[tuple[Mapping, list, list, tuple[RedBlackTreeMapping.TreeNode, list] | None]]
        q.append((m, [], [None], None))
        while q:
            d, ps, pos, tnp_tuple = q.popleft()
            for i, item in enumerate(d.items()):
                k, v = item
                c_pos = [*pos]
                c_pos[-1] = i

                # Add current key in mapping
                if isinstance(v, Mapping):
                    tn = self._add_nested_mapping(
                        key=k, value=v, position=c_pos, parents=ps
                    )
                    q.append((v, [*ps, k], [*c_pos, 0], (tn, ps)))
                else:
                    tn = self._add(key=k, value=v, position=c_pos, parents=ps)

                # Add reference to parent/child nodes
                if tnp_tuple is not None:
                    tnp, tnp_ps = tnp_tuple
                    # parent <- child
                    tnp.values[tnp.get_index(tnp_ps)].append((tn, ps))
                    # child <- parent
                    tn._parent_nodes[tn.get_index(ps)] = tnp

    def add_tree(self, t: Self):
        """
        Add all key-value pairs in `t` to this tree.

        Overwrites existing keys in this tree with keys from `t`.
        """
        for node in t:
            self.add(*node)

    def remove(
        self,
        key: Hashable,
        parent: Union[Hashable, Iterable[Hashable], None] = None,
        immediate: bool = False,
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
            By default False.

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
        self._modified = True
        tn, i = self._find_index(key, parent, immediate)
        if len(tn) < 2:  # At most one key in node, remove node entirely
            super().remove(tn)
        self._key_count -= 1  # Update size

        # Remove parent node's reference to this node, if any.
        ps = tn.parents[i]
        if ps:
            try:
                # tnp, ip = self._find_index(ps[-1], ps[:-2])
                tnp = tn._parent_nodes[i]  # type: RedBlackTreeMapping.TreeNode
                tnp.values.remove((tn, ps))
            except ValueError:
                pass
        return tn.remove(i)  # Remove key from the node's list

    def update(
        self,
        key: Hashable,
        value: Any,
        parent: Union[Hashable, Iterable[Hashable], None] = None,
        immediate: bool = False,
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
            By default False.

        Raises
        ------
        KeyError
            If the combination of (`key`,`parent`) does not exist.

        LookupError
            If a key-value pair can not be uniquely identified from (`key`,`parent`).
            Can happen if `parent` information is insufficient.
        """
        self._modified = True
        tn, i = self._find_index(key, parent, immediate)
        tn.values[i] = value

    def _tree_dump(self, items: Iterable[_rbtm_item]) -> dict[Hashable, Any]:
        """Generate a dictionary representation of `items`"""
        dump = {}
        heap = MeldableHeap([RedBlackTreeMapping.HeapNode(*item) for item in items])
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

    def dump(self) -> dict[Hashable, Any]:
        """
        Generate a dictionary representation of the tree.

        Returns
        -------
        dict[Hashable, Any]
            A dictionary representation of the tree.
        """
        if self._modified or self._dump_cache is None:
            self._dump_cache = self._tree_dump(self)
            self._modified = False
        return self._dump_cache
