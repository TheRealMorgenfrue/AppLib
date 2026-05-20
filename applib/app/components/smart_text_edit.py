from typing import override

from PyQt6.QtWidgets import QWidget
from qfluentwidgets import TextEdit


class SmartTextEdit(TextEdit):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ensureVisible = False

        # Only emit the valueChanged() signal when the user releases the slider
        self.verticalScrollBar().setTracking(False)

        self.__connectSignalToSlot()

    def __connectSignalToSlot(self):
        self.verticalScrollBar().sliderReleased.connect(
            self._onVerticalScrollBarReleased
        )

    def _onVerticalScrollBarReleased(self):
        self.ensureVisible = (
            self.verticalScrollBar().value() == self._getDocumentLength()
        )

    def _getDocumentLength(self) -> int:
        sc = self.verticalScrollBar()
        return sc.maximum() - sc.minimum() + sc.pageStep()

    @override
    def append(self, text: str | None = None):
        super().append(text)
        if self.ensureVisible:
            self.verticalScrollBar().setSliderPosition(self._getDocumentLength())
