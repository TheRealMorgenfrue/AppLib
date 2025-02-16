from typing import Optional, override

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import ColorPickerButton

from ....module.configuration.runners.converters.color_converter import ColorConverter
from ....module.configuration.tools.template_utils.converter import Converter
from ....module.configuration.tools.template_utils.options import GUIOption
from ....module.tools.types.config import AnyConfig
from .base_setting import BaseSetting


class CoreColorPicker(BaseSetting):
    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        option: GUIOption,
        converter: Optional[Converter] = ColorConverter(),
        parent_keys: list[str] = [],
        parent: Optional[QWidget] = None,
    ):
        """
        ColorPicker widget connected to a config key.

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting.

        config_key : str
            The option key in the config which should be associated with this setting.

        option : GUIOption
            The options associated with `config_key`.

        converter : Converter | None, optional
            The value converter used to convert values between config and GUI representation.

        title : str
            Widget title.

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
            current_value=config.get_value(key=config_key, parents=parent_keys),
            default_value=config.template.get_value(
                key=config_key, parents=parent_keys
            ).default,
            converter=converter,
            parent_keys=parent_keys,
            parent=parent,
        )
        try:
            self.setting = ColorPickerButton(
                self._convert_value(self.current_value, to_gui=True),
                self.tr("application color"),  # Lowercase string is intended
                self,
            )
            self.buttonlayout.addWidget(self.setting)
            self._connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def _connectSignalToSlot(self) -> None:
        self.setting.colorChanged.connect(self.setConfigValue)

    @override
    def _setWidgetValue(self, color: QColor) -> None:
        self.setting.setColor(color)
