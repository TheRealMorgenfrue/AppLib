from abc import abstractmethod

from applib.module.configuration.tools.search.nested_dict_search import NestedDictSearch

from ...tools.types.general import iconDict
from ..mapping_base import MappingBase


class BaseTemplate(MappingBase):
    def __init__(
        self,
        name: str,
        template: dict,
        icons: iconDict | None = None,
    ) -> None:
        """
        Base class for all templates.

        Parameters
        ----------
        name : str
            Template name.
            Uniquely identifies this template.

        template : dict
            The dict representing the template.

        icons : icon_dict, optional
            A mapping of icons to keys in `template`.
            By default None.
        """
        super().__init__(template)
        self.icons = icons  # TODO: Add full icon support to templates in AppLib
        self.name = name

    def __or__(self, other):
        if not isinstance(other, (BaseTemplate)):
            return NotImplemented
        d = {}
        for instance in [self, other]:
            for k, v, path in instance.options():
                NestedDictSearch.insert(d, k, v, path, create_missing=True)

        # TODO: Reimplement when icon support is added
        if self.icons:
            if other.icons:
                icons = self.icons | other.icons
            icons = self.icons
        else:
            icons = other.icons  # Maybe None

        template = super().__new__(BaseTemplate)  # type: ignore
        template.__init__(f"{self.name}-union", d, icons)
        return template

    def __ror__(self, other):
        if not isinstance(other, BaseTemplate):
            return NotImplemented
        d = {}
        for instance in [other, self]:
            for k, v, path in instance.options():
                NestedDictSearch.insert(d, k, v, path, create_missing=True)

        # TODO: Reimplement when icon support is added
        if other.icons:
            if self.icons:
                icons = other.icons | self.icons
            icons = other.icons
        else:
            icons = self.icons  # Maybe None

        template = super().__new__(BaseTemplate)  # type: ignore
        template.__init__(f"{other.name}-union", d, icons)
        return template

    def __ior__(self, other):
        if not isinstance(other, (BaseTemplate)):
            return NotImplemented
        for k, v, path in other.options():
            NestedDictSearch.insert(self._dict, k, v, path, create_missing=True)
        return self

    def _prefix_msg(self) -> str:
        return f"Template '{self.name}':"

    @abstractmethod
    def _create_template(self) -> dict: ...

    def get_template(self) -> dict:
        return self._dict
