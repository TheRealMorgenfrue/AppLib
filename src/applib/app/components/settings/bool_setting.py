from typing import override


from .base_setting import BaseSetting


# TODO: This should be a mixin class
class BoolSetting(BaseSetting):
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
    def _setDisableWidget(self, isDisabled: bool, saveValue: bool) -> None:
        if self.isDisabled != isDisabled:
            self.isDisabled = isDisabled
            self.setting.setDisabled(self.isDisabled)

            if self.isDisabled:
                self.backupValue = self.currentValue
                value = self.disableSelfValue
            else:
                value = (
                    not self.disableSelfValue
                    if self._canGetDisabled()
                    else self.backupValue
                )
            if self._canGetDisabled() and saveValue:
                self.setValue(value)

    @override
    def setValue(self, value: bool) -> None:
        if (
            self.configkey == "defaultSketchOption"
        ):  # FIXME: This must not be hardcoded!!
            value = self._convertBool(value, reverse=True)
        return super().setValue(value)
