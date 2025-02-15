from abc import abstractmethod
from typing import Any, Hashable, Iterable, Mapping, Optional, Self, override

from ...datastructures.pure.meldableheap import MeldableHeap
from ...datastructures.pure.skiplist import Skiplist
from ...datastructures.redblacktree_mapping import (
    RedBlackTreeMapping,
    _rbtm_item,
    _supports_rbtm_iter,
)
from ...tools.types.general import iconDict
from ..mapping_base import MappingBase
from ..tools.template_utils.options import GUIOption, Option


class BaseTemplate(MappingBase):
    def __init__(
        self,
        name: str,
        template: Mapping,
        icons: Optional[iconDict] = None,
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

        icons : Optional[icon_dict], optional
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
        return self.new(f"{self.name}-union", [self, other], None)

    def __ror__(self, other):
        if not isinstance(other, Mapping):
            return NotImplemented
        return self.new(f"{self.name}-union", [other, self], None)

    @classmethod
    def new(
        cls, name: str, iterable: list[_supports_rbtm_iter], icons: iconDict | None
    ) -> Self:
        """Let singleton subclasses create a new instance of their class"""
        new = super().__new__(cls)
        # This is called in a direct subclass. Thus, super() is actually calling this class
        super(type(new), new).__init__(name, [], icons)
        new.add_all(iterable)
        return new

    @override
    def _prefix_msg(self) -> str:
        return f"Template '{self.name}':"

    @override
    def _check_value(self, v) -> bool:
        try:
            return super()._check_value(v) and isinstance(v.x[0][0], Option)
        except Exception:
            return False

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
        if isinstance(value, Option) or self._check_value(value):
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

    @override
    def get_value(
        self, key, parents=[], default=None, search_mode="smart", errors="ignore"
    ) -> Option | GUIOption:
        return super().get_value(key, parents, default, search_mode, errors)

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
                        value.x
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
    def _create_template(self) -> dict: ...
