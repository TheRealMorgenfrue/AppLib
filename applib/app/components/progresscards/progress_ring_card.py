from math import ceil
from qfluentwidgets import ProgressRing, IndeterminateProgressRing, setFont
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from typing import Optional


from app.components.progresscards.progress_card import ProgressCard


class ProgressRingCard(ProgressCard):
    def __init__(self, title: str, parent: Optional[QWidget] = None):
        super().__init__(title, ProgressRing(), parent)
        self.vBoxLayout = QVBoxLayout(self)

        self.__initLayout()

    def __initLayout(self) -> None:
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        setFont(self.progressWidget, 28, 400)
        self.progressWidget.setStrokeWidth(10)
        self.progressWidget.setFixedSize(120, 120)
        self.progressWidget.setTextVisible(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(15)
        self.vBoxLayout.addWidget(self.titleLabel, alignment=Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(
            self.progressWidget, alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.vBoxLayout.addStretch(1)

    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        super().resizeEvent(a0)
        text_rect = self.titleLabel.fontMetrics().boundingRect(self.titleLabel.text())
        widget_rect = self.progressWidget.rect()

        wpad = 50
        hpad = 40
        w = widget_rect.width() + wpad
        h = text_rect.height() + widget_rect.height() + hpad

        if text_rect.width() > w - wpad // 2:
            self.titleLabel.setWordWrap(True)
            h += text_rect.height() * ceil(text_rect.width() / w)

        self.setFixedSize(w, h)
        self.vBoxLayout.update()


class IndeterminateProgressRingCard(ProgressRingCard):
    def __init__(self, title: str, parent: Optional[QWidget] = None):
        super().__init__(title, IndeterminateProgressRing(), parent)
