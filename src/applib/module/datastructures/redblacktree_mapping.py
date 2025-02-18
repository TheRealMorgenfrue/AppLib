from collections import deque
from typing import (
    Any,
    Generator,
    Hashable,
    Iterable,
    Literal,
    Mapping,
    Self,
    TypeAlias,
    Union,
)

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
            self.positions = Skiplist([pos])  # Tracks the order of keys
            self.parents = Skiplist([ps])  # Uniquely identifies keys

        def __iter__(self) -> Generator[_rbtm_item, Any, None]:
            attr = [
                v
                for k, v in self.__dict__.items()
                if k[:2].count("_") == 0
                and k[-2:].count("_") == 0
                and isinstance(v, Iterable)
                and not isinstance(v, Mapping)
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

        def _strict_index(self, parents: Iterable[Hashable]) -> list[int]:
            return [self.parents.index(parents)]  # ValueError

        def _smart_index(self, parents: Iterable[Hashable]) -> list[int]:
            if len(self.keys) == 1:
                return [0]

            try:
                return self._strict_index(parents)
            except ValueError:
                pass

            imm = self._immediate_index(parents)
            if len(imm) == 1:
                return imm
            anys = self._any_index(parents)
            if len(anys) == 1:
                return anys

            # TODO: Implement fuzzy matching of array values
            # E.g. ["a", "b", "c", "d"] == ["a", "b", "c"] iff im == False,
            #      ["a", "b", "c", "d"] == ["b", "c", "d"] iff im == True
            raise LookupError()

        def _immediate_index(self, parents: Iterable[Hashable]) -> list[int]:
            return [i for i, ps in enumerate(self.parents) if parents[-1] == ps[-1]]

        def _any_index(self, parents: Iterable[Hashable]) -> list[int]:
            idxs = []
            for i, ps in enumerate(self.parents):
                for p in parents:
                    if p in ps:
                        idxs.append(i)
            return idxs

        def index(
            self,
            parents: Iterable[Hashable],
            search_mode: Literal["strict", "smart", "immediate", "any"] = "smart",
        ) -> int:
            """
            Get index of `parents`.

            Parameters
            ----------
            parents : Union[Hashable, Iterable[Hashable]]
                The parents of `key`.

            search_mode : Literal["strict", "smart", "immediate", "any"], optional
                How to select keys.
                - "strict"
                    &ensp; Requires `parents` to match exactly.
                    I.e. ["a", "b"] == ["a", "b"]
                - "smart"
                    &ensp; Tries to find the key using different heuristics.
                    Note that it can result in the wrong key under certain conditions.
                - "immediate"
                    &ensp; Requires `parents` to be a Hashable that matches the closest parent.
                    I.e. "b" == ["a", "b"]
                - "any"
                    &ensp; Requires `parents` to be a Hashable that matches any parent.
                    I.e. "a" == ["a", "b"]

                By default "smart".

            Returns
            -------
            int
                The index of `parents`.

            Raises
            ------
            ValueError
                If `parents` does not exist.

            LookupError
                If `parents` cannot be uniquely identified.
                Can happen if `parents` is not an Iterable of all parents of the key.
            """
            match search_mode:
                case "strict":
                    i = self._strict_index(parents)
                case "smart":
                    i = self._smart_index(parents)
                case "immediate":
                    i = self._immediate_index(parents)
                case "any":
                    i = self._any_index(parents)
            if len(i) != 1:
                raise LookupError()
            return i[0]

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
                self.positions[i] = pos
                self.parents[i] = ps
            except ValueError:
                self.keys.append(k)
                self.values.append(v)
                self.positions.append(pos)
                self.parents.append(ps)
                self._parent_nodes.append(None)

        def remove(self, i: int) -> _rbtm_item:
            """Remove and return objects at index `i`."""
            # Do not return internal tree data
            self._parent_nodes.pop(i)
            return (
                self.keys.pop(i),
                self.values.pop(i),
                self.positions.pop(i),
                self.parents.pop(i),
            )

        def get(self, i: int) -> _rbtm_item:
            """Return objects at index `i`."""
            return (self.keys[i], self.values[i], self.positions[i], self.parents[i])

    class HeapNode:
        def __init__(
            self,
            k: Hashable,
            v: Any,
            pos: Iterable[int],
            ps: Iterable[Hashable],
        ):
            self.k = k
            self.v = v
            self.pos = pos
            self.ps = ps
            self._ppos = dict(
                zip([*ps, k], pos, strict=True)
            )  # Restores order of keys when sorting data

        def __lt__(self, other):
            if not isinstance(other, RedBlackTreeMapping.HeapNode):
                return NotImplemented

            lps, lops = len(self.ps), len(other.ps)
            if lps < lops:
                return True  # Node's parent path is shorter
            elif lps == lops:
                # Check positions of nodes' parents, starting from the root
                for spos, opos in zip(self._ppos.items(), other._ppos.items()):
                    sp, si = spos  # self
                    op, oi = opos  # other
                    if sp != op:  # Nodes' common ancestor is diverging
                        # The nodes' ancestors that are closest to the root
                        return si < oi
            return False  # Node's parent path is longer

        def get(self) -> _rbtm_item:
            return (self.k, self.v, self.pos, self.ps)

    class ReversedHeapNode(HeapNode):
        def __init__(
            self,
            k: Hashable,
            v: Any,
            pos: Iterable[int],
            ps: Iterable[Hashable],
        ):
            super().__init__(k, v, pos, ps)

        def __lt__(self, other):
            return not super().__lt__(other)

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
            - _rbtm_iterable : Iterable[_rbtm_item]
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
            - Mapping
                Any class supporting the Mapping interface for providing key-value pairs.
            - RedBlackTreeMapping
                An instance of this class.

        name : str, optional
            Give the tree a name for easier identification.
            By default "".
        """
        super().__init__()
        self.name = name
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
            [RedBlackTreeMapping.ReversedHeapNode(*item) for item in self]
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
        return f"{self._prefix_msg()} (\n  nodes: {len(self)},\n  keys: {self._key_count},\n  positions: {self._position_tracker}\n)"  # ,\n  structure: {self._structure_tracker}\n)"

    def _create_node(self, *args, **kwargs) -> "RedBlackTreeMapping.TreeNode":
        return RedBlackTreeMapping.TreeNode(*args, **kwargs)

    def _prefix_msg(self) -> str:
        return f"{self.__class__.__name__} '{self.name}':"

    def _raise_key_error(self, k, p, from_none: bool = True):
        e = KeyError(f"{self._prefix_msg()} Key ('{k}', '{p}') does not exist")
        if from_none:
            raise e from None
        else:
            raise e

    def _raise_lookup_error(self, k, p, tn, from_none: bool = True):
        e = LookupError(
            f"{self._prefix_msg()} Cannot uniquely identify a value for key ('{k}', '{p}')"
        )
        e.add_note(f"Possible values: {tn}")
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
        k, p, mode = key, None, "smart"
        if isinstance(key, (tuple)):
            try:
                if len(key) == 2:
                    k, p = key
                else:  # len(key) == 3
                    k, p, mode = key
            except ValueError as e:
                e.add_note(
                    f"tuple must contain 1-3 items (key, parent, search_mode), where key is required. "
                    + "Type: tuple[Hashable, Hashable, Literal['strict', 'smart', 'immediate', 'any']]"
                )
                raise e from None
        return k, p, mode

    def _check_value(self, v) -> bool:
        """Returns True if `v` is nesting child nodes and thus should be serialized as a dict."""
        return isinstance(v, RedBlackTree.Node)

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

    def _remove_position(self, position: Iterable[int]):
        pos_i = "".join([f"{v}" for v in position])
        try:
            self._structure_tracker.pop(pos_i)
            self._position_tracker[len(position) - 1] -= 1
        except (KeyError, IndexError):
            pass

    def _create_subtree(self, node: RedBlackTree.Node) -> list[_rbtm_item]:
        subtree = []
        q = deque(
            node.x
        )  # type: deque[tuple[RedBlackTreeMapping.TreeNode, Iterable[Hashable]]]
        while q:
            tn, ps = q.popleft()
            u = tn.values[tn.index(ps)]
            if self._check_value(u):
                for cn, cps in u.x:
                    q.append((cn, cps))
            subtree.append(tn.get(tn.index(ps, "strict")))
        return subtree

    def _find_index(
        self,
        key: Hashable,
        parents: Union[Hashable, Iterable[Hashable]] = [],
        search_mode: Literal["strict", "smart", "immediate", "any"] = "smart",
    ) -> tuple["RedBlackTreeMapping.TreeNode", int]:
        """
        Return the index of `key` and its TreeNode object.

        Parameters
        ----------
        key : Hashable
            The key to look for.

        parents : Hashable | Iterable[Hashable], optional
            The parents of `key`.
            By default [].

        search_mode : Literal["strict", "smart", "immediate", "any"], optional
            How to select keys.
            - "strict"
                &ensp; Requires `parents` to match exactly.
                I.e. ["a", "b"] == ["a", "b"]
            - "smart"
                &ensp; Tries to find the key using different heuristics.
                Note that it can result in the wrong key under certain conditions.
            - "immediate"
                &ensp; Requires `parents` to be a Hashable that matches the closest parent.
                I.e. "b" == ["a", "b"]
            - "any"
                &ensp; Requires `parents` to be a Hashable that matches any parent.
                I.e. "a" == ["a", "b"]

            By default "smart".

        Returns
        -------
        tuple[RedBlackTreeMapping.TreeNode, int]
            The TreeNode which contains `key` at index.

        Raises
        ------
        KeyError
            If the combination of (`key`,`parents`) does not exist.

        LookupError
            If a key-value pair can not be uniquely identified from (`key`,`parents`).
            Can happen if `parents` information is insufficient.
        """
        if not isinstance(parents, Iterable):
            parents = [parents]

        tn = self._create_node(key, None, None, parents)
        u = self._find_node(tn)  # type: RedBlackTreeMapping.TreeNode | None
        if u is None:
            self._raise_key_error(key, parents)
        try:
            i = u.index(parents, search_mode)
        except LookupError:
            # Convert generic LookupError to informative version
            self._raise_lookup_error(key, parents, u)
        except ValueError:
            self._raise_key_error(key, parents)
        return (u, i)

    def find(
        self,
        key: Hashable,
        parents: Union[Hashable, Iterable[Hashable]] = [],
        search_mode: Literal["strict", "smart", "immediate", "any"] = "smart",
    ) -> Any:
        """
        Return the value for `key`.

        Parameters
        ----------
        key : Hashable
            The key to look for.

        parents : Hashable | Iterable[Hashable], optional
            The parents of `key`.
            By default [].

        search_mode : Literal["strict", "smart", "immediate", "any"], optional
            How to search for `key`.
            - "strict"
                &ensp; Requires `parents` to match exactly.
                I.e. ["a", "b"] == ["a", "b"]
            - "smart"
                &ensp; Tries to find the key using different heuristics.
                Note that it can result in the wrong key under certain conditions.
            - "immediate"
                &ensp; Requires `parents` to be a Hashable that matches the closest parent.
                I.e. "b" == ["a", "b"]
            - "any"
                &ensp; Requires `parents` to be a Hashable that matches any parent.
                I.e. "a" == ["a", "b"]

            By default "smart".

        Raises
        ------
        KeyError
            If the combination of (`key`,`parents`) does not exist.

        LookupError
            If a key-value pair can not be uniquely identified from (`key`,`parents`).
            Can happen if `parents` information is insufficient.
        """
        tn, i = self._find_index(key, parents, search_mode)
        v = tn.values[i]
        return self._tree_dump(self._create_subtree(v)) if self._check_value(v) else v

    def add_all(self, iterable: Iterable[_supports_rbtm_iter]):
        """
        Add elements in `iterable` to the tree.

        Parameters
        ----------
        iterable : Iterable[_supports_rbtm_iter]
            `iterable` may contain any of:
            - _rbtm_iterable : Iterable[_rbtm_item]
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
            - Mapping :
                Any class supporting the Mapping interface for providing key-value pairs.
            - RedBlackTreeMapping :
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
        __normalize___=True,
        **kwargs,
    ) -> "RedBlackTreeMapping.TreeNode":
        self._modified = True
        if __normalize___:
            self._normalize_position(key, position, parents)
            self._key_count += 1  # Update size
        tn = self._create_node(key, value, position, parents, *args, **kwargs)
        if super().add(tn):  # Object is new
            return tn
        else:  # Append to existing node
            u = self._find_node(tn)  # type: RedBlackTreeMapping.TreeNode
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

    def add_mapping(self, m: Mapping):
        """
        Add all key-value pairs in `m` to this tree.

        Overwrites existing keys in this tree with keys from `m`.
        """
        if not m:
            return
        q = deque(
            [(m, [], [None], None)]
        )  # type: deque[tuple[Mapping, list, list, tuple[RedBlackTreeMapping.TreeNode, list] | None]]
        while q:
            d, ps, pos, tnp_tuple = q.popleft()
            for i, item in enumerate(d.items()):
                k, v = item
                c_pos = [*pos]
                c_pos[-1] = i

                tn = self._add(key=k, value=v, position=c_pos, parents=ps)
                if isinstance(v, Mapping):
                    tn.values[tn.index(ps)] = RedBlackTree.Node([])
                    q.append((v, [*ps, k], [*c_pos, 0], (tn, ps)))

                # Add reference to parent/child nodes
                if tnp_tuple is not None:
                    tnp, tnp_ps = tnp_tuple
                    # parent <- child
                    tnp.values[tnp.index(tnp_ps)].x.append((tn, ps))
                    # child <- parent
                    tn._parent_nodes[tn.index(ps)] = tnp_tuple

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
        parents: Union[Hashable, Iterable[Hashable]] = [],
        search_mode: Literal["strict", "smart", "immediate", "any"] = "smart",
    ) -> tuple[Hashable, Any, Hashable]:
        """
        Remove and return a key-value pair from this tree.

        Parameters
        ----------
        key : Hashable
            Key-value pair to remove.

        parents : Hashable | Iterable[Hashable], optional
            The parents of `key`.
            By default [].

        search_mode : Literal["strict", "smart", "immediate", "any"], optional
            How to search for `key`.
            - "strict"
                &ensp; Requires `parents` to match exactly.
                I.e. ["a", "b"] == ["a", "b"]
            - "smart"
                &ensp; Tries to find the key using different heuristics.
                Note that it can result in the wrong key under certain conditions.
            - "immediate"
                &ensp; Requires `parents` to be a Hashable that matches the closest parent.
                I.e. "b" == ["a", "b"]
            - "any"
                &ensp; Requires `parents` to be a Hashable that matches any parent.
                I.e. "a" == ["a", "b"]

            By default "smart".

        Returns
        -------
        tuple[Hashable, Any, Hashable]
            A tuple of (`key`, `value`, `parents`).

        Raises
        ------
        KeyError
            If the combination of (`key`,`parents`) does not exist.

        LookupError
            If a key-value pair can not be uniquely identified from (`key`,`parents`).
            Can happen if `parents` information is insufficient.
        """
        self._modified = True
        tn, i = self._find_index(key, parents, search_mode)
        if len(tn) < 2:  # At most one key in node, remove node entirely
            super().remove(tn)
        self._key_count -= 1  # Update size

        # Remove parent node's reference to this node, if any.
        ps = tn.parents[i]
        if ps:
            try:
                tnp = tn._parent_nodes[i]  # type: RedBlackTreeMapping.TreeNode
                tnp.values.remove((tn, ps))
            except (ValueError, AttributeError):
                pass

        # Remove child nodes, if any
        node = tn.values[i]
        if self._check_value(node):
            for cn, cps in node.x:
                self.remove(cn.keys[cn.index(cps, "strict")], cps, "strict")

        # Adjust position counter
        self._remove_position(tn.positions[i])
        return tn.remove(i)  # Remove key from the node's list

    def update(
        self,
        key: Hashable,
        value: Any,
        parents: Union[Hashable, Iterable[Hashable]] = [],
        search_mode: Literal["strict", "smart", "immediate", "any"] = "smart",
    ):
        """
        Update value of `key` with `value`.

        Parameters
        ----------
        key : Hashable
            The key to look for.

        value : Any
            Map value to `key`.

        parents : Hashable | Iterable[Hashable], optional
            The parent of `key`.
            By default [].

        search_mode : Literal["strict", "smart", "immediate", "any"], optional
            How to search for `key`.
            - "strict"
                &ensp; Requires `parents` to match exactly.
                I.e. ["a", "b"] == ["a", "b"]
            - "smart"
                &ensp; Tries to find the key using different heuristics.
                Note that it can result in the wrong key under certain conditions.
            - "immediate"
                &ensp; Requires `parents` to be a Hashable that matches the closest parent.
                I.e. "b" == ["a", "b"]
            - "any"
                &ensp; Requires `parents` to be a Hashable that matches any parent.
                I.e. "a" == ["a", "b"]

            By default "smart".

        Raises
        ------
        KeyError
            If the combination of (`key`,`parents`) does not exist.

        LookupError
            If a key-value pair can not be uniquely identified from (`key`,`parents`).
            Can happen if `parents` information is insufficient.
        """
        if isinstance(value, (Mapping, RedBlackTreeMapping)):
            self.add_all([value])
        else:
            tn, i = self._find_index(key, parents, search_mode)
            tn.values[i] = value
        self._modified = True

    def rename(
        self,
        new_key: Hashable,
        key: Hashable,
        parents: Union[Hashable, Iterable[Hashable]] = [],
        search_mode: Literal["strict", "smart", "immediate", "any"] = "smart",
    ):
        """
        Rename `key` to `new_key` while preserving order.

        Parameters
        ----------
        new_key : Hashable
            The new name of `key`.

        key : Hashable
            The key to look for.

        parents : Hashable | Iterable[Hashable], optional
            The parent of `key`.
            By default [].

        search_mode : Literal["strict", "smart", "immediate", "any"], optional
            How to search for `key`.
            - "strict"
                &ensp; Requires `parents` to match exactly.
                I.e. ["a", "b"] == ["a", "b"]
            - "smart"
                &ensp; Tries to find the key using different heuristics.
                Note that it can result in the wrong key under certain conditions.
            - "immediate"
                &ensp; Requires `parents` to be a Hashable that matches the closest parent.
                I.e. "b" == ["a", "b"]
            - "any"
                &ensp; Requires `parents` to be a Hashable that matches any parent.
                I.e. "a" == ["a", "b"]

            By default "smart".

        Raises
        ------
        KeyError
            If the combination of (`key`,`parents`) does not exist.

        LookupError
            If a key-value pair can not be uniquely identified from (`key`,`parents`).
            Can happen if `parents` information is insufficient.
        """
        tn, i = self._find_index(key, parents, search_mode)
        if len(tn) < 2:  # At most one key in node, remove node entirely
            super().remove(tn)

        pn_tuple = tn._parent_nodes[
            i
        ]  # type: tuple[RedBlackTreeMapping.TreeNode, list[Hashable]]
        pn, pnps = pn_tuple
        k, v, pos, ps = tn.remove(i)
        new_tn = self._add(new_key, v, pos, ps, __normalize___=False)
        new_tn._parent_nodes[new_tn.index(ps, "strict")] = pn  # Add parent to child
        pn_value = pn.values[pn.index(pnps, "strict")]
        pn_value[pn_value.index((tn, ps))] = new_tn  # Add child to parent

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
                stack[-1][k] = v
            else:
                dump[k] = v
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

    def keys(self) -> list[Hashable]:
        """A list of this tree's keys, ordered by position."""
        return [k for k, v, pos, ps in self]

    def values(self) -> list[Any]:
        """A list of this tree's values, ordered by position."""
        return [v for k, v, pos, ps in self]

    def items(self) -> list[tuple[Hashable, Any]]:
        """A list of this tree's key-value pairs, ordered by position."""
        return [(k, v) for k, v, pos, ps in self]
