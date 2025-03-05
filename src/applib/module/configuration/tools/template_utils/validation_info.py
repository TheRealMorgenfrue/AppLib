from typing import Any, Callable, Generator, Hashable, Iterable, override

from ....datastructures.pure.meldableheap import MeldableHeap
from ....datastructures.pure.redblacktree import RedBlackTree
from ....datastructures.redblacktree_mapping import RedBlackTreeMapping
from ....logging import AppLibLogger


class ValidationTree(RedBlackTreeMapping):
    class ValidationNode(RedBlackTreeMapping.TreeNode):
        def __init__(
            self,
            setting: Hashable,
            value: Any,
            position: list[int],
            parents: Iterable[Hashable],
            validator: Callable,
        ):
            super().__init__(setting, value, position, parents)
            self._idx = f"{parents}{validator}".encode(errors="replace")
            self.validator = validator

    def __init__(self, iterable=[], name=""):
        super().__init__(iterable, name)

    def __iter__(self) -> Generator[ValidationNode, Any, None]:
        return super(RedBlackTree, self).__iter__()

    @override
    def _create_node(self, *args, **kwargs):
        return ValidationTree.ValidationNode(*args, **kwargs)


class FieldTree(RedBlackTreeMapping):
    class FieldNode(RedBlackTreeMapping.TreeNode):
        def __init__(
            self,
            setting: Hashable,
            value: Any,
            position: list[int],
            parents: Iterable[Hashable],
        ):
            super().__init__(setting, value, position, parents)
            self._idx = f"{parents if parents else setting}".encode(errors="replace")
            try:
                self.fields = dict(value)
            except TypeError:
                self.fields = {}

        @override
        def add(self, k, v, pos, ps):
            self.fields |= v
            return super().add(k, v, pos, ps)

        @override
        def remove(self, i):
            k, v, pos, ps = super().remove(i)
            try:
                self.fields.pop(next(iter(v.keys())))
            except KeyError:
                pass
            return k, v, pos, ps

    _logger = AppLibLogger().get_logger()

    def __init__(self, iterable=[], name=""):
        super().__init__(iterable, name)

    def __iter__(self) -> Generator[FieldNode, Any, None]:
        return super(RedBlackTree, self).__iter__()

    def __reversed__(
        self,
    ) -> Generator[tuple[str, dict, Iterable[Hashable]], Any, None]:
        heap = MeldableHeap(
            [
                RedBlackTreeMapping.ReversedHeapNode(
                    k=node.keys[0], v=node, pos=node.positions[0], ps=node.parents[0]
                )
                for node in self
            ]
        )
        while heap:
            h_node = heap.remove()  # type: RedBlackTreeMapping.ReversedHeapNode
            k, v, pos, ps = h_node.get()
            f_node = v  # type: FieldTree.FieldNode
            yield k, f_node.fields, pos, ps

    @override
    def _create_node(self, *args, **kwargs):
        return FieldTree.FieldNode(*args, **kwargs)

    @override
    def _normalize_position(self, key, position, parents):
        pass

    def dump_fields(self) -> dict:
        """Generate a dictionary representation of fields"""
        dump = {}
        heap = MeldableHeap(
            [
                RedBlackTreeMapping.HeapNode(
                    node.keys[0], node.fields, node.positions[0], node.parents[0]
                )
                for node in self
            ]
        )
        while heap:
            node = heap.remove()  # type: RedBlackTreeMapping.HeapNode
            k, v, i, ps = node.get()
            dump |= v
        return dump

    def merge(
        self,
        setting: Hashable,
        value: Any,
        position: list[int],
        parents: list[Hashable],
    ):
        """
        Merge `setting`'s node with its parent node and remove `setting`'s node.

        `value` is the value of `setting` which is retained in the parent of `setting`.
        """
        if parents:
            key = parents[-1]
            try:
                ps = parents[:-1]
            except IndexError:
                ps = []
            try:
                pos = position[:-1]
            except IndexError:
                pos = position[-1]
            self.remove(setting, parents)
            self.add(key, value, pos, ps)
        else:
            self._logger.warning(f"Cannot merge node '{setting}' with no parents")


class ValidationInfo:
    def __init__(self) -> None:
        self.fields = FieldTree()
        self.validators = ValidationTree()

    def add_field(
        self,
        setting: Hashable,
        field: dict,
        position: list[int],
        parents: list[Hashable],
    ):
        self.fields.add(setting, field, position, parents)

    def add_setting_validation(
        self,
        setting: Hashable,
        position: list[int],
        parents: list[Hashable],
        validators: list[Callable],
    ):
        for validator in validators:
            self.validators.add(setting, None, position, parents, validator=validator)
