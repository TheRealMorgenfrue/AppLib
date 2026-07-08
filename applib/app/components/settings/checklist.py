from collections.abc import Hashable
from typing import override

from PyQt6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import CheckBox

from ....module.configuration.runners.converters.converter import Converter
from ....module.configuration.tools.template_utils.options import Option
from ....module.tools.types.config import AnyConfig
from .base_setting import BaseSetting


class CoreCheckList(BaseSetting):
    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        option: Option,
        converter: Converter | None = None,
        path="",
        parent: QWidget | None = None,
    ) -> None:
        """
        List of check box widgets connected to a config key.

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting.

        config_key : str
            The option key in the config which should be associated with this setting.

        option : Option
            The option associated with `config_key`.

        converter : Converter | None, optional
            The value converter used to convert values between config and GUI representation.

        path : str
            The path of `key`. Used for lookup in the config.

        parent : QWidget, optional
            Parent of this setting.
            By default None.
        """
        super().__init__(
            config=config,
            config_key=config_key,
            option=option,
            converter=converter,
            path=path,
            parent=parent,
        )

        self.settings: dict[Hashable, CheckBox] = {}
        self.checkbox_layout = QVBoxLayout()

        try:
            self.selected_values: dict[Hashable, None] = dict.fromkeys(
                self.current_value, None
            )

            for value in option.values:
                setting = CheckBox(text=self._convert_value(value, to_gui=True))
                self.settings[value] = setting
                self.checkbox_layout.addWidget(setting)
                self._connectSignalToSlot(setting, value)

            self.buttonlayout.addLayout(self.checkbox_layout)
            self.setWidgetValue(self.current_value)
        except Exception:
            self.deleteLater()
            raise

    def _connectSignalToSlot(self, setting: CheckBox, value: Hashable) -> None:
        setting.stateChanged.connect(
            lambda state, value=value: self._updateState(state, value)
        )

    def _updateState(self, state: bool, value: Hashable):
        if state:
            v = self.selected_values[value] = None
        else:
            v = self.selected_values.pop(value)

        self.setConfigValue(v)

    @override
    def _setWidgetValue(self, value: list[Hashable]) -> None:
        v_set = set(value)
        for k, v in self.settings.items():
            v.setChecked(k in v_set)
