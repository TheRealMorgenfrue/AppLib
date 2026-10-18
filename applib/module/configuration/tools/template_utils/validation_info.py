from collections.abc import Callable
from typing import Any, Literal

from ..search.nested_dict_search import NestedDictSearch
from ..template_utils.options import CompatilityValidator


class FieldValidatorContainer:
    def __init__(
        self,
        setting: str,
        validator: Callable,
        mode: Literal["before", "after", "plain"] = "after",
    ) -> None:
        """Stores validation information for a single field.

        Parameters
        ----------
        setting : str
            The name of the field/setting.
        validator : Callable
            The validator to apply to this field.
        mode : Literal['before', 'after', 'plain']
            Specify the order the field_validator is applied in relation to standard Pydantic validation.
            By default 'after'.
        """
        self.settings = [setting]
        self.validator = validator
        self.mode = mode

    def add(self, setting: str):
        self.settings.append(setting)

    def get_first_field(self) -> str:
        return self.settings[0]

    def get_other_fields(self) -> list[str]:
        return self.settings[1:] if len(self.settings) > 1 else []


class FieldValidationInfo:
    def __init__(self) -> None:
        self.fields: dict[str, Any] = {}
        self.raw_validators: dict[str, dict[str, FieldValidatorContainer]] = {}

    def add_field(
        self,
        setting: str,
        field: tuple[Any, Callable],
        path: str,
    ):
        NestedDictSearch.insert(
            d=self.fields, key=setting, value=field, path=path, create_missing=True
        )

    def add_field_validator(
        self,
        setting: str,
        path: str,
        validator: Callable,
        mode: Literal["before", "after", "plain"] = "after",
    ):
        if path not in self.raw_validators:
            self.raw_validators[path] = {}
        try:
            self.raw_validators[path][f"{validator}"].add(setting)
        except KeyError:
            self.raw_validators[path][f"{validator}"] = FieldValidatorContainer(
                setting, validator, mode
            )


class ModelValidationInfo:
    def __init__(self) -> None:
        self.validators: dict[Callable, list[tuple[str, ...]]] = {}

    def add_model_validator(self, model_validator: CompatilityValidator):
        if model_validator.validator in self.validators:
            self.validators[model_validator.validator].append(
                tuple(model_validator.fields)
            )
        else:
            self.validators[model_validator.validator] = [tuple(model_validator.fields)]
