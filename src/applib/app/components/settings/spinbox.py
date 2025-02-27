from numbers import Number
from typing import Optional, override

from PyQt6.QtWidgets import QWidget
from qfluentwidgets import DoubleSpinBox, SpinBox

from ....module.configuration.tools.template_utils.converter import Converter
from ....module.configuration.tools.template_utils.options import GUIOption
from ....module.tools.types.config import AnyConfig
from .base_setting import BaseSetting
from .range_setting import RangeSettingMixin


class CoreSpinBox(BaseSetting, RangeSettingMixin):
    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        option: GUIOption,
        num_range: tuple[Number | None, Number | None],
        converter: Optional[Converter] = None,
        parent_keys: list[str] = [],
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

        option : GUIOption
            The options associated with `config_key`.

        num_range : tuple[Number | None, Number | None]
            - num_range[0] == min
            - num_range[1] == max
            If min is None, it defaults to 0.
            If max is None, it defaults to 999999.

        converter : Converter | None, optional
            The value converter used to convert values between config and GUI representation.

        parent_keys : list[str]
            The parents of `key`. Used for lookup in the config.

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
        self._defineRange(num_range)
        try:
            if type(self.current_value) == int:
                self.setting = SpinBox(self)
            else:
                self.setting = DoubleSpinBox(self)
                self.min_value = float(self.min_value)
                self.max_value = float(self.max_value)

            # Configure spinbox
            self.setting.setAccelerated(True)
            self.setting.setSingleStep(1)
            self.setting.setRange(self.min_value, self.max_value)

            # Ensure value cannot be invalid in the GUI
            self.setWidgetValue(self.current_value)

            # Add SpinBox to layout
            self.buttonlayout.addWidget(self.setting)
            self._connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def _connectSignalToSlot(self) -> None:
        self.setting.valueChanged.connect(self.setConfigValue)

    @override
    def _setWidgetValue(self, value: Number) -> None:
        if self.notify_disabled:
            self.notify_disabled = False
            # Do not update GUI with disable values
            self.setting.setValue(self._ensureValidGUIValue(value))
            self.notify_disabled = True
