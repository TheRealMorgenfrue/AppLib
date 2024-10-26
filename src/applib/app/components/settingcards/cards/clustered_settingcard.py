from qfluentwidgets import (
    FluentIconBase,
    FluentStyleSheet,
    isDarkTheme,
)
from PyQt6.QtGui import QIcon, QPainter, QColor, QResizeEvent, QPaintEvent
from PyQt6.QtWidgets import QWidget, QFrame, QVBoxLayout
from PyQt6.QtCore import Qt

from typing import Optional, Union, override

from ..card_base import (
    CardBase,
    DisableWrapper,
    ParentCardBase,
)
from .expanding_settingcard import GroupSeparator
from .settingcard import FluentSettingCard
from module.tools.types.gui_settings import AnySetting


class ClusteredSettingCard(CardBase, ParentCardBase, QFrame):
    def __init__(
        self,
        setting: str,
        icon: Union[str, QIcon, FluentIconBase],
        title: str,
        content: Optional[str],
        hasDisableButton: bool,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(cardName=setting, parent=parent)
        self.viewLayout = QVBoxLayout(self)

        self.card = FluentSettingCard(
            setting=setting,
            icon=icon,
            title=title,
            content=content,
            hasDisableButton=hasDisableButton,
        )
        self._setQss()
        self._connectSignalToSlot()
        self.addChild(self.card)

    def _setQss(self) -> None:
        FluentStyleSheet.EXPAND_SETTING_CARD.apply(self)

    def _connectSignalToSlot(self) -> None:
        self.notifyCard.connect(self.card.notifyCard.emit)
        self.disableCard.connect(self.setDisableAll)

    def resizeEvent(self, e: QResizeEvent | None) -> None:
        # FIXME: Resize bug with FluentSettingCards when initially loaded where a card reports incorrect sizeHint
        # causing the ClusteredSettingCard's height to be too large. The issue resolves itself when the user manually
        # resizes the window causing the affected widgets to recalculate their sizes correctly - however it does look odd.
        # The bug occurs because the FluentLabel reports incorrect sizeHint initially - but ONLY in a ClusteredSettingCard
        self.resize(self.width(), self.viewLayout.sizeHint().height())

    def paintEvent(self, e: QPaintEvent | None) -> None:
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        if isDarkTheme():
            painter.setBrush(QColor(255, 255, 255, 13))
            painter.setPen(QColor(0, 0, 0, 50))
        else:
            painter.setBrush(QColor(255, 255, 255, 170))
            painter.setPen(QColor(0, 0, 0, 19))

        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 6, 6)

    @override
    def addChild(self, child: QWidget) -> None:
        # Add separator
        if self.viewLayout.count() >= 1:
            self.viewLayout.addWidget(GroupSeparator())

        self.viewLayout.addWidget(child)

    @override
    def getOption(self) -> AnySetting:
        return self.card.getOption()

    @override
    def setDisableAll(self, wrapper: DisableWrapper) -> None:
        self.card.setDisableAll(wrapper)

    @override
    def setOption(
        self,
        option: AnySetting,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignRight,
    ) -> None:
        self.card.setOption(option, alignment)
