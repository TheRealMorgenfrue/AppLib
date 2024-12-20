from typing import Any, Callable, TypeAlias


FieldDict: TypeAlias = dict[str, dict[str, tuple]]
ValidatorDict: TypeAlias = dict[str, dict[str, Any]]


class ValidationInfo:
    def __init__(self) -> None:
        self._fields = {}  # type: FieldDict
        self._validators = {}  # type: ValidatorDict

    def addField(self, section_name: str, field: dict):
        if not section_name in self._fields:
            self._fields |= {section_name: {}}
        self._fields[section_name] |= field

    def getFields(self) -> FieldDict:
        return self._fields

    def getValidators(self) -> ValidatorDict:
        return self._validators

    def addSettingValidation(
        self, section_name: str, setting: str, validator: Callable
    ):
        validator_name = f"{validator}"
        if section_name not in self._validators:
            self._validators |= {section_name: {}}

        if validator_name in self._validators[section_name]:
            self._validators[section_name][validator_name]["settings"].append(setting)
        else:
            validator_options = {"validator": validator, "settings": [setting]}
            self._validators[section_name] |= {validator_name: validator_options}
