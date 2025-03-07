from typing import Optional, Union, override

from PyQt6.QtCore import QEvent, QObject, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPaintEvent, QResizeEvent
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QWidget
from qfluentwidgets import FluentIconBase, isDarkTheme

from .....module.tools.types.gui_settings import AnySetting
from ....common.core_stylesheet import CoreStyleSheet
from ..card_base import CardBase, DisableWrapper, ParentSettingCardBase
from .expanding_settingcard import GroupSeparator
from .settingcard import FluentSettingCard


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


class ClusteredSettingCard(ParentSettingCardBase, QFrame):
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
        self.add_child(self.card)

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
    def add_child(self, child: QWidget) -> None:
        # Add separator
        if self.viewLayout.count() >= 1:
            self.viewLayout.addWidget(GroupSeparator())
        self.viewLayout.addWidget(child)

    @override
    def get_option(self) -> AnySetting:
        return self.card.get_option()

    @override
    def setDisableAll(self, wrapper: DisableWrapper) -> None:
        self.card.setDisableAll(wrapper)

    @override
    def set_option(
        self,
        option: AnySetting,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignRight,
    ) -> None:
        self.card.set_option(option, alignment)
