import os
from typing import Optional, override

from PyQt6.QtWidgets import QFileDialog, QWidget
from qfluentwidgets import PushButton

from ....module.tools.types.config import AnyConfig
from ....module.tools.types.general import StrPath
from .base_setting import BaseSetting


class CoreFileSelect(BaseSetting):
    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        options: dict,
        caption: str,
        directory: StrPath,
        filter: str,
        initial_filter: str,
        parent_keys: list[str] = [],
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        File Select widget connected to a config key.

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

        caption : str
            Title of the file dialog.

        directory : StrPath
            Open file dialog in this directory.

        filter : str
            File extension filter.
            E.g. `Images (*.jpg *.jpeg *.png *.bmp)`.

        initial_filter : str
            Initial file extension filter.
            E.g. `Images (*.jpg *.jpeg *.png *.bmp)`.

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
            self.caption = caption
            self.directory = (
                os.path.split(self.current_value)[0]
                if self.current_value
                else directory
            )
            self.filter = filter
            self.initial_filter = initial_filter
            self.setting = PushButton("Select")

            # Add file selection to layout
            self.buttonlayout.addWidget(self.setting)
            self._connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def _connectSignalToSlot(self) -> None:
        self.setting.clicked.connect(self._onSelectClicked)
        self.notify.connect(self._onParentNotification)

    def _onParentNotification(self, values: tuple) -> None:
        type, value = values
        if type == "content":
            self.notifyParent.emit(("content", self.current_value))

    def _onSelectClicked(self) -> None:
        file = QFileDialog.getOpenFileName(
            parent=self.parent() if self.parent() else self,
            caption=self.caption,
            directory=self.directory,
            filter=self.filter,
            initialFilter=self.initial_filter,
        )
        if file[0]:
            self.setConfigValue(file[0])
            self.directory = os.path.split(file[0])[0]

    def setConfigValue(self, value: StrPath) -> None:
        if super().setConfigValue(value):
            self.notifyParent.emit(("content", self.current_value))

    @override
    def setWidgetValue(self, value: StrPath) -> None:
        # Not used as the "file" setting is just a push button
        # File changes are handled by `notifyParent` signal
        pass
