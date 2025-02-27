from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ....common.core_stylesheet import CoreStyleSheet
from ..card_group import CardGroupBase


class CardWidgetGroup(CardGroupBase, QWidget):
    def __init__(self, title: str, parent: Optional[QWidget] = None) -> None:
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
