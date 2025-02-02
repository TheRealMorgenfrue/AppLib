from abc import abstractmethod
from typing import Any, Hashable, Iterable, Mapping, Optional, Union, override

from PyQt6.QtGui import QIcon
from qfluentwidgets import FluentIconBase

from ...datastructures.pure.meldableheap import MeldableHeap
from ...datastructures.pure.skiplist import Skiplist
from ...datastructures.redblacktree_mapping import RedBlackTreeMapping, _rbtm_item
from ...tools.utilities import checkDictNestingLevel
from ..mapping_base import MappingBase


class BaseTemplate(MappingBase):
    def __init__(
        self,
        name: str,
        template: Mapping,
        icons: Optional[dict[str, Union[str, QIcon, FluentIconBase]]] = None,
    ) -> None:
        """
        Base class for all templates.

        Parameters
        ----------
        name : str
            Template name.
            Uniquely identifies this template.

        template : Mapping
            A mapping of key-value pairs.

        icons : Optional[dict[str, Union[str, QIcon, FluentIconBase]]], optional
            A mapping of icons to keys in `template`.
            By default None.
        """
        self.icons = icons
        self._settings = Skiplist()
        self._settings_cache = None
        super().__init__([template], name)

    def __or__(self, other):
        if not isinstance(other, (Mapping, RedBlackTreeMapping)):
            return NotImplemented
        new = super().__new__(type(self))
        super(type(new), new).__init__(f"{self.name}-union", [], None)
        new.add_all([self, other])
        return new

    def __ror__(self, other):
        if not isinstance(other, Mapping):
            return NotImplemented
        new = super().__new__(type(self))
        super(type(new), new).__init__(f"{self.name}-union", [], None)
        new.add_all([other, self])
        return new

    @override
    def _prefix_msg(self) -> str:
        return f"Template '{self.name}':"

    @override
    def _add(
        self,
        key: Hashable,
        value: Any,
        position: Iterable[int],
        parents: Iterable[Hashable] = [],
        *args,
        **kwargs,
    ):
        is_setting = False
        if isinstance(value, Mapping):
            # A setting mapping has a nesting level of exactly 0
            if checkDictNestingLevel(value, 0):
                is_setting = True
        elif self._check_value(value):
            # A setting tree node has a nesting level of exactly 1
            v = value[
                0
            ]  # type: tuple[RedBlackTreeMapping.TreeNode, Iterable[Hashable]]
            tn, ps = v
            if not self._check_value(tn.values[tn.index(ps)]):
                is_setting = True
        if is_setting:
            self._settings.append((key, value, position, parents))
        return super()._add(key, value, position, parents, *args, **kwargs)

    @override
    def remove(self, key, parent=None, immediate=True):
        tn, i = self._find_index(key, parent, immediate)
        if len(tn) < 2:
            try:
                self._settings.remove(tn)
            except ValueError:
                pass
        return super().remove(key, parent, immediate)

    def get_settings(self) -> list[_rbtm_item]:
        """
        Get settings with corresponding options as specified in the template documentation.

        Returns
        -------
        list[dict[Hashable, Any]]
            A position-prioritised list of settings.
        """
        if self._modified or self._settings_cache is None:
            heap = MeldableHeap(
                [RedBlackTreeMapping.HeapNode(*item) for item in self._settings]
            )
            d_settings = []
            while heap:
                h_node = heap.remove()  # type: RedBlackTreeMapping.HeapNode
                key, value, pos, ps = h_node.get()
                dump = {key: {}}
                if self._check_value(value):
                    v = (
                        value
                    )  # type: list[tuple[RedBlackTreeMapping.TreeNode, Iterable[Hashable]]]
                    for tn, tn_ps in v:
                        c_k, c_v, c_i, c_ps = tn.get(tn.index(tn_ps))
                        dump[key][c_k] = c_v
                else:
                    dump[key] = value
                d_settings.append((key, dump, pos, ps))
            self._settings_cache = d_settings
        return self._settings_cache

    @abstractmethod
    def _createTemplate(self) -> dict: ...
