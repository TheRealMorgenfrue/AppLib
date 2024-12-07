from __future__ import annotations
from qfluentwidgets import LineEdit
from PyQt6.QtWidgets import QWidget

from typing import Optional, override

from ...common.core_signalbus import core_signalbus
from .base_setting import BaseSetting
from ....module.tools.types.config import AnyConfig


class CoreLineEdit(BaseSetting):
    def __init__(
        self,
        config: AnyConfig,
        configkey: str,
        configname: str,
        options: dict,
        is_tight: bool,
        invalidmsg: Optional[dict[str, str]] = None,
        tooltip: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """LineEdit widget connected to a config key.

        Parameters
        ----------
        config : ConfigBase
            Config from which to get values used for this setting.

        configkey : str
            The option key in the config which should be associated with this setting.

        configname : str
            The name of the config.

        options : dict
            The options associated with the `configkey`.

        is_tight : bool, optional
            Use a smaller version of the line edit.

        invalidmsg : str
            If validation error message shown to the user.

        tooltip : str, optional
            Tooltip for this setting, by default None.

        parent : QWidget, optional
            Parent of this class, by default `None`.
        """
        super().__init__(
            config=config,
            configkey=configkey,
            configname=configname,
            options=options,
            currentValue=config.getValue(configkey, configname),
            defaultValue=config.getValue(configkey, configname, use_template=True),
            backupValue=None,
            isDisabled=False,
            notifyDisabled=True,
            parent=parent,
        )
        try:
            self.minWidth = 100
            self.maxWidth = 200 if is_tight else 400
            self.invalidmsg = (
                [val for val in invalidmsg.values()] if invalidmsg else ["", ""]
            )
            self.setting = LineEdit(self)

            # Configure LineEdit
            self.setting.setText(self.currentValue)
            self.setting.setToolTip(tooltip)
            self.setting.setToolTipDuration(4000)
            self._resizeTextBox()

            # Add LineEdit to layout
            self.buttonlayout.addWidget(self.setting)

            self._connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def _connectSignalToSlot(self) -> None:
        self.setting.editingFinished.connect(lambda: self.setValue(self.setting.text()))
        self.setting.textChanged.connect(self._resizeTextBox)

    def _resizeTextBox(self) -> None:
        padding = 30
        w = self.setting.fontMetrics().boundingRect(self.setting.text()).width()

        if w <= self.minWidth:
            w = self.minWidth
        elif w > self.maxWidth:
            w = self.maxWidth
        self.setting.setFixedWidth(w + padding)

    def setMaxWidth(self, width: int) -> None:
        self.maxWidth = width if 0 < width > self.minWidth else self.maxWidth

    def setMinWidth(self, width: int) -> None:
        self.minWidth = width if 0 < width < self.maxWidth else 0

    def setValue(self, value: str) -> None:
        success = super().setValue(value)
        if success:
            if not self.isDisabled:
                self.setWidgetValue(value)
        elif success is None:
            core_signalbus.genericError.emit(
                "Failed to save setting", "Config lock active"
            )
        else:
            core_signalbus.configValidationError.emit(
                self.configname, self.invalidmsg[0], self.invalidmsg[1]
            )
            self.setting.setText(self.currentValue)

    @override
    def setWidgetValue(self, value: str) -> None:
        self.setting.setText(value)
