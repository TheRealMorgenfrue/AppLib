from abc import abstractmethod

from applib.module.configuration.tools.search.nested_dict_search import NestedDictSearch

from ..mapping_base import MappingBase


class BaseTemplate(MappingBase):
    def __init__(
        self,
        name: str,
        template: dict,
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
        """
        super().__init__(template)
        self.name = name

    def __or__(self, other):
        if not isinstance(other, (BaseTemplate)):
            return NotImplemented
        d = {}
        for instance in [self, other]:
            for k, v, path in instance.options():
                NestedDictSearch.insert(d, k, v, path, create_missing=True)

        template = super().__new__(BaseTemplate)
        template.__init__(f"{self.name}-union", d)
        return template

    def __ror__(self, other):
        if not isinstance(other, BaseTemplate):
            return NotImplemented
        d = {}
        for instance in [other, self]:
            for k, v, path in instance.options():
                NestedDictSearch.insert(d, k, v, path, create_missing=True)

        template = super().__new__(BaseTemplate)
        template.__init__(f"{other.name}-union", d)
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
