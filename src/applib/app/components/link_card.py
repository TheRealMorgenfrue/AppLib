from qfluentwidgets import (
    IconWidget,
    FluentIcon,
    FluentIconBase,
    TextWrap,
    SingleDirectionScrollArea,
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QIcon
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget, QHBoxLayout

from typing import Optional, Union

from ..common.core_stylesheet import CoreStyleSheet


class LinkCard(QFrame):

    def __init__(
        self,
        icon: Union[str, QIcon, FluentIconBase],
        title: str,
        content: str,
        url: QUrl,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent=parent)
        self.url = QUrl(url)
        self.setFixedSize(188, 190)
        self.iconWidget = IconWidget(icon, self)
        self.titleLabel = QLabel(title, self)
        self.contentLabel = QLabel(TextWrap.wrap(content, 28, False)[0], self)
        self.contentLabel.setStyleSheet("font-size: 14px; font-weight: 600;")
        self.urlWidget = IconWidget(FluentIcon.LINK, self)

        self._initWidget()

    def _initWidget(self) -> None:
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.iconWidget.setFixedSize(54, 54)
        self.urlWidget.setFixedSize(16, 16)

        self.vbox_layout = QVBoxLayout(self)
        self.vbox_layout.setSpacing(0)
        self.vbox_layout.setContentsMargins(24, 24, 0, 13)
        self.vbox_layout.addWidget(self.iconWidget)
        self.vbox_layout.addSpacing(16)
        self.vbox_layout.addWidget(self.titleLabel)
        self.vbox_layout.addSpacing(8)
        self.vbox_layout.addWidget(self.contentLabel)
        self.vbox_layout.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self.urlWidget.move(160, 162)

        self.titleLabel.setObjectName("titleLabel")
        self.contentLabel.setObjectName("contentLabel")

    def mouseReleaseEvent(self, e) -> None:
        super().mouseReleaseEvent(e)
        QDesktopServices.openUrl(self.url)


class LinkCardView(SingleDirectionScrollArea):
    """Link card view"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent, Qt.Orientation.Horizontal)
        self._view = QWidget(self)
        self.hBoxLayout = QHBoxLayout(self._view)

        self.hBoxLayout.setContentsMargins(36, 0, 0, 0)
        self.hBoxLayout.setSpacing(12)
        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.setWidget(self._view)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._view.setObjectName("view")
        CoreStyleSheet.LINK_CARD.apply(self)

    def addCard(
        self,
        icon: Union[str, QIcon, FluentIconBase],
        title: str,
        content: str,
        url: QUrl,
    ) -> None:
        card = LinkCard(icon, title, content, url, self._view)
        self.hBoxLayout.addWidget(card, 0, Qt.AlignmentFlag.AlignLeft)
