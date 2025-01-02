import traceback
from typing import Hashable, Optional, Union

from qfluentwidgets import ScrollArea, qrouter, PopUpAniStackedWidget, FluentIconBase
from PyQt6.QtCore import Qt, QEasingCurve
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtGui import QIcon

from ..common.core_stylesheet import CoreStyleSheet
from ..components.infobar_test import InfoBar, InfoBarPosition
from ..components.sample_card import SampleCardView

from ...module.config.internal.core_args import CoreArgs
from ...module.logging import logger


class CoreSettingsInterface(ScrollArea):
    _logger = logger

    def __init__(self, parent: Optional[QWidget] = None):
        """
        The default main settings page.

        Parameters
        ----------
        parent : QWidget, optional
            The parent of the main settings page.
            By default `None`.
        """
        super().__init__(parent=parent)
        self._widgets = {}  # type: dict[Hashable, QWidget]
        self._view = QWidget(self)
        self._sampleCardView = SampleCardView()
        self.vBoxLayout = QVBoxLayout(self._view)
        self.stackedWidget = PopUpAniStackedWidget()
        self._initWidget()

    def _initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self._view)
        self.setWidgetResizable(True)

        self._setQss()
        self._initLayout()

    def _setQss(self):
        self.setObjectName("settingInterface")
        self._view.setObjectName("view")
        CoreStyleSheet.SETTINGS_INTERFACE.apply(self)

    def _initLayout(self):
        self.vBoxLayout.addWidget(self._sampleCardView)
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
                    f"Please check the logs at:\n {CoreArgs.log_dir.resolve()}"
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
            if widget_id in self._widgets:
                err_msg = f"ID '{widget_id}' already exists"
                raise ValueError(err_msg)
            self._widgets |= {widget_id: widget}
            self.stackedWidget.addWidget(widget)
        else:
            title += self.tr("\n❌Unavailable")

        self._sampleCardView.addSampleCard(
            icon=icon,
            title=title,
            widget_id=widget_id,
            onClick=self._onCurrentIndexChanged,
        )

    def addSubInterface(
        self, icon: Union[str, QIcon, FluentIconBase], title: str, widget: QWidget
    ) -> None:
        """
        Add a subinterface to the main settings page.

        Parameters
        ----------
        icon : Union[str, QIcon, FluentIconBase]
            Icon for the subinterface.

        title : str
            Title for the subinterface.

        widget : QWidget
            The widget to add as a subinterface.
        """
        try:
            self._createSampleCard(
                widget_id=id(widget), icon=icon, title=title, widget=widget
            )
        except Exception:
            self._logger.error(
                f"Failed to add subinterface '{type(widget).__name__}'\n"
                + f"{traceback.format_exc(limit=CoreArgs.traceback_limit)}"
            )
            widget.deleteLater()
