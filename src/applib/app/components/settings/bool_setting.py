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
