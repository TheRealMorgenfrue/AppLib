from PyQt6.QtWidgets import QWidget
from qfluentwidgets import FlowLayout, ScrollArea

from ..common.core_stylesheet import CoreStyleSheet


class FlowArea(ScrollArea):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._view = QWidget(self)
        self.flowLayout = FlowLayout(self._view, needAni=True)

        self._initWidget()
        self._initLayout()

    def _initWidget(self) -> None:
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self._view)
        self.setWidgetResizable(True)
        self._setQss()

    def _setQss(self) -> None:
        self.setObjectName("flowConsoles")
        self._view.setObjectName("view")
        CoreStyleSheet.GENERIC.apply(self)

    def _initLayout(self) -> None:
        self.flowLayout.setContentsMargins(0, 0, 0, 0)
        self.flowLayout.setHorizontalSpacing(30)
        self.flowLayout.setVerticalSpacing(30)
