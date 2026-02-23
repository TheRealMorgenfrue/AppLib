from collections.abc import Hashable
from typing import Self

from ....logging import LoggingManager


class Group:
    _instances: dict[str, dict[Hashable, Self]] = {}
    _logger = None

    def __new__(cls, template_name: str, group_name: str) -> Self:
        """
        Specifies a relationship between parent and child settings.

        Create a new Group if another Group instance with the supplied template name
        and group name does not exist. Otherwise, return the existing instance.

        Parameters
        ----------
        template_name : str
            The name of the template this group belongs to.

        group_name : str
            The name of the group.

        Returns
        -------
        Self
            An instance (new or existing) of Group matching the template name and group name.
        """
        if cls._logger is None:
            # Lazy load the logger
            cls._logger = LoggingManager()

        if template_name not in cls._instances:
            cls._instances[template_name] = {}

        if group_name not in cls._instances[template_name]:
            instance = super().__new__(cls)
            instance._created = False
            cls._instances[template_name][group_name] = instance
        return cls._instances[template_name][group_name]

    def __init__(self, template_name: str, group_name: str):
        if not self._created:
            self._template_name = template_name
            self._group_name = group_name
            self._parent: str | None = None
            self._children: set[str] = set()

            # This group is a child of these groups
            self._parent_group_names = []

            self._created = True

    @classmethod
    def get_group(cls, template_name: str, ui_group: Hashable) -> Self | None:
        """
        Get the Group instance with name `ui_group`.

        Parameters
        ----------
        template_name : str
            The template in which to search for `ui_group`.

        ui_group : Hashable
            The ID of the Group to search for.

        Returns
        -------
        Self | None
             Returns Group instance if an instance with `ui_group` exists, otherwise None.
        """
        try:
            return cls._instances.get(template_name, None).get(ui_group, None)
        except AttributeError as err:
            err.add_note(
                f"Cause: Failed to get group '{ui_group}' because template '{template_name}' has no Group instance"
            )
            raise

    @classmethod
    def get_all_groups(cls, template_name: str):
        """Get all Group instances in `template_name`."""
        groups = cls._instances.get(template_name, None)
        return groups.values() if groups else None

    @classmethod
    def remove_group(cls, template_name: str, ui_group: str) -> None:
        """
        Remove `ui_group` from all Group instances in `template_name`.
        """
        group = cls._instances[template_name].pop(ui_group)
        # Remove group from any parent groups as well
        for parent in group._parent_group_names:
            parent_group = cls.get_group(template_name, parent)
            if parent_group:
                parent_group.remove_child(group.get_parent_name())
        group._parent_group_names.clear()

    def set_parent_group_names(self, parent_groups: list[str]) -> None:
        self._parent_group_names = parent_groups

    def get_parent_group_names(self) -> list[str]:
        return self._parent_group_names

    def get_group_name(self) -> str:
        return self._group_name

    def get_template_name(self) -> str:
        return self._template_name

    def set_parent_name(self, parent: str) -> None:
        self._parent = parent

    def get_parent_name(self) -> str | None:
        return self._parent

    def add_child_name(self, child: str) -> None:
        self._children.add(child)

    def remove_child(self, child: str | None) -> None:
        if child == None:
            return

        self._children.remove(child)

    def get_child_names(self):
        return self._children
