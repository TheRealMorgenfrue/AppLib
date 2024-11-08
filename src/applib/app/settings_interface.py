import traceback
from typing import Any, Hashable, Optional, Union

from qfluentwidgets import ScrollArea, qrouter, PopUpAniStackedWidget, FluentIconBase
from PyQt6.QtCore import Qt, QEasingCurve
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtGui import QIcon

from .common.core_stylesheet import CoreStyleSheet
from .components.infobar_test import InfoBar, InfoBarPosition
from .components.sample_card import SampleCardView
from .settings_interface_app import SettingsInterface_App

from module.config.internal.app_args import AppArgs
from module.logging import logger


class CoreSettingsInterface(ScrollArea):
    _logger = logger

    def __init__(self, parent: Optional[QWidget] = None):
        try:
            super().__init__(parent=parent)
            self._widgets = {}  # type: dict[Any, QWidget]
            self.view = QWidget(self)
            self.vBoxLayout = QVBoxLayout(self.view)
            self.stackedWidget = PopUpAniStackedWidget()

            self._initWidget()
            self.__loadAppInterface()  # For testing purposes
        except Exception:
            self.deleteLater()
            raise

    def __loadAppInterface(self) -> None:
        # For testing purposes
        try:
            self.app_settings = SettingsInterface_App()
        except Exception:
            self._logger.error(
                f"Could not load {AppArgs.app_name} settings panel\n"
                + traceback.format_exc(limit=AppArgs.traceback_limit)
            )
            self.app_settings = None
        self._createSampleCard(
            widget_id=AppArgs.app_name,
            # REVIEW: Set your own icon!
            icon=f"{AppArgs.logo_dir}/logo.png",
            title=AppArgs.app_name,
            widget=self.app_settings,
        )

    def _initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self._setQss()
        self._initLayout()

    def _setQss(self):
        self.setObjectName("settingInterface")
        self.view.setObjectName("view")
        CoreStyleSheet.SETTINGS_INTERFACE.apply(self)

    def _initLayout(self):
        self.sampleCardView = SampleCardView()
        self.vBoxLayout.addWidget(self.sampleCardView)
        self.vBoxLayout.addWidget(self.stackedWidget, stretch=1)
        self.vBoxLayout.setSpacing(20)
        self.stackedWidget.setHidden(True)

    def _onCurrentIndexChanged(self, pack: tuple):
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

    def _createSampleCard(
        self,
        widget_id: Hashable,
        icon: Union[str, QIcon, FluentIconBase],
        title: str,
        widget: QWidget | None,
    ):
        if widget:
            self._addSampleCardWidget(widget_id, widget)
        else:
            title += self.tr("\n❌Unavailable")

        self.sampleCardView.addSampleCard(
            icon=icon,
            title=title,
            widget_id=widget_id,
            onClick=self._onCurrentIndexChanged,
        )

    def _addSampleCardWidget(self, widget_id: Hashable, widget: QWidget) -> None:
        if widget_id in self._widgets:
            err_msg = f"ID '{widget_id}' already exists"
            raise ValueError(err_msg)
        self._widgets |= {widget_id: widget}
        self.stackedWidget.addWidget(widget)
