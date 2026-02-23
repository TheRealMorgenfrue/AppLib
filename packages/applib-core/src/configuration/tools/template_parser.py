from typing import Any, Self

from pydantic import Field

from ...logging import LoggingManager
from ...types.templates import AnyTemplate
from ..tools.template_utils.options import Option
from .action_manager import Actions
from .template_utils.validation_info import ValidationInfo


class TemplateParser:
    _instance = None
    _logger = None
    _current_template_name = ""

    # Remember templates already parsed
    _parsed_templates = set()  # type: set[str]
    # Store information used to generate validation models
    _validation_infos = {}  # type: dict[str, ValidationInfo]
    actions = Actions()

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._logger = LoggingManager()
        return cls._instance

    def _prefix_msg(self) -> str:
        return f"Template '{self._current_template_name}':"

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
                        + f"An action must be callable. Removing value"
                    )
                    option.actions.pop(i)

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
        validation_info: ValidationInfo,
    ):
        if option.defined(option.validators):
            if not isinstance(option.validators, list):
                option.validators = [option.validators]
            validation_info.add_setting_validation(setting, path, option.validators)
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
            if field_default is not None:
                min_values.append(field_default)

        field_min = min(min_values, default=None)
        field_max = option.max if option.defined(option.max) else None
        field = (
            field_type,
            Field(default=field_default, ge=field_min, le=field_max),
        )
        validation_info.add_field(setting, field, path)

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
            validation_info = ValidationInfo()
            for setting, option, path in template.options():
                self._parse_validation(
                    setting,
                    option,
                    path,
                    validation_info,
                )
                self._parse_actions(
                    setting,
                    option,
                    path,
                    template_name,
                )
            self._validation_infos[template_name] = validation_info
            self._parsed_templates.add(template_name)

    def get_validation_info(self, template_name: str) -> ValidationInfo:
        return self._validation_infos[template_name]
