from typing import Any, Iterable, Self

from ....logging import AppLibLogger
from ....tools.types.gui_cardgroups import AnyCardGroup
from ....tools.types.gui_cards import AnyCard, AnyParentCard
from ....tools.utilities import iter_to_str
from .template_enums import UIGroups


class Group:
    _instances: dict[str, dict[str, Self]] = {}
    _logger = AppLibLogger().get_logger()

    def __new__(cls, template_name: str, group_name: str) -> Self:
        """Specifies a relationship between parent and child settings.

        Create a new Group if another Group instance with the supplied template name
        and group name does not exist. Otherwise, return the existing instance.

        Parameters
        ----------
        template_name : str
            The name of the template this group belongs to

        group_name : str
            The name of the group

        Returns
        -------
        Self
            An instance (new or existing) of Group matching the template name and group name
        """
        if not template_name in cls._instances:
            cls._instances[template_name] = {}

        if not group_name in cls._instances[template_name]:
            instance = super().__new__(cls)
            instance._template_name = template_name
            instance._group_name = group_name
            instance._parent = {}  # Type: dict[str, AnyParentCard]
            instance._children = {}  # Type: dict[str, AnyCard]
            instance._ui_group_parent = None
            instance._parent_card_group = None  # The card group which this parent could be a child of - if its nesting level is 0
            instance._child_card_groups = (
                {}
            )  # If children of this group are not nested under a parent, they should be added to their original card group
            instance._parent_group_names = []  # This group is a child of these groups
            instance._nesting_level = (
                -1
            )  # How many parent groups want to nest this group. A nesting_level of -1 means it is unknown.
            instance._isNestingChildren = False
            cls._instances[template_name][group_name] = instance
        return cls._instances[template_name][group_name]

    @classmethod
    def get_group(cls, template_name: str, ui_group: str) -> Self | None:
        """Get group instance matching the *ui_group* ID

        Parameters
        ----------
        template_name : str
            The template in which to search for the *ui_group* ID

        ui_group : str
            The ID of the Group to search for

        Returns
        -------
        Self | None
             Returns Group instance if an instance with the *ui_group* ID exists, otherwise None
        """
        try:
            return cls._instances.get(template_name, None).get(ui_group, None)
        except AttributeError as err:
            err.add_note(
                f"Cause: Failed to get group '{ui_group}' because template '{template_name}' has no Group instance"
            )
            raise

    @classmethod
    def get_all_groups(cls, template_name: str) -> Iterable[Self] | None:
        groups = cls._instances.get(template_name, None)
        if groups:
            groups = groups.values()
        return groups

    @classmethod
    def remove_group(cls, template_name: str, ui_group: str) -> None:
        group = cls._instances[template_name].pop(ui_group)
        # Remove group from any parent groups as well
        for parent in group._parent_group_names:
            parent_group = cls.get_group(template_name, parent)
            if parent_group:
                parent_group.remove_child(group.get_parent_name())
        group._parent_group_names.clear()

    def enforce_logical_nesting(self) -> None:
        """
        Check wether multiple parent groups want to nest this child group and resolve this issue.
        Only the first parent group detected is allowed to nest this group as their child.
        All other parent groups have their reference to this child group deleted.
        """
        if self._nesting_level < 0:
            self._nesting_level = 0  # Set initial nesting level. 0 means no nesting

            # Ask all parent groups of this group if they want to nest this group
            for parent_group_name in self._parent_group_names:
                if self.get_group(
                    self._template_name, parent_group_name
                ).getParentNestingPolicy():
                    self._nesting_level += 1

            # A nesting_level above 1 indicates a problem; multiple parents want to nest this child.
            if self._nesting_level > 1:
                self._logger.warning(
                    f"Group '{self.get_group_name()}': Multiple parents want to nest this UI group. "
                    + f"Only the first parent in the list '{iter_to_str(self._parent_group_names, separator=", ")}' "
                    + f"will be allowed nesting."
                )
                # Only the first parent is allowed to nest - all other parent groups have their reference to this child group deleted.
                for parent_group_name in self._parent_group_names[
                    1 : len(self._parent_group_names)
                ]:
                    self.get_group(self._template_name, parent_group_name).remove_child(
                        self.get_parent_card()
                    )
                self._nesting_level = 1

    def set_parent_group_names(self, parent_groups: list[str]) -> None:
        self._parent_group_names = parent_groups

    def get_parent_group_names(self) -> list[str]:
        return self._parent_group_names

    def is_nested_child(self) -> bool:
        """The parent of this Group is a nested child of another Group"""
        self.enforce_logical_nesting()
        return self._nesting_level > 0

    def getParentNestingPolicy(self) -> bool:
        return self._isNestingChildren

    def get_group_name(self) -> str:
        return self._group_name

    def get_template_name(self) -> str:
        return self._template_name

    def set_parent_card_group(self, card_group: AnyCardGroup | None) -> None:
        self._parent_card_group = card_group

    def get_parent_card_group(self) -> AnyCardGroup | None:
        return self._parent_card_group

    def add_child_card_group(
        self, child_name: str, card_group: AnyCardGroup | None
    ) -> None:
        self._child_card_groups[child_name] = card_group

    def get_child_card_group(self, child_name: str) -> AnyCardGroup | None:
        return self._child_card_groups.get(child_name, None)

    def set_parent_name(self, parent: str) -> None:
        self._parent[parent] = None

    def set_parent_card(self, parent: AnyParentCard) -> None:
        self._parent[self.get_parent_name()] = parent

    def get_parent_name(self) -> str | None:
        try:
            return next(iter(self._parent.keys()))
        except StopIteration:
            return None

    def get_parent_card(self) -> AnyParentCard:
        return self._parent[self.get_parent_name()]

    def add_child_name(self, child: str) -> None:
        self._children[child] = None

    def add_child_card(self, child: AnyCard) -> None:
        card_name = child.card_name
        if card_name in self._children:
            self._children[card_name] = child
        else:
            self._logger.warning(
                f"Group '{self.get_group_name()}': Cannot add card with non-existing name '{card_name}' to the child list"
            )

    def remove_child(self, child: Any) -> None:
        if isinstance(child, str):
            self._children.pop(child)
        else:
            for name, card in self._children.items():
                if child == card:
                    self._children.pop(name)
                    break

    def get_child_names(self) -> Iterable[str]:
        return self._children.keys()

    def get_child_cards(self) -> Iterable[AnyCard]:
        return self._children.values()

    def set_ui_group_parent(self, ui_group_parent: list[UIGroups]):
        self._ui_group_parent = set(ui_group_parent)
        self._isNestingChildren = (
            UIGroups.NESTED_CHILDREN in ui_group_parent
            or UIGroups.CLUSTERED in ui_group_parent
        )

    def get_ui_group_parent(self) -> set[UIGroups] | None:
        """Returns None if UI group parent has not been set - this indicates an error"""
        return self._ui_group_parent
