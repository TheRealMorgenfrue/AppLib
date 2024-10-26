from qfluentwidgets import SpinBox, DoubleSpinBox
from PyQt6.QtWidgets import QWidget

from typing import Optional, override

from .range_setting import RangeSetting
from module.tools.types.config import AnyConfig


class ConfigSpinBox(RangeSetting):
    def __init__(
        self,
        config: AnyConfig,
        configkey: str,
        configname: str,
        options: dict,
        min_value: int,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Spinbox widget connected to a config key.

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

        min : int
            The minimum value this setting will accept.

        parent : QWidget, optional
            Parent of this class, by default `None`.
        """
        super().__init__(
            config=config,
            configkey=configkey,
            configname=configname,
            options=options,
            currentValue=config.getValue(configkey, configname),
            defaultValue=config.getValue(
                configkey, configname, use_template_config=True
            ),
            backupValue=None,
            isDisabled=False,
            notifyDisabled=True,
            parent=parent,
        )
        try:
            self.minValue = min_value
            if type(self.currentValue) == int:
                self.setting = SpinBox(self)
                self.maxValue = 999999
            else:
                self.setting = DoubleSpinBox(self)
                self.maxValue = 999999.0

            # Configure spinbox
            self.setting.setAccelerated(True)
            self.setting.setSingleStep(1)
            self.setting.setRange(self.minValue, self.maxValue)

            # Ensure value cannot be invalid in the GUI
            self.setting.setValue(self._ensureValidGUIValue(self.currentValue))

            # Add SpinBox to layout
            self.buttonlayout.addWidget(self.setting)

            self._connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def _connectSignalToSlot(self) -> None:
        self.setting.valueChanged.connect(self.setValue)

    def setValue(self, value: int) -> None:
        if super().setValue(value):
            if self.notifyDisabled:
                self.notifyDisabled = False
                self.setWidgetValue(value)
                self.notifyDisabled = True

    @override
    def setWidgetValue(self, value: str) -> None:
        # Do not update GUI with disable values
        self.setting.setValue(self._ensureValidGUIValue(value))
