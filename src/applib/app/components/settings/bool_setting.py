from abc import abstractmethod
from typing import override

from PyQt6.QtCore import pyqtBoundSignal


class BoolSettingMixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @abstractmethod
    def getCheckedSignal(self) -> pyqtBoundSignal:
        """Get the setting's state change signal."""

    ...

    @override
    def _setDisableWidget(self, is_disabled: bool, save_value: bool) -> None:  # type: ignore
        if self.is_disabled != is_disabled:
            self.is_disabled = is_disabled
            self.setting.setDisabled(self.is_disabled)  # type: ignore

            if self.is_disabled:
                self.backup_value = self.current_value  # type: ignore
                value = self.disable_self_value  # type: ignore
            else:
                value = (
                    not self.disable_self_value  # type: ignore
                    if self._canGetDisabled()  # type: ignore
                    else self.backup_value
                )
            if self._canGetDisabled() and save_value:  # type: ignore
                self.setValue(value)  # type: ignore
