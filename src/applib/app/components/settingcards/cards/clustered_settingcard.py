from qfluentwidgets import (
    FluentIconBase,
    isDarkTheme,
)
from PyQt6.QtGui import QIcon, QPainter, QColor, QResizeEvent, QPaintEvent
from PyQt6.QtWidgets import QWidget, QFrame, QVBoxLayout
from PyQt6.QtCore import Qt, QObject, QEvent

from typing import Optional, Union, override

from ....common.core_stylesheet import CoreStyleSheet
from ..card_base import (
    CardBase,
    DisableWrapper,
    ParentCardBase,
)
from .expanding_settingcard import GroupSeparator
from .settingcard import FluentSettingCard
from .....module.tools.types.gui_settings import AnySetting


class ClusterHeaderSettingCard(FluentSettingCard):
    def __init__(
        self,
        card_name: str,
        icon: Union[str, QIcon, FluentIconBase],
        title: str,
        content: Optional[str],
        has_disable_button: bool,
        is_frameless: bool = False,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(
            card_name, icon, title, content, has_disable_button, is_frameless, parent
        )
        self.titleLabel.installEventFilter(self)
        self.contentLabel.installEventFilter(self)

    def eventFilter(self, obj: QObject, e: QEvent) -> None:
        if (
            obj in [self.titleLabel, self.contentLabel]
            and e.type() == QEvent.Type.Resize
        ):
            self.resizeEvent(e)
            if self.parentWidget():
                self.parentWidget().resizeEvent(e)
        return super().eventFilter(obj, e)


class ClusteredSettingCard(CardBase, ParentCardBase, QFrame):
    def __init__(
        self,
        card_name: str,
        icon: Union[str, QIcon, FluentIconBase],
        title: str,
        content: Optional[str],
        has_disable_button: bool,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(card_name=card_name, parent=parent)
        self.viewLayout = QVBoxLayout(self)
        self.card = ClusterHeaderSettingCard(
            card_name=card_name,
            icon=icon,
            title=title,
            content=content,
            has_disable_button=has_disable_button,
        )
        self.__setQss()
        self.__connectSignalToSlot()
        self.addChild(self.card)

    def __setQss(self) -> None:
        CoreStyleSheet.SETTING_CARD.apply(self)

    def __connectSignalToSlot(self) -> None:
        self.notifyCard.connect(self.card.notifyCard.emit)
        self.disableCard.connect(self.setDisableAll)

    def resizeEvent(self, e: QResizeEvent | None) -> None:
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
