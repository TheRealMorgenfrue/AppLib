from abc import abstractmethod
from typing import Mapping, Optional, Self, override

from ...datastructures.redblacktree_mapping import (
    RedBlackTreeMapping,
    _rbtm_item,
    _supports_rbtm_iter,
)
from ...tools.types.general import iconDict
from ..mapping_base import MappingBase
from ..tools.template_utils.options import Option


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
        self.icons = icons  # TODO: Add full icon support to templates in AppLib
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
        """Let direct singleton subclasses create a new instance of their class"""
        new = super().__new__(cls)
        # This is called in a direct subclass. Thus, super() is actually calling this class
        super(type(new), new).__init__(name, [], icons)
        new.add_all(iterable)
        return new

    @override
    def _is_setting(self, item: _rbtm_item) -> bool:
        check = False
        k, v, pos, ps = item
        try:
            check = isinstance(v, Option)
            check = check or isinstance(v.x[0][0], Option)
        except Exception:
            pass
        return check

    @override
    def _prefix_msg(self) -> str:
        return f"Template '{self.name}':"

    @abstractmethod
    def _create_template(self) -> dict: ...
