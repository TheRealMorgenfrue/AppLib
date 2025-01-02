from typing import override


class BoolSettingMixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def _convertBool(self, value: str | bool, reverse: bool = False) -> bool | str:
        value = self._parseBool(value)
        if reverse:
            if value:
                value = (
                    "y"  # This is a hack designed only for 1 usecase. TODO: Fix this
                )
            else:
                value = "n"
        return value

    def _parseBool(self, value: str | bool) -> bool:
        if isinstance(value, bool):
            return value
        truthy = ["y", "true"]
        if value in truthy:
            return True
        return False

    @override
    def _setDisableWidget(self, is_disabled: bool, save_value: bool) -> None:
        if self.is_disabled != is_disabled:
            self.is_disabled = is_disabled
            self.setting.setDisabled(self.is_disabled)

            if self.is_disabled:
                self.backup_value = self.current_value
                value = self.disable_self_value
            else:
                value = (
                    not self.disable_self_value
                    if self._canGetDisabled()
                    else self.backup_value
                )
            if self._canGetDisabled() and save_value:
                self.setValue(value)

    @override
    def setValue(self, value: bool) -> None:
        if (
            self.config_key == "defaultSketchOption"
        ):  # FIXME: This must not be hardcoded!!
            value = self._convertBool(value, reverse=True)
        return super().setValue(value)
