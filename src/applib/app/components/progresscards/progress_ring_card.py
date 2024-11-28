from math import ceil
from qfluentwidgets import ProgressRing, IndeterminateProgressRing, setFont
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from typing import Optional


from .progress_card import ProgressCard


class ProgressRingCard(ProgressCard):
    def __init__(self, title: str, parent: Optional[QWidget] = None):
        super().__init__(title, ProgressRing(), parent)
        self.vbox_layout = QVBoxLayout(self)

        self._initLayout()

    def _initLayout(self) -> None:
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        setFont(self.progressWidget, 28, 400)
        self.progressWidget.setStrokeWidth(10)
        self.progressWidget.setFixedSize(120, 120)
        self.progressWidget.setTextVisible(True)

        self.vbox_layout.setContentsMargins(0, 0, 0, 0)
        self.vbox_layout.setSpacing(15)
        self.vbox_layout.addWidget(self.titleLabel, alignment=Qt.AlignmentFlag.AlignTop)
        self.vbox_layout.addWidget(
            self.progressWidget, alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.vbox_layout.addStretch(1)

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
        self.vbox_layout.update()


class IndeterminateProgressRingCard(ProgressRingCard):
    def __init__(self, title: str, parent: Optional[QWidget] = None):
        super().__init__(title, IndeterminateProgressRing(), parent)
