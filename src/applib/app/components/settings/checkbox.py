from typing import Optional, override

from PyQt6.QtCore import pyqtBoundSignal
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import CheckBox

from ....module.configuration.tools.template_options.options import GUIOption
from ....module.tools.types.config import AnyConfig
from .base_setting import BaseSetting
from .bool_setting import BoolSettingMixin


class CoreCheckBox(BaseSetting, BoolSettingMixin):
    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        option: GUIOption,
        parent_keys: list[str] = [],
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Check box widget connected to a config key.

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting.

        config_key : str
            The option key in the config which should be associated with this setting.

        option : GUIOption
            The options associated with `config_key`.

        parent_keys : list[str]
            The parents of `key`. Used for lookup in the config.

        parent : QWidget, optional
            Parent of this class
            By default None.
        """
        super().__init__(
            config=config,
            config_key=config_key,
            option=option,
            current_value=self._convertBool(
                config.get_value(key=config_key, parents=parent_keys)
            ),
            default_value=self._convertBool(
                config.template.get_value(key=config_key, parents=parent_keys).default
            ),
            parent_keys=parent_keys,
            parent=parent,
        )
        try:
            self.setting = CheckBox()
            self.setting.setChecked(self.current_value)  # Set value of switch
            self.buttonlayout.addWidget(self.setting)
            self._connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def _connectSignalToSlot(self) -> None:
        self.setting.stateChanged.connect(
            lambda state: self.set_config_value(bool(state))
        )

    def getCheckedSignal(self) -> pyqtBoundSignal:
        return self.setting.stateChanged

    def set_config_value(self, value: bool) -> None:
        if super().set_config_value(value):
            self.setWidgetValue(value)

    @override
    def setWidgetValue(self, value: bool) -> None:
        self.setting.setChecked(value)
