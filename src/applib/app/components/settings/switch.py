from typing import Optional, override

from PyQt6.QtCore import pyqtBoundSignal
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import SwitchButton

from ....module.tools.types.config import AnyConfig
from .base_setting import BaseSetting
from .bool_setting import BoolSettingMixin


class CoreSwitch(BaseSetting, BoolSettingMixin):
    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        options: dict,
        parent_key: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Switch widget connected to a config key.

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting.

        config_key : str
            The option key in the config which should be associated with this setting.

        config_name : str
            The name of the config.

        options : dict
            The options associated with `config_key`.

        parent_key : str, optional
            Search for `config_key` within the scope of a parent key.

        parent : QWidget, optional
            Parent of this class
            By default `None`.
        """
        super().__init__(
            config=config,
            config_key=config_key,
            options=options,
            current_value=self._convertBool(
                config.get_value(key=config_key, parent_key=parent_key)
            ),
            default_value=self._convertBool(
                config.get_value(
                    key=config_key, parent_key=parent_key, use_template_model=True
                )
            ),
            parent_key=parent_key,
            parent=parent,
        )
        try:
            self.setting = SwitchButton(self)

            # Set value of switch
            self.setWidgetValue(self.current_value)

            # Add Switch to layout
            self.buttonlayout.addWidget(self.setting)

            self._connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def _connectSignalToSlot(self) -> None:
        self.setting.checkedChanged.connect(self.setConfigValue)

    def getCheckedSignal(self) -> pyqtBoundSignal:
        return self.setting.checkedChanged

    def setConfigValue(self, value: bool) -> None:
        if super().setConfigValue(value):
            self.setWidgetValue(value)

    @override
    def setWidgetValue(self, value: bool) -> None:
        self.setting.setChecked(value)
