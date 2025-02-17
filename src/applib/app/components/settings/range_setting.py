from numbers import Number
from typing import override


class RangeSettingMixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def _defineRange(self, num_range: tuple[Number | None, Number | None]):
        min, max = num_range
        self.min_value = min if min is not None else -999999
        self.max_value = max if max is not None else 999999

    def _ensureValidGUIValue(self, value: int | float) -> int | float:
        return value if value > self.min_value else self.min_value

    @override
    def _setDisableWidget(self, is_disabled: bool, save_value: bool) -> None:
        if self.backup_value is not None:
            self.backup_value = self._ensureValidGUIValue(self.backup_value)
        super()._setDisableWidget(is_disabled, save_value)
