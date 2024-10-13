from qfluentwidgets import SwitchButton
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtBoundSignal

from typing import Optional, override

from .bool_setting import BoolSetting
from module.tools.types.config import AnyConfig


class ConfigSwitch(BoolSetting):
    def __init__(
        self,
        config: AnyConfig,
        configkey: str,
        configname: str,
        options: dict,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Switch widget connected to a config key.

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting.

        configkey : str
            The option key in the config which should be associated with this setting.

        configname : str
            The name of the config.

        options : dict
            The options associated with the `configkey`.

        parent : QWidget, optional
            Parent of this class, by default `None`.
        """
        super().__init__(
            config=config,
            configkey=configkey,
            configname=configname,
            options=options,
            currentValue=self._convertBool(config.getValue(configkey, configname)),
            defaultValue=self._convertBool(
                config.getValue(configkey, configname, use_template_config=True)
            ),
            backupValue=False,
            isDisabled=False,
            notifyDisabled=True,
            parent=parent,
        )
        try:
            self.setting = SwitchButton(self)

            # Set value of switch
            self.setWidgetValue(self.currentValue)

            # Add Switch to layout
            self.buttonlayout.addWidget(self.setting)

            self.__connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def __connectSignalToSlot(self) -> None:
        self.setting.checkedChanged.connect(self.setValue)

    def getCheckedSignal(self) -> pyqtBoundSignal:
        return self.setting.checkedChanged

    def setValue(self, value: bool) -> None:
        if super().setValue(value):
            self.setWidgetValue(value)

    @override
    def setWidgetValue(self, value: bool) -> None:
        self.setting.setChecked(value)
