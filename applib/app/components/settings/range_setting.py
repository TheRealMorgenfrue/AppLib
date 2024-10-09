from typing import override
from app.components.settings.base_setting import BaseSetting


# TODO: This should be a mixin class
class RangeSetting(BaseSetting):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def _ensureValidGUIValue(self, value: int | float) -> int | float:
        return value if value > self.minValue else self.minValue

    @override
    def _setDisableWidget(self, isDisabled: bool, saveValue: bool) -> None:
        if self.backupValue is not None:
            self.backupValue = self._ensureValidGUIValue(self.backupValue)
        super()._setDisableWidget(isDisabled, saveValue)
