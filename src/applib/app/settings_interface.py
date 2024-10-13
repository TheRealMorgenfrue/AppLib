import traceback
import os
from typing import Any, Hashable, Optional

from qfluentwidgets import ScrollArea, qrouter, PopUpAniStackedWidget
from PyQt6.QtCore import Qt, QEasingCurve
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from .common.core_stylesheet import CoreStyleSheet
from .components.infobar_test import InfoBar, InfoBarPosition
from .components.sample_card import SampleCardView
from .settings_interface_app import SettingsInterface_App

from module.config.internal.app_args import AppArgs
from module.config.internal.names import ModuleNames
from module.logging import logger


class SettingsInterface(ScrollArea):
    _logger = logger

    def __init__(self, parent: Optional[QWidget] = None):
        try:
            super().__init__(parent=parent)
            self._widgets = {}  # type: dict[Any, QWidget]
            self.view = QWidget(self)
            self.vBoxLayout = QVBoxLayout(self.view)
            self.stackedWidget = PopUpAniStackedWidget()

            self.app_settings = None
            self.pu_settings = None

            self.__initWidget()

            self._loadAppInterface()
        except Exception:
            self.deleteLater()
            raise

    def __initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.__setQss()
        self.__initLayout()

    def __setQss(self):
        self.setObjectName("settingInterface")
        self.view.setObjectName("view")
        CoreStyleSheet.SETTINGS_INTERFACE.apply(self)

    def __initLayout(self):
        self.sampleCardView = SampleCardView()
        self.vBoxLayout.addWidget(self.sampleCardView)
        self.vBoxLayout.addWidget(self.stackedWidget, stretch=1)
        self.vBoxLayout.setSpacing(20)
        self.stackedWidget.setHidden(True)

    def __onCurrentIndexChanged(self, pack: tuple):
        (widget_id,) = pack
        widget = self._widgets.get(widget_id, None)
        if widget:
            qrouter.push(self.stackedWidget, widget.objectName())
            self.stackedWidget.setCurrentWidget(
                widget, duration=250, easingCurve=QEasingCurve.Type.InQuad
            )
            self.stackedWidget.setHidden(False)
        else:
            InfoBar.error(
                title=self.tr("Module is not available"),
                content=self.tr(
                    f"Please check the logs at:\n {AppArgs.log_dir.resolve()}"
                ),
                orient=Qt.Orientation.Vertical,
                isClosable=False,
                duration=5000,
                position=InfoBarPosition.TOP,
                parent=self,
            )

    def _loadAppInterface(self) -> None:
        try:
            self.app_settings = SettingsInterface_App()
        except Exception:
            self._logger.error(
                f"Could not load {ModuleNames.app_name} settings panel\n"
                + traceback.format_exc(limit=AppArgs.traceback_limit)
            )
            self.app_settings = None
        self._createSampleCard(
            widget_id=ModuleNames.app_name,
            # REVIEW: Set your own icon!
            icon=f"{AppArgs.logo_dir}/logo.png",
            title=ModuleNames.app_name,
            widget=self.app_settings,
        )

    def _createSampleCard(
        self, widget_id: Hashable, icon, title: str, widget: QWidget | None
    ):
        if widget:
            self._addSampleCardWidget(widget_id, widget)
        else:
            title += self.tr("\n❌Unavailable")

        self.sampleCardView.addSampleCard(
            icon=icon,
            title=title,
            widget_id=widget_id,
            onClick=self.__onCurrentIndexChanged,
        )

    def _addSampleCardWidget(self, widget_id: Hashable, widget: QWidget) -> None:
        if widget_id in self._widgets:
            err_msg = f"ID '{widget_id}' already exists"
            raise ValueError(err_msg)
        self._widgets |= {widget_id: widget}
        self.stackedWidget.addWidget(widget)
