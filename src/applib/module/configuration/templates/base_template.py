from abc import abstractmethod
from copy import deepcopy
from typing import Any, Mapping, Optional, Self, Union

from qfluentwidgets import FluentIconBase
from PyQt6.QtGui import QIcon

from ..mapping_base import MappingBase
from ...tools.utilities import retrieveDictValue, insertDictValue


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

    def _prefixMsg(self) -> str:
        return f"Template {self.name}:"

    @abstractmethod
    def _createTemplate(self) -> dict: ...
