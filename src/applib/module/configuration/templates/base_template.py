from abc import abstractmethod
from typing import Mapping, Optional, Union

from PyQt6.QtGui import QIcon
from qfluentwidgets import FluentIconBase

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
        super().__init__([template], name)
        self.icons = icons

    def _prefix_msg(self) -> str:
        return f"Template {self.name}:"

    @abstractmethod
    def _createTemplate(self) -> dict: ...
