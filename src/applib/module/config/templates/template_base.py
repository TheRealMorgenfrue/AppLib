from abc import abstractmethod
from copy import deepcopy
from typing import Any, Optional, Self, Union

from qfluentwidgets import FluentIconBase
from PyQt6.QtGui import QIcon


from ...logging import logger
from ...tools.types.general import NestedDict
from ...tools.utilities import retrieveDictValue


class BaseTemplate:
    """Base class for all templates"""

    _logger = logger

    def __init__(
        self,
        template_name: str,
        template: NestedDict,
        icons: Optional[dict[str, Union[str, QIcon, FluentIconBase]]] = None,
    ) -> None:
        self._template_name = template_name
        self._template = template
        self._icons = icons

    @classmethod
    def createSubTemplate(
        cls,
        template_name: str,
        template: NestedDict,
        icons: dict[str, Union[str, QIcon, FluentIconBase]],
    ) -> Self:
        instance = super().__new__(cls)
        instance._template_name = template_name
        instance._template = deepcopy(template)
        instance._icons = icons
        return instance

    def getValue(self, key: str, parent_key: str = None, default: Any = None) -> Any:
        """Return first value found. If there is no item with that key, return
        default.

        Has support for defining search scope with the parent key.
        A value will only be returned if it is within parent key's scope.
        """
        value = retrieveDictValue(d=self.getTemplate(), key=key, parent_key=parent_key)
        if value is None:
            if parent_key:
                self._logger.warning(
                    f"Could not find key '{key}' inside the scope of parent key '{parent_key}' in the template. "
                    + f"Returning default: '{default}'"
                )
            else:
                self._logger.warning(
                    f"Could not find key '{key}' in the template. Returning default: '{default}'"
                )
        return default if value is None else value

    def getTemplate(self) -> NestedDict:
        return self._template

    def getName(self) -> str:
        return self._template_name

    def getIcons(self) -> dict[str, Union[str, QIcon, FluentIconBase]] | None:
        return self._icons

    def setName(self, name: str) -> None:
        self._template_name = name

    @abstractmethod
    def _createTemplate(self) -> NestedDict: ...
