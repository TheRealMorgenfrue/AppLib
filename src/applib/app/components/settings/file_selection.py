import os
from qfluentwidgets import PushButton
from PyQt6.QtWidgets import QWidget, QFileDialog

from typing import Optional, override

from .base_setting import BaseSetting

from module.tools.types.config import AnyConfig
from module.tools.types.general import StrPath


class ConfigFileSelect(BaseSetting):
    def __init__(
        self,
        config: AnyConfig,
        configkey: str,
        configname: str,
        options: dict,
        caption: str,
        directory: StrPath,
        filter: str,
        initial_filter: str,
        parent: Optional[QWidget] = None,
    ) -> None:
        """File Select widget connected to a config key.

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting.

        configkey : str
            The option key in the config which should be associated with this setting.

        configname : str
            The name of the config.

        options : dict
            The options associated with the `configkey`.

        parent : QWidget, optional
            Parent of this class, by default `None`.
        """
        super().__init__(
            config=config,
            configkey=configkey,
            configname=configname,
            options=options,
            currentValue=config.getValue(configkey, configname),
            defaultValue=config.getValue(
                configkey, configname, use_template_config=True
            ),
            backupValue=None,
            isDisabled=False,
            notifyDisabled=True,
            parent=parent,
        )
        try:
            self.caption = caption
            self.directory = (
                os.path.split(self.currentValue)[0] if self.currentValue else directory
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
        type = values[0]
        value = values[1]
        if type == "content":
            self.notifyParent.emit(("content", self.currentValue))

    def _onSelectClicked(self) -> None:
        file = QFileDialog.getOpenFileName(
            parent=self.parent() if self.parent() else self,
            caption=self.caption,
            directory=self.directory,
            filter=self.filter,
            initialFilter=self.initial_filter,
        )
        if file[0]:
            self.setValue(file[0])
            self.directory = os.path.split(file[0])[0]

    def setValue(self, value: StrPath) -> None:
        if super().setValue(value):
            self.notifyParent.emit(("content", self.currentValue))

    @override
    def setWidgetValue(self, value: StrPath) -> None:
        pass
