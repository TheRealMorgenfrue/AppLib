from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ....common.core_stylesheet import CoreStyleSheet


class CardWidgetGroup(QWidget):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.titleLabel = QLabel(title)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(
            self.titleLabel, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self._setQss()

    def _setQss(self):
        self.titleLabel.setObjectName("titleLabel")
        self.setObjectName("view")
        CoreStyleSheet.SETTING_WIDGET.apply(self)

    def addSettingCard(self, widget: QWidget) -> None:
        self.vBoxLayout.addWidget(widget)

    def getTitleLabel(self) -> QLabel:
        return self.titleLabel
