from typing import Optional, override

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QWidget
from qfluentwidgets import Slider

from ....module.configuration.internal.core_args import CoreArgs
from ....module.tools.types.config import AnyConfig
from ....module.tools.utilities import dictLookup
from .base_setting import BaseSetting
from .range_setting import RangeSettingMixin


class CoreSlider(BaseSetting, RangeSettingMixin):
    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        options: dict,
        num_range: tuple[int, int],
        is_tight: bool,
        baseunit: Optional[str] = None,
        parent_keys: list[str] = [],
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

        parent_keys : list[str]
            The parents of `key`. Used for lookup in the config.

        parent : QWidget, optional
            Parent of this class
            By default `None`.
        """
        super().__init__(
            config=config,
            config_key=config_key,
            options=options,
            current_value=config.get_value(key=config_key, parents=parent_keys),
            default_value=config.template.get_value(
                key="default", parents=[*parent_keys, config_key]
            ),
            parent_keys=parent_keys,
            parent=parent,
        )
        try:
            self.baseunit = baseunit
            if baseunit:
                self.unit = self._get_unit(baseunit)
            self.min_value, self.max_value = num_range
            self.setting = Slider(Qt.Orientation.Horizontal, self)
            self.valueLabel = QLabel(self)

            # Configure slider and label
            w = 268
            if is_tight:
                w = int(w * 0.67) if self.max_value > 40 else w // 2
            self.setting.setMinimumWidth(w)
            self.setting.setSingleStep(1)
            self.setting.setRange(self.min_value, self.max_value)
            self.setWidgetValue(self.current_value)
            self.valueLabel.setObjectName("valueLabel")

            # Add label and slider to layout
            self.buttonlayout.addWidget(self.valueLabel)
            self.buttonlayout.addWidget(self.setting)
            # Add extra margin for slider handle
            self.buttonlayout.setContentsMargins(8, 0, 8, 0)
            self._connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def _connectSignalToSlot(self) -> None:
        self.setting.valueChanged.connect(self.setConfigValue)

    def _get_unit(self, baseunit: str) -> str:
        unit = dictLookup(CoreArgs._core_config_units, baseunit)
        # Found a unit definition for the base unit
        if unit is not None:
            # This unit does not have a plural definition
            if unit == "":
                unit = baseunit
        return unit

    def _setLabelText(self, value: int) -> None:
        if self.baseunit:
            self.valueLabel.setText(
                f"{value} {self.unit if value != 1 and value != -1 else self.baseunit}"
            )
        else:
            self.valueLabel.setNum(value)

    def setConfigValue(self, value: int) -> None:
        if super().setConfigValue(value):
            if self.notify_disabled:
                self.notify_disabled = False
                self.setWidgetValue(value)
                self.notify_disabled = True

    @override
    def setWidgetValue(self, value: str) -> None:
        # Do not update GUI with disable values
        gui_value = self._ensureValidGUIValue(value)
        self.setting.setValue(gui_value)
        self._setLabelText(gui_value)
