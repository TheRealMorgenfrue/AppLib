from copy import deepcopy
from typing import Any, Hashable, Iterable, Self, Union

from pydantic import Field

from ...exceptions import OrphanGroupWarning
from ...logging import AppLibLogger
from ...tools.types.templates import AnyTemplate
from ...tools.utilities import iter_to_str
from ..tools.template_utils.options import GUIOption, Option
from .template_utils.action_manager import Actions
from .template_utils.groups import Group
from .template_utils.template_enums import UIFlags, UIGroups
from .template_utils.validation_info import ValidationInfo


class TemplateParser:
    _instance = None
    _logger = AppLibLogger().get_logger()
    _current_template_name = ""

    # Remember templates already parsed
    _parsed_templates = set()  # type: set[str]
    # Store information used to generate validation models
    _validation_infos = {}  # type: dict[str, ValidationInfo]
    # These groups have no parent assigned to them (which is an error)
    _orphan_groups = {}  # type: dict[str, list[str]]
    group = None  # type: Group
    actions = Actions()

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _prefix_msg(self) -> str:
        return f"Template '{self._current_template_name}':"

    def _group_is_included(self, option: GUIOption) -> bool:
        # option.ui_flags is a list after parsing flags
        return not (
            option.defined(option.ui_flags) and UIFlags.EXCLUDE in option.ui_flags
        )

    def _parse_group(self, setting: str, option: GUIOption, template_name: str) -> None:
        """Parse *ui_group* and *ui_group_parent* information from supplied template"""
        # Check if this setting belongs to a ui_group
        if option.defined(option.ui_group):
            # Make ui_group option a formatted list of strings
            groups = self.format_raw_group(template_name, option.ui_group)
            # This group is a child of these groups
            parent_groups = groups[1 : len(groups)] if len(groups) > 1 else None

            for i, group_name in enumerate(groups):
                if group_name == "":
                    self._logger.warning(
                        f"{self._prefix_msg()} Missing group ID in setting '{setting}'"
                    )
                    continue

                # Create a strong reference to the Group class (prevent accidental garbage collection)
                self.group = Group(template_name, group_name)
                if parent_groups:
                    self.group.set_parent_group_names(parent_groups)

                # Check if this setting is a ui_group_parent.
                # Note: If multiple ui_groups are given to a parent setting, the setting is only a parent for the first group and
                #       a child in any remaining groups
                if i == 0 and option.defined(option.ui_group_parent):
                    # Check if a parent is defined for this group
                    if self.group.get_parent_name():
                        self._logger.warning(
                            f"{self._prefix_msg()} Unable to assign setting '{setting}' as group parent "
                            + f"for group '{self.group.get_group_name()}'. Setting '{self.group.get_parent_name()}' is already designated as parent. "
                            + f"Adding as child to existing group"
                        )
                        self._add_child(
                            setting=setting,
                            option=option,
                            group=self.group,
                            group_name=group_name,
                            template_name=template_name,
                        )
                    else:
                        self._add_parent(
                            setting=setting,
                            option=option,
                            group=self.group,
                            group_name=group_name,
                            template_name=template_name,
                        )
                # This setting is a child of this group
                else:
                    self._add_child(
                        setting=setting,
                        option=option,
                        group=self.group,
                        group_name=group_name,
                        template_name=template_name,
                    )
        # This setting has wrong options; it is not in a group yet is still a group parent
        elif option.defined(option.ui_group_parent):
            self._logger.warning(
                f"{self._prefix_msg()} Group parent '{setting}' is not in a group. Skipping group assignment"
            )

    def _add_parent(
        self,
        setting: str,
        option: GUIOption,
        group: Group,
        group_name: str,
        template_name: str,
    ) -> None:
        # Convert the value of ui_group_parent to a list if it isn't one already
        if not isinstance(option.ui_group_parent, list):
            option.ui_group_parent = [option.ui_group_parent]

        # Check that the values of the ui_group_parent list are "UIGroups" enums
        for i, value in enumerate(option.ui_group_parent):
            if not value.name in UIGroups._member_names_:
                self._logger.error(
                    f"{self._prefix_msg()} Group parent setting '{setting}' has invalid value '{value}'. "
                    + f"Expected one of '{iter_to_str(UIGroups._member_names_, separator=", ")}'. "
                    + f"Removing value"
                )
                option.ui_group_parent.pop(i)

        # Add this setting as the parent setting of its ui_group
        group.set_parent_name(setting)
        group.set_ui_group_parent(option.ui_group_parent)

        # A parent for this group was found
        if group_name in self._orphan_groups[template_name]:
            self._orphan_groups[template_name].remove(group_name)

    def _add_child(
        self,
        setting: str,
        option: GUIOption,
        group: Group,
        group_name: str,
        template_name: str,
    ) -> None:
        group.add_child_name(setting)
        # This group has no parent associated
        if (
            group.get_parent_name() is None
            and group.get_group_name() not in self._orphan_groups[template_name]
        ):
            self._orphan_groups[template_name].append(group_name)

    def _parse_flags(self, setting: str, option: GUIOption):
        if option.defined(option.ui_flags):
            if not isinstance(option.ui_flags, list):
                option.ui_flags = [option.ui_flags]

            for i, flag in enumerate(deepcopy(option.ui_flags)):
                if not flag.name in UIFlags._member_names_:
                    self._logger.error(
                        f"{self._prefix_msg()} Setting '{setting}' has invalid flag '{flag}'. "
                        + f"Expected one of '{iter_to_str(UIFlags._member_names_, separator=", ")}'. "
                        + f"Removing value"
                    )
                    option.ui_flags.pop(i)

    def _parse_actions(
        self,
        setting: str,
        option: Option,
        parents: list[str],
        template_name: str,
    ):
        if option.defined(option.actions):
            if not isinstance(option.actions, list):
                option.actions = [option.actions]

            for i, action in enumerate(deepcopy(option.actions)):
                if callable(action):
                    self.actions.add_action(setting, action, parents, template_name)
                else:
                    self._logger.error(
                        f"{self._prefix_msg()} Setting '{setting}' has invalid action '{action}'. "
                        + f"An action must be callable. Removing value"
                    )
                    option.actions.pop(i)

    def _check_groups(self, template_name: str) -> None:
        self._check_orphan_groups(template_name)
        self._check_childless_parent_groups(template_name)

    def _check_orphan_groups(self, template_name: str) -> None:
        if self._orphan_groups[template_name]:
            for orphan_group in self._orphan_groups[template_name]:
                self._logger.warning(
                    f"{self._prefix_msg()} Group '{orphan_group}' does not have a group parent associated. Removing from group list"
                )
                Group.remove_group(template_name, orphan_group)

    def _check_childless_parent_groups(self, template_name: str) -> None:
        groups = Group.get_all_groups(template_name)
        if groups:
            for group in groups:
                if not group.get_child_names():
                    self._logger.warning(
                        f"{self._prefix_msg()} Group '{group.get_group_name()}' is nesting children, but has no children assigned to it"
                    )

    def _get_field_type(self, setting: str, option: Option) -> Any:
        field_type = None
        default_in = option.defined(option.default)
        type_in = option.defined(option.type)
        if type_in:
            if default_in and option.default is None:
                field_type = Union[option.type, type(None)]
            else:
                field_type = option.type
        elif default_in:
            field_type = type(option.default)
        else:
            self._logger.warning(
                f"{self._prefix_msg()} Could not determine object type for setting '{setting}'. This will cause validation issues"
            )
        return field_type

    def _parse_validation_info(
        self,
        setting: str,
        option: Option | GUIOption,
        position: Iterable[int],
        parents: Iterable[Hashable],
        validation_info: ValidationInfo,
    ):
        if option.defined(option.validators):
            validation_info.add_setting_validation(
                setting, position, parents, option.validators
            )
        field_type = self._get_field_type(setting, option)
        field_default = (
            option.default
            if option.defined(option.default)
            else self._logger.warning(
                f"{self._prefix_msg()} Missing default value for setting '{setting}'"
            )
        )

        # The minimum value should be the smallest value available for a given setting
        min_values = []
        if option.defined(option.min):
            min_values.append(option.min)
            if option.defined(option.ui_disable_self):
                min_values.append(option.ui_disable_self)
            if option.defined(option.ui_disable_other):
                min_values.append(option.ui_disable_other)
            if field_default is not None:
                min_values.append(field_default)

        field_min = min(min_values, default=None)
        field_max = option.max if option.defined(option.max) else None
        field = {
            setting: (
                field_type,
                Field(default=field_default, ge=field_min, le=field_max, required=True),
            )
        }
        validation_info.add_field(setting, field, position, parents)

    def parse(self, template: AnyTemplate, force: bool = False):
        """Parse the supplied template.

        Parameters
        ----------
        template : AnyTemplate
            The template to parse.

        force : bool, optional
            Force parsing of the template instead of using the cached version.
            Defaults to False.
        """
        self._current_template_name = template_name = template.name
        if template_name not in self._parsed_templates or force:
            self._orphan_groups[template_name] = []
            validation_info = ValidationInfo()
            for k, v, i, ps in template.get_settings():
                setting, option = next(iter(v.items()))
                if isinstance(option, GUIOption):
                    self._parse_flags(setting=setting, option=option)

                    if self._group_is_included(option):
                        self._parse_group(
                            setting=setting, option=option, template_name=template_name
                        )
                self._parse_validation_info(
                    setting=setting,
                    option=option,
                    position=i,
                    parents=ps,
                    validation_info=validation_info,
                )
                self._parse_actions(
                    setting=setting,
                    option=option,
                    parents=ps,
                    template_name=template_name,
                )
            self._check_groups(template_name)
            self._validation_infos[template_name] = validation_info
            self._parsed_templates.add(template_name)

    def format_raw_group(
        self, template_name: str, raw_ui_group: Union[str, Hashable, list[Hashable]]
    ) -> list[str]:
        """
        Format a raw template Group string.

        Parameters
        ----------
        template_name : str
            The template where `raw_ui_group` originates.

        raw_ui_group : Union[str, Hashable, list[Hashable]]
            The raw ui_group.

        Returns
        -------
        list[str]
            A list of formatted ui group strings.

        Raises
        ------
        OrphanGroupWarning
            If any of the groups are orphans, and thus invalid.
        """
        self._current_template_name = template_name
        if isinstance(raw_ui_group, str):
            group_list = raw_ui_group.replace(" ", "").split(",")
        elif isinstance(raw_ui_group, list):
            group_list = raw_ui_group
        elif isinstance(raw_ui_group, tuple):
            group_list = list(raw_ui_group)
        else:
            group_list = [raw_ui_group]
        if template_name in self._parsed_templates and group_list:
            for group in group_list:
                if group in self._orphan_groups[template_name]:
                    raise OrphanGroupWarning(
                        f"{self._prefix_msg()} Group '{group}' is an orphan"
                    )
        return group_list

    def get_validation_info(self, template_name: str) -> ValidationInfo:
        return self._validation_infos[template_name]
