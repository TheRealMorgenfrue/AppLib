from pydantic import Field
from typing import Any, Self, Union

from module.config.templates.template_enums import UIFlags, UIGroups
from module.config.tools.template_options.groups import Group
from module.config.tools.template_options.validation_info import ValidationInfo
from module.logger import logger
from module.tools.utilities import getDictNestingLevel, iterToString


class TemplateParser():
    _instance = None
    _logger = logger

    _parsed_templates: list[str] = [] # Remember templates already parsed
    _validation_infos: dict[str, ValidationInfo] = {} # Store information used to generate validation models
    _orphan_groups: dict[str, list[str]] = {} # These groups have no parent assigned to them which is an error

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _parseContent(self, section_name: str, section: dict,
                       template_name: str, validation_info: ValidationInfo):
        for setting, options in section.items():
            # Gather UI groups
            self._parseGroup(
                setting=setting,
                options=options,
                template_name=template_name
            )
            # Gather UI flags
            self._parseFlags(setting=setting, options=options, template_name=template_name)
            # Gather validation info for the validation model
            self._parseValidationInfo(
                section_name=section_name,
                setting=setting,
                options=options,
                validation_info=validation_info
            )

    def _parseGroup(self, setting: str, options: dict[str, Any], template_name: str) -> None:
        """ Parse *ui_group* and *ui_group_parent* information from supplied template """
        # Check if this setting belongs to a ui_group
        if "ui_group" in options:
            # Make ui_group option a formatted list of strings
            groups = self.formatGroup(template_name, options["ui_group"])

            # This group is a child of these groups
            parent_groups = groups[1:len(groups)] if len(groups) > 1 else None

            for i, group_name in enumerate(groups):
                if group_name == "":
                    self._logger.warning(f"Template '{template_name}': Missing group ID in setting '{setting}'")
                    continue

                # Create a strong reference to the Group class (prevent accidental garbage collection)
                group = Group(template_name, group_name)
                if parent_groups:
                    group.setParentGroupNames(parent_groups)

                # Check if this setting is a ui_group_parent.
                # Note: If multiple ui_groups are given to a parent setting, the setting is only a parent for the first group and
                #       a child in any remaining groups
                if i == 0 and "ui_group_parent" in options:
                    # Check if a parent is defined for this group
                    if group.getParentName():
                        self._logger.warning(f"Template '{template_name}': Can't assign ui_group_parent to setting '{setting}'. "
                                          + f"The setting '{group.getParentName()}' is already designated as parent for "
                                          + f"group '{group.getGroupName()}'")
                    else:
                        # Convert the value of ui_group_parent to a list if it isn't one already
                        if not isinstance(options["ui_group_parent"], list):
                            options["ui_group_parent"] = [options["ui_group_parent"]]

                        # Check that the values of the ui_group_parent list are "UIGroups" enums
                        for i, value in enumerate(options["ui_group_parent"]):
                            if not value.name in UIGroups._member_names_:
                                self._logger.error(f"Template '{template_name}': Group parent setting '{setting}' has invalid value '{value}'. "
                                                   + f"Expected one of '{iterToString(UIGroups._member_names_, separator=", ")}'. "
                                                   + f"Removing value")
                                del options["ui_group_parent"][i] # Remove the invalid value

                        # Add this setting as the parent setting of its ui_group
                        group.setParentName(setting)
                        group.setUIGroupParent(options["ui_group_parent"])

                        # A parent for this group was found
                        if group_name in self._orphan_groups[template_name]:
                            self._orphan_groups[template_name].remove(group_name)
                # This setting is a child of this group
                else:
                    group.addChildName(setting)

                    # This group has no parent associated
                    if group.getParentName() is None and group.getGroupName() not in self._orphan_groups[template_name]:
                        self._orphan_groups[template_name].append(group_name)
        # This setting has wrong options; it is not in a group yet is still a group parent
        elif "ui_group_parent" in options:
            self._logger.warning(f"Template '{template_name}': Group parent setting '{setting}' is not in a group. Skipping")

    def _parseFlags(self, setting: str, options: dict[str, Any], template_name: str) -> None:
        if "ui_flags" in options:
            if not isinstance(options["ui_flags"], list):
                options["ui_flags"] = [options["ui_flags"]]

            for i, value in enumerate(options["ui_flags"]):
                if not value.name in UIFlags._member_names_:
                    self._logger.error(f"Template '{template_name}': Setting '{setting}' has invalid flag '{value}'. "
                                        + f"Expected one of '{iterToString(UIFlags._member_names_, separator=", ")}'. "
                                        + f"Removing value")
                    del options["ui_group_parent"][i] # Remove the invalid value

    def _checkGroups(self, template_name: str) -> None:
        self._checkOrphanGroups(template_name)
        self._checkChildlessParentGroups(template_name)

    def _checkOrphanGroups(self, template_name: str) -> None:
        if self._orphan_groups[template_name]:
            for orphan_group in self._orphan_groups[template_name]:
                self._logger.warning(f"Template '{template_name}': Group '{orphan_group}' does not have a group parent associated. Removing from group list")
                Group.removeGroup(template_name, orphan_group)

    def _checkChildlessParentGroups(self, template_name: str) -> None:
        groups = Group.getAllGroups(template_name)
        if groups:
            for group in groups:
                if not group.getChildNames():
                    self._logger.warning(f"Template '{template_name}': Group '{group.getGroupName()}' is nesting children, but has no children assigned to it")

    def _getFieldType(self, setting: str, options: dict) -> Any:
        field_type = None
        if "type" in options:
            if options["default"] is None:
                field_type = Union[options["type"], type(None)]
            else:
                field_type = options["type"]
        elif "default" in options:
            field_type = type(options["default"])
        else:
            self._logger.warning(f"Could not determine object type for setting '{setting}'. This will cause validation issues")
        return field_type

    def _parseValidationInfo(self, section_name: str, setting: str, options: dict, validation_info: ValidationInfo):
        if "validators" in options:
            for validator in options["validators"]:
                validation_info.addSettingValidation(section_name, setting, validator)
        field_type = self._getFieldType(setting, options)
        field_default = options["default"] if "default" in options else self._logger.warning(f"Missing default value for setting '{setting}'")

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

        field = {setting: (field_type, Field(default=field_default, ge=field_min, le=field_max, required=True))}
        validation_info.addField(section_name, field)

    def parse(self, template_name: str, template: dict, force: bool=False):
        """Parse the supplied template (this is the first pass of the template).

        Parameters
        ----------
        template_name : str
            The name of the template.

        template : dict
            The template to parse.

        force : bool, optional
            Force parsing of the template instead of using the cached version.
            Defaults to False.
        """
        if not template_name in self._parsed_templates or force:
            self._orphan_groups |= {template_name: []}
            validation_info = ValidationInfo()

            # Enable both section and sectionless parsing
            if getDictNestingLevel(template, 2) == 2:
                for section_name, section in template.items():
                    self._parseContent(
                        section_name=section_name,
                        section=section,
                        template_name=template_name,
                        validation_info=validation_info
                    )
            else:
                self._parseContent(
                    section_name="nosection", # TODO: Remove hardcoded need for sections in validation
                    section=template,
                    template_name=template_name,
                    validation_info=validation_info
                )
            self._checkGroups(template_name)
            self._validation_infos |= {template_name: validation_info}
            self._parsed_templates.append(template_name)

    def formatGroup(self, template_name, ui_group: Any) -> list[str]:
        group_list = f"{ui_group}".replace(" ", "").split(",")

        # Ensure orphan groups are excluded when external components
        # need raw access to template groups
        if template_name in self._parsed_templates and group_list:
            for group in group_list:
                if group in self._orphan_groups[template_name]:
                    group_list.remove(group)
        return group_list

    def getValidationInfo(self, template_name: str) -> ValidationInfo | None:
        return self._validation_infos.get(template_name)
