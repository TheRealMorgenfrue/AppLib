from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

from typing import Optional

from ....common.core_stylesheet import CoreStyleSheet


class CardWidgetGroup(QWidget):
    def __init__(self, title: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.titleLabel = QLabel(title)
        self.vbox_layout = QVBoxLayout(self)
        self.vbox_layout.setContentsMargins(0, 0, 0, 0)
        self.vbox_layout.addWidget(
            self.titleLabel, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self._setQss()

    def _setQss(self):
        self.titleLabel.setObjectName("titleLabel")
        self.setObjectName("view")
        CoreStyleSheet.SETTING_WIDGET.apply(self)

    def addSettingCard(self, widget: QWidget) -> None:
        self.vbox_layout.addWidget(widget)

    def getTitleLabel(self) -> QLabel:
        return self.titleLabel
