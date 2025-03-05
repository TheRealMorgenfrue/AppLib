from typing import Optional, override

from PyQt6.QtWidgets import QWidget
from qfluentwidgets import LineEdit

from ....module.configuration.runners.converters.converter import Converter
from ....module.configuration.tools.template_utils.options import GUIMessage, GUIOption
from ....module.tools.types.config import AnyConfig
from ...common.core_signalbus import core_signalbus
from .base_setting import BaseSetting


class CoreLineEdit(BaseSetting):
    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        option: GUIOption,
        is_tight: bool = False,
        ui_invalid_input: Optional[GUIMessage] = None,
        converter: Optional[Converter] = None,
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

        option : GUIOption
            The options associated with `config_key`.

        is_tight : bool, optional
            Use a smaller version of the line edit.
            By default False.

        ui_invalid_input : GUIMessage, optional
            Message informing the user that they typed invalid data into this setting in the GUI.
            If None, no message is shown.
            By default None.

        converter : Converter | None, optional
            The value converter used to convert values between config and GUI representation.

        parent_keys : list[str], optional
            The parents of `key`. Used for lookup in the config.
            By default [].

        parent : QWidget, optional
            Parent of this setting.
            By default None.
        """
        super().__init__(
            config=config,
            config_key=config_key,
            option=option,
            converter=converter,
            parent_keys=parent_keys,
            parent=parent,
        )
        self.minWidth = 100
        self.maxWidth = 200 if is_tight else 400
        self.ui_invalid_input = ui_invalid_input
        try:
            self.setting = LineEdit(self)
            self.setWidgetValue(self.current_value)
            self._resizeTextBox()
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

    @override
    def _setWidgetValue(self, value: str) -> None:
        self.setting.setText(value)

    @override
    def setConfigValue(self, value: str) -> None:
        if super().setConfigValue(value):
            if not self.is_disabled:
                self.setWidgetValue(value)
        else:
            core_signalbus.configValidationError.emit(
                self.config.name, self.ui_invalid_input[0], self.ui_invalid_input[1]
            )
            self.setWidgetValue(value)
