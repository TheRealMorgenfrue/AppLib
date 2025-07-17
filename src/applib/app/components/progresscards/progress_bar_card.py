from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QWidget
from qfluentwidgets import IndeterminateProgressBar, ProgressBar

from .progress_card import ProgressCard


class ProgressBarCard(ProgressCard):
    def __init__(self, title: str, parent: QWidget | None = None):
        super().__init__(title, ProgressBar(), parent)
        self.hBoxLayout = QHBoxLayout(self)

        self._initLayout()

    def _initLayout(self) -> None:
        self.progressWidget.setFixedHeight(8)

        self.hBoxLayout.setSpacing(20)
        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.hBoxLayout.addWidget(self.titleLabel)
        self.hBoxLayout.addWidget(self.progressWidget)

    # def resizeEvent(self, a0: QResizeEvent | None) -> None:
    #     super().resizeEvent(a0)
    #     text_rect = self.titleLabel.fontMetrics().boundingRect(self.titleLabel.text())
    #     widget_rect = self.progressWidget.rect()

    #     wpad = 20
    #     hpad = 20
    #     w = widget_rect.width() + wpad
    #     h = text_rect.height() + widget_rect.height() + hpad

    #     if text_rect.width() > w - wpad // 2:
    #         self.titleLabel.setWordWrap(True)
    #         h += text_rect.height() * ceil(text_rect.width() / w)

    #     self.setFixedHeight(h)
    #     self.hBoxLayout.update()


class IndeterminateProgressBarCard(ProgressBarCard):
    def __init__(self, title: str, parent: QWidget | None = None):
        super().__init__(title, IndeterminateProgressBar(), parent)
