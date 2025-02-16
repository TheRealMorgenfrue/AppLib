from typing import Optional, override

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import ColorPickerButton

from ....module.configuration.tools.template_options.options import GUIOption
from ....module.tools.types.config import AnyConfig
from .base_setting import BaseSetting


class CoreColorPicker(BaseSetting):
    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        option: GUIOption,
        parent_keys: list[str] = [],
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        ColorPicker widget connected to a config key

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting.

        config_key : str
            The option key in the config which should be associated with this setting.

        config_name : str
            The name of the config.

        option : GUIOption
            The options associated with `config_key`.

        title : str
            Widget title.

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
            current_value=QColor(config.get_value(key=config_key, parents=parent_keys)),
            default_value=QColor(
                config.template.get_value(key=config_key, parents=parent_keys).default
            ),
            parent_keys=parent_keys,
            parent=parent,
        )
        try:
            # Lowercase string is intended
            self.setting = ColorPickerButton(
                self.current_value, self.tr("application color"), self
            )
            # Add colorpicker to layout
            self.buttonlayout.addWidget(self.setting)
            self._connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def _connectSignalToSlot(self) -> None:
        self.setting.colorChanged.connect(self.set_config_value)

    def set_config_value(self, color: QColor | str) -> None:
        if not isinstance(color, QColor):
            color = QColor(color)

        if super().set_config_value(color.name()):
            self.setWidgetValue(color)

    @override
    def setWidgetValue(self, color: QColor | str) -> None:
        self.setting.setColor(color)
