from qfluentwidgets import SpinBox, DoubleSpinBox
from PyQt6.QtWidgets import QWidget

from typing import Optional, override

from .base_setting import BaseSetting
from .range_setting import RangeSettingMixin

from ....module.tools.types.config import AnyConfig


class CoreSpinBox(BaseSetting, RangeSettingMixin):
    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        options: dict,
        min_value: int,
        parent_key: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Spinbox widget connected to a config key.

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting.

        config_key : str
            The key in the config which should be associated with this setting.

        options : dict
            The options associated with `config_key`.

        min : int
            The minimum value this setting will accept.

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
            current_value=config.getValue(key=config_key, parent_key=parent_key),
            default_value=config.getValue(
                key=config_key, parent_key=parent_key, use_template_model=True
            ),
            parent_key=parent_key,
            parent=parent,
        )
        try:
            self.min_value = min_value
            if type(self.current_value) == int:
                self.setting = SpinBox(self)
                self.maxValue = 999999
            else:
                self.setting = DoubleSpinBox(self)
                self.maxValue = 999999.0

            # Configure spinbox
            self.setting.setAccelerated(True)
            self.setting.setSingleStep(1)
            self.setting.setRange(self.min_value, self.maxValue)

            # Ensure value cannot be invalid in the GUI
            self.setWidgetValue(self.current_value)

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
            if self.notify_disabled:
                self.notify_disabled = False
                self.setWidgetValue(value)
                self.notify_disabled = True

    @override
    def setWidgetValue(self, value: str) -> None:
        # Do not update GUI with disable values
        self.setting.setValue(self._ensureValidGUIValue(value))
