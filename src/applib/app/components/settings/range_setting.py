from typing import override

from ....module.tools.types.general import floatOrInt


class RangeSettingMixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def _defineRange(self, num_range: tuple[floatOrInt | None, floatOrInt | None]):
        min, max = num_range
        self.min_value = min if min is not None else -999999
        self.max_value = max if max is not None else 999999

    def _ensureValidGUIValue(self, value: int | float) -> int | float:
        return value if value > self.min_value else self.min_value

    @override
    def _setDisableWidget(self, is_disabled: bool, save_value: bool) -> None:  # type: ignore
        if self.backup_value is not None:
            self.backup_value = self._ensureValidGUIValue(self.backup_value)
        super()._setDisableWidget(is_disabled, save_value)  # type: ignore
