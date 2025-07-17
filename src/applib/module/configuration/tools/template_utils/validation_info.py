from collections.abc import Callable
from typing import Any

from applib.module.configuration.tools.search.nested_dict_search import NestedDictSearch


class ValidatorContainer:
    def __init__(self, setting: str, validator: Callable) -> None:
        self.settings = [setting]
        self.validator = validator

    def add(self, setting: str):
        self.settings.append(setting)

    def get_first_field(self) -> str:
        return self.settings[0]

    def get_other_fields(self) -> list[str]:
        return self.settings[1:] if len(self.settings) > 1 else []


class ValidationInfo:
    def __init__(self) -> None:
        self.fields: dict[str, Any] = {}
        self.raw_validators: dict[str, dict[str, ValidatorContainer]] = {}

    def add_field(
        self,
        setting: str,
        field: tuple[Any, Callable],
        path: str,
    ):
        NestedDictSearch.insert(
            d=self.fields, key=setting, value=field, path=path, create_missing=True
        )

    def add_setting_validation(
        self,
        setting: str,
        path: str,
        validators: list[Callable],
    ):
        if path not in self.raw_validators:
            self.raw_validators[path] = {}
        for validator in validators:
            try:
                self.raw_validators[path][f"{validator}"].add(setting)
            except KeyError:
                self.raw_validators[path][f"{validator}"] = ValidatorContainer(
                    setting, validator
                )
