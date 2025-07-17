import os
from typing import override

from PyQt6.QtWidgets import QFileDialog, QWidget
from qfluentwidgets import PushButton

from ....module.configuration.runners.converters.converter import Converter
from ....module.configuration.tools.template_utils.options import GUIOption
from ....module.tools.types.config import AnyConfig
from .base_setting import BaseSetting


class CoreFileSelect(BaseSetting):
    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        option: GUIOption,
        caption: str,
        directory: str,
        show_dir_only: bool = False,
        filter: str | None = None,
        selected_filter: str | None = None,
        converter: Converter | None = None,
        path="",
        parent: QWidget | None = None,
    ) -> None:
        """
        File Select widget connected to a config key.

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting.

        config_key : str
            The option key in the config which should be associated with this setting.

        option : GUIOption
            The options associated with `config_key`.

        caption : str
            Title of the file dialog.

        directory : str
            Open file dialog in this directory.
            If a value for `config_key` exists, it overrides this directory parameter.

        show_dir_only : bool, optional
            Only show directories. `filter` and `selected_filter` are ignored.
            By default False.

        filter : str | None, optional
            File extension filter. Only files matching this are shown.
            If None, all files are shown.
            If you want multiple filters, seperate them with ;;

            For instance:
            ```
            "Images (*.png *.xpm *.jpg);;Text files (*.txt);;XML files (*.xml)"
            ```

        selected_filter : str | None, optional
            The selected file extension filter.
            If None, all files are shown.
            If you want multiple filters, seperate them with ;;

            For instance:
            ```
            "Images (*.png *.xpm *.jpg);;Text files (*.txt);;XML files (*.xml)"
            ```

        converter : Converter | None, optional
            The value converter used to convert values between config and GUI representation.

        path : str, optional
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
        self.show_dir_only = show_dir_only
        self.caption = caption
        self.filter = None if show_dir_only else filter
        self.selected_filter = None if show_dir_only else selected_filter
        self.dialogParent = parent if parent else self
        try:
            self.directory = (
                os.path.split(self.current_value)[0]
                if self.current_value
                else directory
            )
            self.fileDialog = QFileDialog()
            self.setting = PushButton("Select")
            self.buttonlayout.addWidget(self.setting)
            self._connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def _connectSignalToSlot(self) -> None:
        self.setting.clicked.connect(self._onSelectClicked)
        self.notify.connect(self._onParentNotification)

    def _onParentNotification(self, values: tuple) -> None:
        super()._onParentNotification(values)
        type, value = values
        if type == "content":
            self.setWidgetValue(self.current_value)

    def _onSelectClicked(self) -> None:
        if self.show_dir_only:
            value = self.fileDialog.getExistingDirectory(
                parent=self.dialogParent,
                caption=self.caption,
                directory=self.directory,
                options=QFileDialog.Option.ShowDirsOnly,
            )
        else:
            value = self.fileDialog.getOpenFileName(
                parent=self.dialogParent,
                caption=self.caption,
                directory=self.directory,
                filter=self.filter,
                initialFilter=self.selected_filter,
            )[0]
        if value:
            self.setConfigValue(value)
            self.directory = os.path.split(value)[0]

    @override
    def _setWidgetValue(self, value: str) -> None:
        self.notifyParent.emit(("content", value))
