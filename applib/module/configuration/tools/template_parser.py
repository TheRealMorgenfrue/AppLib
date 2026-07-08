from collections.abc import Hashable
from copy import deepcopy
from typing import Any, Self

from pydantic import Field

from ...exceptions import OrphanGroupWarning
from ...logging.logging_manager import LoggingManager
from ...tools.types.templates import AnyTemplate
from ..runners.actions.action_manager import Actions
from ..tools.template_utils.options import CompatilityValidator, GUIMessage, Option
from .template_utils.groups import Group
from .template_utils.template_enums import Flags, UIGroups
from .template_utils.validation_info import FieldValidationInfo, ModelValidationInfo


class TemplateParser:
    _instance = None
    _current_template_name = ""

    _parsed_templates: set[str] = set()
    _field_validation_infos: dict[str, FieldValidationInfo] = {}
    _model_validation_infos: dict[str, ModelValidationInfo] = {}
    # These groups have no parent assigned to them (which is an error)
    _orphan_groups: dict[str, list[Hashable]] = {}
    group: Group | None = None
    actions = Actions()

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._logger = LoggingManager()
        return cls._instance

    def _prefix_msg(self) -> str:
        return f"Template '{self._current_template_name}':"

    def _group_is_included(self, option: Option) -> bool:
        # option.flags is a list after parsing flags
        return not (
            option.defined(option.flags) and Flags.HIDE_IN_GUI in option.flags  # type: ignore
        )

    def _parse_group(self, setting: str, option: Option, template_name: str) -> None:
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
                if parent_groups and group_name not in parent_groups:
                    self.group.set_parent_group_names(parent_groups)

                # Check if this setting is a ui_group_parent.
                # NOTE: If multiple ui_groups are given to a parent setting, the setting is only a parent for the first group and
                #       a child in any remaining groups
                if i == 0 and option.defined(option.ui_group_parent):
                    # Check if a parent is defined for this group
                    if self.group.get_parent_name():
                        self._logger.warning(
                            f"{self._prefix_msg()} Unable to assign setting '{setting}' as group parent "
                            + f"for group '{self.group.get_group_name()}'. Setting '{self.group.get_parent_name()}' is already designated as parent. "
                            + "Adding as child to existing group"
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
        option: Option,
        group: Group,
        group_name: Hashable,
        template_name: str,
    ) -> None:
        # Convert the value of ui_group_parent to a list if it isn't one already
        if not isinstance(option.ui_group_parent, list):
            option.ui_group_parent = [option.ui_group_parent]

        # Check that the values of the ui_group_parent list are "UIGroups" enums
        for i, value in enumerate(option.ui_group_parent):
            if value.name not in UIGroups._member_names_:
                self._logger.error(
                    f"{self._prefix_msg()} Group parent setting '{setting}' has invalid value '{value}'. "
                    + f"Expected one of '{', '.join(UIGroups._member_names_)}'. "
                    + "Removing value"
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
        option: Option,
        group: Group,
        group_name: Hashable,
        template_name: str,
    ) -> None:
        group.add_child_name(setting)
        # This group has no parent associated
        if (
            group.get_parent_name() is None
            and group.get_group_name() not in self._orphan_groups[template_name]
        ):
            self._orphan_groups[template_name].append(group_name)

    def _parse_flags(self, setting: str, option: Option):
        if option.defined(option.flags):
            if not isinstance(option.flags, list):
                option.flags = [option.flags]

            for i, flag in enumerate(deepcopy(option.flags)):
                if flag.name not in Flags._member_names_:
                    self._logger.error(
                        f"{self._prefix_msg()} Setting '{setting}' has invalid flag '{flag}'. "
                        + f"Expected one of '{', '.join(Flags._member_names_)}'. "
                        + "Removing value"
                    )
                    option.flags.pop(i)

    def _parse_actions(
        self,
        setting: str,
        option: Option,
        path: str,
        template_name: str,
    ):
        if option.defined(option.actions):
            if not isinstance(option.actions, list):
                option.actions = [option.actions]

            for i, action in enumerate(option.actions):
                if callable(action):
                    self.actions.add_action(setting, action, path, template_name)
                else:
                    self._logger.error(
                        f"{self._prefix_msg()} Setting '{setting}' has invalid action '{action}'. "
                        + "An action must be callable. Removing value"
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
            if default_in:
                field_type = option.type | type(option.default)
            else:
                field_type = option.type
        elif default_in:
            field_type = type(option.default)
        else:
            self._logger.warning(
                f"{self._prefix_msg()} Could not determine object type for setting '{setting}'. This will cause validation issues"
            )
        return field_type

    def _parse_validation(
        self,
        setting: str,
        option: Option,
        path: str,
        field_validation_info: FieldValidationInfo,
        model_validation_info: ModelValidationInfo,
    ):
        if option.defined(option.validators):
            if not isinstance(option.validators, list):
                option.validators = [option.validators]
            for validator in option.validators:
                if isinstance(validator, CompatilityValidator):
                    if setting != validator.fields[0]:
                        validator.fields.insert(0, setting)
                    model_validation_info.add_model_validator(validator)
                else:
                    field_validation_info.add_field_validator(setting, path, validator)
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
        if option.defined(option.min) and option.min is not None:
            min_values.append(option.min)
            if option.defined(option.ui_disable_self):
                min_values.append(option.ui_disable_self)
            if option.defined(option.ui_disable_children):
                min_values.append(option.ui_disable_children)
            if field_default is not None:
                min_values.append(field_default)

        field_min = min(min_values, default=None)
        field_max = option.max if option.defined(option.max) else None
        field = (
            field_type,
            Field(default=field_default, ge=field_min, le=field_max),
        )
        field_validation_info.add_field(setting, field, path)

    def _validate_setting(
        self,
        setting: str,
        option: Option,
        template_name: str,
    ):
        """Validates a template setting and corrects any errors.

        Parameters
        ----------
        setting : str
            The name of the `option` in the template.
        option : Option
            The object describing this setting.
        template_name : str
            The name of the template this setting is defined in.
        """
        if not option.defined(option.ui_info):
            self._logger.warning(
                f"Setting '{setting}' is missing a title. You can specify one using \"ui_info\" in the template '{template_name}'"
            )
            option.ui_info = GUIMessage("")

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
            field_validation_info = FieldValidationInfo()
            model_validation_info = ModelValidationInfo()
            for setting, option, path in template.options():
                if isinstance(option, Option):
                    self._parse_flags(setting=setting, option=option)

                    if self._group_is_included(option):
                        self._parse_group(
                            setting=setting, option=option, template_name=template_name
                        )
                self._parse_validation(
                    setting, option, path, field_validation_info, model_validation_info
                )
                self._parse_actions(
                    setting,
                    option,
                    path,
                    template_name,
                )
                self._validate_setting(setting, option, template_name)
            self._check_groups(template_name)
            self._field_validation_infos[template_name] = field_validation_info
            self._model_validation_infos[template_name] = model_validation_info
            self._parsed_templates.add(template_name)

    def format_raw_group(
        self, template_name: str, raw_ui_group: Hashable | list[Hashable]
    ) -> list[Hashable]:
        """
        Format a raw template Group.

        Parameters
        ----------
        template_name : str
            The template where `raw_ui_group` originates.

        raw_ui_group : Union[Hashable, list[Hashable]]
            The raw ui_group.

        Returns
        -------
        list[Hashable]
            A list of formatted ui groups.

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
        return group_list  # type: ignore

    def get_field_validation_info(self, template_name: str) -> FieldValidationInfo:
        return self._field_validation_infos[template_name]

    def get_model_validation_info(self, template_name: str) -> ModelValidationInfo:
        return self._model_validation_infos[template_name]
