from copy import deepcopy
from typing import Any, Hashable, Iterable, Self, Union

from pydantic import Field

from ...exceptions import OrphanGroupWarning
from ...logging import AppLibLogger
from ...tools.types.templates import AnyTemplate
from ...tools.utilities import iter_to_str
from ..tools.template_options.actions import Actions
from .template_options.groups import Group
from .template_options.template_enums import UIFlags, UIGroups
from .template_options.validation_info import ValidationInfo


class TemplateParser:
    _instance = None
    _logger = AppLibLogger().getLogger()
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

    def _group_is_included(self, options: dict[str, Any]) -> bool:
        # options["ui_flags"] is a list after parsing flags
        return not ("ui_flags" in options and UIFlags.EXCLUDE in options["ui_flags"])

    def _parse_group(
        self, setting: str, options: dict[str, Any], template_name: str
    ) -> None:
        """Parse *ui_group* and *ui_group_parent* information from supplied template"""
        # Check if this setting belongs to a ui_group
        if "ui_group" in options:
            # Make ui_group option a formatted list of strings
            groups = self.format_raw_group(template_name, options["ui_group"])
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
                    self.group.setParentGroupNames(parent_groups)

                # Check if this setting is a ui_group_parent.
                # Note: If multiple ui_groups are given to a parent setting, the setting is only a parent for the first group and
                #       a child in any remaining groups
                if i == 0 and "ui_group_parent" in options:
                    # Check if a parent is defined for this group
                    if self.group.getParentName():
                        self._logger.warning(
                            f"{self._prefix_msg()} Unable to assign setting '{setting}' as group parent "
                            + f"for group '{self.group.getGroupName()}'. Setting '{self.group.getParentName()}' is already designated as parent. "
                            + f"Adding as child to existing group"
                        )
                        self._add_child(
                            setting=setting,
                            options=options,
                            group=self.group,
                            group_name=group_name,
                            template_name=template_name,
                        )
                    else:
                        self._add_parent(
                            setting=setting,
                            options=options,
                            group=self.group,
                            group_name=group_name,
                            template_name=template_name,
                        )
                # This setting is a child of this group
                else:
                    self._add_child(
                        setting=setting,
                        options=options,
                        group=self.group,
                        group_name=group_name,
                        template_name=template_name,
                    )
        # This setting has wrong options; it is not in a group yet is still a group parent
        elif "ui_group_parent" in options:
            self._logger.warning(
                f"{self._prefix_msg()} Group parent '{setting}' is not in a group. Skipping group assignment"
            )

    def _add_parent(
        self,
        setting: str,
        options: dict,
        group: Group,
        group_name: str,
        template_name: str,
    ) -> None:
        # Convert the value of ui_group_parent to a list if it isn't one already
        if not isinstance(options["ui_group_parent"], list):
            options["ui_group_parent"] = [options["ui_group_parent"]]

        # Check that the values of the ui_group_parent list are "UIGroups" enums
        for i, value in enumerate(options["ui_group_parent"]):
            if not value.name in UIGroups._member_names_:
                self._logger.error(
                    f"{self._prefix_msg()} Group parent setting '{setting}' has invalid value '{value}'. "
                    + f"Expected one of '{iter_to_str(UIGroups._member_names_, separator=", ")}'. "
                    + f"Removing value"
                )
                options["ui_group_parent"].pop(i)

        # Add this setting as the parent setting of its ui_group
        group.setParentName(setting)
        group.setUIGroupParent(options["ui_group_parent"])

        # A parent for this group was found
        if group_name in self._orphan_groups[template_name]:
            self._orphan_groups[template_name].remove(group_name)

    def _add_child(
        self,
        setting: str,
        options: dict,
        group: Group,
        group_name: str,
        template_name: str,
    ) -> None:
        group.addChildName(setting)
        # This group has no parent associated
        if (
            group.getParentName() is None
            and group.getGroupName() not in self._orphan_groups[template_name]
        ):
            self._orphan_groups[template_name].append(group_name)

    def _parse_flags(self, setting: str, options: dict[str, Any], template_name: str):
        if "ui_flags" in options:
            if not isinstance(options["ui_flags"], list):
                options["ui_flags"] = [options["ui_flags"]]

            for i, flag in enumerate(deepcopy(options["ui_flags"])):
                if not flag.name in UIFlags._member_names_:
                    self._logger.error(
                        f"{self._prefix_msg()} Setting '{setting}' has invalid flag '{flag}'. "
                        + f"Expected one of '{iter_to_str(UIFlags._member_names_, separator=", ")}'. "
                        + f"Removing value"
                    )
                    options["ui_flags"].pop(i)

    def _parse_actions(
        self,
        setting: str,
        options: dict[str, Any],
        parents: list[str],
        template_name: str,
    ):
        if "actions" in options:
            if not isinstance(options["actions"], list):
                options["actions"] = [options["actions"]]

            for i, action in enumerate(deepcopy(options["actions"])):
                if callable(action):
                    self.actions.add_action(setting, action, parents, template_name)
                else:
                    self._logger.error(
                        f"{self._prefix_msg()} Setting '{setting}' has invalid action '{action}'. "
                        + f"An action must be callable. Removing value"
                    )
                    options["actions"].pop(i)

    def _check_groups(self, template_name: str) -> None:
        self._check_orphan_groups(template_name)
        self._check_childless_parent_groups(template_name)

    def _check_orphan_groups(self, template_name: str) -> None:
        if self._orphan_groups[template_name]:
            for orphan_group in self._orphan_groups[template_name]:
                self._logger.warning(
                    f"{self._prefix_msg()} Group '{orphan_group}' does not have a group parent associated. Removing from group list"
                )
                Group.removeGroup(template_name, orphan_group)

    def _check_childless_parent_groups(self, template_name: str) -> None:
        groups = Group.getAllGroups(template_name)
        if groups:
            for group in groups:
                if not group.getChildNames():
                    self._logger.warning(
                        f"{self._prefix_msg()} Group '{group.getGroupName()}' is nesting children, but has no children assigned to it"
                    )

    def _get_field_type(self, setting: str, options: dict) -> Any:
        field_type = None
        default_in = "default" in options
        type_in = "type" in options
        if type_in:
            if default_in and options["default"] is None:
                field_type = Union[options["type"], type(None)]
            else:
                field_type = options["type"]
        elif default_in:
            field_type = type(options["default"])
        else:
            self._logger.warning(
                f"{self._prefix_msg()} Could not determine object type for setting '{setting}'. This will cause validation issues"
            )
        return field_type

    def _parse_validation_info(
        self,
        setting: str,
        options: dict,
        position: Iterable[int],
        parents: Iterable[Hashable],
        validation_info: ValidationInfo,
    ):
        if "validators" in options:
            validation_info.add_setting_validation(
                setting, position, parents, options["validators"]
            )

        field_type = self._get_field_type(setting, options)
        field_default = (
            options["default"]
            if "default" in options
            else self._logger.warning(
                f"{self._prefix_msg()} Missing default value for setting '{setting}'"
            )
        )

        # The minimum value should be the smallest value available for a given setting
        min_values = []
        if "min" in options:
            min_values.append(options["min"])
            if "ui_disable_self" in options:
                min_values.append(options["ui_disable_self"])
            if "ui_disable_other" in options:
                min_values.append(options["ui_disable_other"])
            if field_default is not None:
                min_values.append(field_default)

        field_min = min(min_values, default=None)
        field_max = options["max"] if "max" in options else None

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
        if not template_name in self._parsed_templates or force:
            self._orphan_groups[template_name] = []
            validation_info = ValidationInfo()
            for k, v, i, ps in template.get_settings():
                setting, options = next(iter(v.items()))
                self._parse_flags(
                    setting=setting, options=options, template_name=template_name
                )
                self._parse_actions(
                    setting=setting,
                    options=options,
                    parents=ps,
                    template_name=template_name,
                )
                if self._group_is_included(options):
                    self._parse_group(
                        setting=setting, options=options, template_name=template_name
                    )
                self._parse_validation_info(
                    setting=setting,
                    options=options,
                    position=i,
                    parents=ps,
                    validation_info=validation_info,
                )
            self._check_groups(template_name)
            self._validation_infos[template_name] = validation_info
            self._parsed_templates.add(template_name)

    def format_raw_group(self, template_name, raw_ui_group: str) -> list[str]:
        """
        Format a raw template Group string.

        Parameters
        ----------
        template_name : _type_
            The template where `raw_ui_group` originates.

        raw_ui_group : str
            The raw ui_group string.

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
        group_list = f"{raw_ui_group}".replace(" ", "").split(",")
        if template_name in self._parsed_templates and group_list:
            for group in group_list:
                if group in self._orphan_groups[template_name]:
                    raise OrphanGroupWarning(
                        f"{self._prefix_msg()} Group '{group}' is an orphan"
                    )
        return group_list

    def get_validation_info(self, template_name: str) -> ValidationInfo:
        return self._validation_infos[template_name]
