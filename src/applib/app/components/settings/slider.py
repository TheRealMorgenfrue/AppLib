from qfluentwidgets import Slider
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt

from typing import Optional, override

from .base_setting import BaseSetting
from .range_setting import RangeSettingMixin

from ....module.config.internal.core_args import CoreArgs
from ....module.tools.utilities import dictLookup
from ....module.tools.types.config import AnyConfig


class CoreSlider(BaseSetting, RangeSettingMixin):
    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        options: dict,
        num_range: tuple[int, int],
        is_tight: bool,
        baseunit: Optional[str] = None,
        parent_key: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Slider widget connected to a config key.

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting.

        config_key : str
            The option key in the config which should be associated with this setting.

        options : dict
            The options associated with `config_key`.

        num_range : tuple[int, int]
            - num_range[0] == min
            - num_range[1] == max

        is_tight : bool, optional
            Use a smaller version of the slider.

        baseunit : str, optional
            The unit of the setting, e.g. "day".
            By default `None`.

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
            parent=parent,
        )
        try:
            self.baseunit = baseunit
            self.min_value, self.maxValue = num_range
            self.setting = Slider(Qt.Orientation.Horizontal, self)
            self.valueLabel = QLabel(self)

            # Ensure value cannot be invalid in the GUI
            guiValue = self._ensureValidGUIValue(self.current_value)

            # Configure slider and label
            w = 268
            if is_tight:
                w = int(w * 0.67) if self.maxValue > 40 else w // 2
            self.setting.setMinimumWidth(w)
            self.setting.setSingleStep(1)
            self.setting.setRange(self.min_value, self.maxValue)
            self.setting.setValue(guiValue)
            self._setLabelText(guiValue)
            self.valueLabel.setObjectName("valueLabel")

            # Add label and slider to layout
            self.buttonlayout.addWidget(self.valueLabel)
            self.buttonlayout.addWidget(self.setting)
            self.buttonlayout.addSpacing(-10)
            self._connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def _connectSignalToSlot(self) -> None:
        self.setting.valueChanged.connect(self.setValue)

    def _setLabelText(self, value: int) -> None:
        if self.baseunit:
            unit = dictLookup(CoreArgs.config_units, self.baseunit)

            # Found a unit definition for the base unit
            if unit is not None:
                # This unit does not have a plural definition
                if unit == "":
                    unit = self.baseunit
                self.valueLabel.setText(
                    f"{value} {unit if value != 1 else self.baseunit}"
                )
        else:
            self.valueLabel.setNum(value)

    def setValue(self, value: int) -> None:
        if super().setValue(value):
            if self.notify_disabled:
                self.notify_disabled = False
                self.setWidgetValue(value)
                self.notify_disabled = True

    @override
    def setWidgetValue(self, value: str) -> None:
        # Do not update GUI with disable values
        guiValue = self._ensureValidGUIValue(value)
        self.setting.setValue(guiValue)
        self._setLabelText(guiValue)
