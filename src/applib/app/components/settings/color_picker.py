from qfluentwidgets import ColorPickerButton
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QColor

from typing import Optional, override

from .base_setting import BaseSetting

from ....module.tools.types.config import AnyConfig


class CoreColorPicker(BaseSetting):
    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        options: dict,
        parent_key: Optional[str] = None,
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

        options : dict
            The options associated with `config_key`.

        title : str
            Widget title.

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
            current_value=QColor(
                config.getValue(key=config_key, parent_key=parent_key)
            ),
            default_value=QColor(
                config.getValue(
                    key=config_key, parent_key=parent_key, use_template_model=True
                )
            ),
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
        self.setting.colorChanged.connect(self.setValue)

    def setValue(self, color: QColor | str) -> None:
        if not isinstance(color, QColor):
            color = QColor(color)

        if super().setValue(color.name()):
            self.setWidgetValue(color)

    @override
    def setWidgetValue(self, color: QColor | str) -> None:
        self.setting.setColor(color)
