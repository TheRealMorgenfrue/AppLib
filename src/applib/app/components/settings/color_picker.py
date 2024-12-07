from __future__ import annotations
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
        configkey: str,
        configname: str,
        options: dict,
        parent: Optional[QWidget] = None,
    ) -> None:
        """ColorPicker widget connected to a config key

        Parameters
        ----------
        config : ConfigBase
            Config from which to get values used for this setting

        configkey : str
            The option key in the config which should be associated with this setting

        configname : str
            The name of the config.

        options : dict
            The options associated with the `configkey`.

        title : str
            Widget title

        parent : QWidget, optional
            Parent of this class, by default `None`.
        """
        super().__init__(
            config=config,
            configkey=configkey,
            configname=configname,
            options=options,
            currentValue=QColor(config.getValue(configkey, configname)),
            defaultValue=QColor(
                config.getValue(configkey, configname, use_template=True)
            ),
            backupValue=None,
            isDisabled=False,
            notifyDisabled=True,
            parent=parent,
        )
        try:
            self.setting = ColorPickerButton(
                self.currentValue, self.tr("application color"), self
            )  # Lowercase string is intended

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
