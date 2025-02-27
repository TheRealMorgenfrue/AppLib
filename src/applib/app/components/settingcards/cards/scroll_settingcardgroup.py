from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from qfluentwidgets import ScrollArea, SettingCardGroup

from ..card_group import CardGroupBase


class ScrollSettingCardGroup(CardGroupBase, ScrollArea):
    def __init__(self, title: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._cardGroup = SettingCardGroup(title, self)
        self.vGeneralLayout = QVBoxLayout(self)
        self.vGeneralLayout.addWidget(self._cardGroup)
        self._initWidget()

    def _initWidget(self) -> None:
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 10, 10)
        self.setWidget(self._cardGroup)
        self.setWidgetResizable(True)

    def addSettingCard(self, card: QWidget) -> None:
        self._cardGroup.addSettingCard(card)

    def getTitleLabel(self) -> QLabel:
        return self._cardGroup.titleLabel
