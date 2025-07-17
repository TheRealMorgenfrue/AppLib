from collections.abc import Callable
from typing import Hashable

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import CardWidget, FlowLayout, FluentIconBase, IconWidget

from ..common.core_stylesheet import CoreStyleSheet


class SampleCard(CardWidget):
    sampleCardClicked = pyqtSignal(tuple)  # index

    def __init__(
        self,
        icon: str | QIcon | FluentIconBase,
        title: str,
        widget_id: Hashable,
        onClick: Callable | None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self.widget_id = widget_id
        if onClick:
            self.sampleCardClicked.connect(onClick)

        self.hBoxLayout = QVBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.iconWidget = IconWidget(icon, self)
        self.iconOpacityEffect = QGraphicsOpacityEffect(self)
        self.iconOpacityEffect.setOpacity(1)  # Set the initial semi-transparency
        self.iconWidget.setGraphicsEffect(self.iconOpacityEffect)

        self.titleOpacityEffect = QGraphicsOpacityEffect(self)
        self.titleOpacityEffect.setOpacity(1)  # Set the initial semi-transparency
        self.titleLabel = QLabel(title, self)
        self.titleLabel.setStyleSheet("font-size: 16px; font-weight: 500;")
        self.titleLabel.setGraphicsEffect(self.titleOpacityEffect)
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._adjustSize()

        self.vBoxLayout.setSpacing(2)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.hBoxLayout.addWidget(
            self.iconWidget, alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(
            self.titleLabel, alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.vBoxLayout.addStretch(1)

        self.titleLabel.setObjectName("titleLabel")

    def _adjustSize(self) -> None:
        title = self.titleLabel.text()
        # Define the initial card size
        w, h = 130, 160

        if (
            self.titleLabel.fontMetrics().boundingRect(self.titleLabel.text()).width()
            >= w
        ):
            self.titleLabel.setWordWrap(True)
            h += self.titleLabel.rect().height() - 15
        h += max(title.count("\n") - 1, 0) * 15
        self.setFixedSize(w, h)
        self.iconWidget.setFixedSize(110, 100)

    def mouseReleaseEvent(self, event) -> None:
        super().mouseReleaseEvent(event)
        self.sampleCardClicked.emit((self.widget_id,))

    def enterEvent(self, event) -> None:
        super().enterEvent(event)
        self.iconOpacityEffect.setOpacity(0.75)
        self.titleOpacityEffect.setOpacity(0.75)
        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )  # Set the mouse pointer to hand shape

    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
        self.iconOpacityEffect.setOpacity(1)
        self.titleOpacityEffect.setOpacity(1)
        self.setCursor(
            Qt.CursorShape.ArrowCursor
        )  # Restore the default shape of the mouse pointer

    def setTitle(self, text: str) -> None:
        self.titleLabel.setText(text)
        self._adjustSize()


class SampleCardView(QWidget):
    def __init__(self, title: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._cards = {}  # type: dict[int, SampleCard]
        self.titleLabel = QLabel(title, self) if title else None
        self.vBoxLayout = QVBoxLayout(self)
        self.flowLayout = FlowLayout()

        self.vBoxLayout.setContentsMargins(20, 0, 20, 0)
        self.vBoxLayout.setSpacing(10)

        self.flowLayout.setContentsMargins(0, 0, 0, 0)
        self.flowLayout.setHorizontalSpacing(12)
        self.flowLayout.setVerticalSpacing(12)

        if self.titleLabel:
            self.vBoxLayout.addWidget(self.titleLabel)
            self.titleLabel.setObjectName("viewTitleLabel")
        self.vBoxLayout.addLayout(self.flowLayout, 1)

        CoreStyleSheet.SAMPLE_CARD.apply(self)

    def addSampleCard(
        self,
        icon: str | QIcon | FluentIconBase,
        title: str,
        widget_id: Hashable,
        onClick: Callable | None = None,
    ) -> None:
        if self._cards.get(widget_id, None):
            err_msg = f"ID '{widget_id}' already exists"
            raise ValueError(err_msg)

        card = SampleCard(
            icon=icon,
            title=title,
            widget_id=widget_id,
            onClick=onClick,
            parent=self,
        )
        self.flowLayout.addWidget(card)
        self._cards[widget_id] = card

    def getSampleCard(self, widget_id: Hashable) -> SampleCard | None:
        return self._cards.get(widget_id)
