from __future__ import annotations
from typing import Optional, override
from qfluentwidgets import CheckBox
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtBoundSignal

from .bool_setting import BoolSetting
from ....module.tools.types.config import AnyConfig


class CoreCheckBox(BoolSetting):
    def __init__(
        self,
        config: AnyConfig,
        configkey: str,
        configname: str,
        options: dict,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Check box widget connected to a config key.

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
                config.getValue(configkey, configname, use_template=True)
            ),
            backupValue=False,
            isDisabled=False,
            notifyDisabled=True,
            parent=parent,
        )
        try:
            self.setting = CheckBox()

            # Set value of switch
            self.setting.setChecked(self.currentValue)

            # Add Switch to layout
            self.buttonlayout.addWidget(self.setting)

            self._connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def _connectSignalToSlot(self) -> None:
        self.setting.stateChanged.connect(lambda state: self.setValue(bool(state)))

    def getCheckedSignal(self) -> pyqtBoundSignal:
        return self.setting.stateChanged

    def setValue(self, value: bool) -> None:
        if super().setValue(value):
            self.setWidgetValue(value)

    @override
    def setWidgetValue(self, value: bool) -> None:
        self.setting.setChecked(value)
