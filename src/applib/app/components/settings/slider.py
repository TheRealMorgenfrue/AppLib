from typing import override

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QWidget
from qfluentwidgets import Slider

from ....module.configuration.internal.core_args import CoreArgs
from ....module.configuration.runners.converters.converter import Converter
from ....module.configuration.tools.template_utils.options import GUIOption
from ....module.tools.types.config import AnyConfig
from ....module.tools.types.general import floatOrInt
from ....module.tools.utilities import dict_lookup
from .base_setting import BaseSetting
from .range_setting import RangeSettingMixin


class CoreSlider(BaseSetting, RangeSettingMixin):
    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        option: GUIOption,
        num_range: tuple[floatOrInt | None, floatOrInt | None],
        is_tight: bool = False,
        baseunit: str | None = None,
        converter: Converter | None = None,
        path="",
        parent: QWidget | None = None,
    ) -> None:
        """
        Slider widget connected to a config key.

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting.

        config_key : str
            The option key in the config which should be associated with this setting.

        option : GUIOption
            The options associated with `config_key`.

        num_range : tuple[floatOrInt | None, floatOrInt | None]
            - num_range[0] == min
            - num_range[1] == max
            If min is None, it defaults to -999999.
            If max is None, it defaults to 999999.

        is_tight : bool, optional
            Use a smaller version of the slider.
            By default False.

        baseunit : str, optional
            The unit of the setting, e.g. "day".
            By default None.

        converter : Converter, optional
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
        self.baseunit = baseunit
        try:
            self._defineRange(num_range)
            if baseunit:
                self.unit = self._get_unit(baseunit)
            self.setting = Slider(Qt.Orientation.Horizontal, self)
            self.valueLabel = QLabel(self)

            # Configure slider and label
            w = 268
            if is_tight:
                w = int(w * 0.67) if self.max_value > 40 else w // 2
            self.setting.setMinimumWidth(w)
            self.setting.setSingleStep(1)
            self.setting.setRange(int(self.min_value), int(self.max_value))
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
        unit = dict_lookup(CoreArgs._core_config_units, baseunit)
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

    @override
    def _setWidgetValue(self, value: int) -> None:
        if self.notify_disabled:
            self.notify_disabled = False
            # Do not update GUI with disable values
            gui_value = int(self._ensureValidGUIValue(value))
            self.setting.setValue(gui_value)
            self._setLabelText(gui_value)
            self.notify_disabled = True
