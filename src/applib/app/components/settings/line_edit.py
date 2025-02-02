from typing import Optional, override

from PyQt6.QtWidgets import QWidget
from qfluentwidgets import LineEdit

from ....module.configuration.tools.template_options.template_utils import UIMsg
from ....module.tools.types.config import AnyConfig
from ...common.core_signalbus import core_signalbus
from .base_setting import BaseSetting


class CoreLineEdit(BaseSetting):
    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        options: dict,
        is_tight: bool,
        invalidmsg: Optional[UIMsg] = None,
        tooltip: Optional[str] = None,
        parent_keys: list[str] = [],
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        LineEdit widget connected to a config key.

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting.

        config_key : str
            The option key in the config which should be associated with this setting.

        options : dict
            The options associated with `config_key`.

        is_tight : bool, optional
            Use a smaller version of the line edit.

        invalidmsg : UIMsg
            If a validation error occurs, this message is shown in the GUI.

        tooltip : str, optional
            Tooltip for this setting, by default None.

        parent_keys : list[str]
            The parents of `key`. Used for lookup in the config.

        parent : QWidget, optional
            Parent of this class
            By default `None`.
        """
        super().__init__(
            config=config,
            config_key=config_key,
            options=options,
            current_value=config.get_value(key=config_key, parents=parent_keys),
            default_value=config.get_template_value(
                key="default", parents=[*parent_keys, config_key]
            ),
            parent_keys=parent_keys,
            parent=parent,
        )
        self.minWidth = 100
        self.maxWidth = 200 if is_tight else 400
        self.invalid_msg = invalidmsg
        try:
            self.setting = LineEdit(self)

            # Configure LineEdit
            self.setting.setText(self.current_value)
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
        self.setting.editingFinished.connect(
            lambda: self.setConfigValue(self.setting.text())
        )
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

    def setConfigValue(self, value: str) -> None:
        success = super().setConfigValue(value)
        if success:
            if not self.is_disabled:
                self.setWidgetValue(value)
        elif success is None:
            core_signalbus.genericError.emit("Failed to save setting", "")
        else:
            core_signalbus.configValidationError.emit(
                self.config.name, self.invalid_msg.title, self.invalid_msg.content
            )
            self.setWidgetValue(value)

    @override
    def setWidgetValue(self, value: str) -> None:
        self.setting.setText(value)
