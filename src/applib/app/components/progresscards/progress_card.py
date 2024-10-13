from qfluentwidgets import (
    CardWidget,
    ProgressBar,
    ProgressRing,
    IndeterminateProgressBar,
    IndeterminateProgressRing,
    themeColor,
)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QColor

from typing import Optional, Union

from ...common.core_stylesheet import CoreStyleSheet


class ProgressCard(CardWidget):
    def __init__(
        self,
        title: str,
        progressWidget: Union[
            ProgressBar,
            ProgressRing,
            IndeterminateProgressBar,
            IndeterminateProgressRing,
        ],
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.titleLabel = QLabel(title)
        self.progressWidget = progressWidget

        self.__initLayout()
        self.__setQss()

    def __initLayout(self) -> None:
        self.setContentsMargins(10, 10, 10, 10)

    def __setQss(self) -> None:
        self.titleLabel.setObjectName("progressTitleLabel")
        CoreStyleSheet.PROGRESS_BAR.apply(self)

    def start(self) -> None:
        """Put progress card in started mode"""
        if isinstance(
            self.progressWidget, (IndeterminateProgressBar, IndeterminateProgressRing)
        ):
            self.progressWidget.start()
            return

        self.progressWidget.reset()
        barColor = themeColor()
        self.progressWidget.setCustomBarColor(barColor, barColor)

    def stop(self, barColor: Union[str, Qt.GlobalColor, QColor] = "#2dc2c7") -> None:
        """Put progress card in stopped mode.

        Parameters
        ----------
        barColor : Union[str, Qt.GlobalColor, QColor], optional
            Color of the progress card when stopped.
            Has no effect on indeterminate progress cards.
            By default "#2dc2c7".
        """
        if isinstance(
            self.progressWidget, (IndeterminateProgressBar, IndeterminateProgressRing)
        ):
            self.progressWidget.stop()
            return

        self.progressWidget.setCustomBarColor(barColor, barColor)

    def resume(self) -> None:
        """Put progress card in resumed mode.
        This changes the progress color back to normal (by default theme color).
        """
        self.progressWidget.resume()

    def pause(self) -> None:
        """Put progress card in paused mode.
        This changes the progress color to yellow.
        """
        self.progressWidget.pause()

    def setPaused(self, isPaused: bool) -> None:
        """Put progress card in paused mode or in resumed mode.
        This changes the progress color to yellow or back to normal (by default theme color).
        """
        self.progressWidget.setPaused(isPaused)

    def isPaused(self) -> bool:
        return self.progressWidget.isPaused()

    def error(self) -> None:
        """Put progress card in error mode.
        This changes the progress color to red.
        """
        self.progressWidget.error()

    def setError(self, isError: bool) -> None:
        """Put progress card in error mode or in resumed mode.
        This changes the progress color to red or back to normal (by default theme color).
        """
        self.progressWidget.setError(isError)

    def isError(self) -> bool:
        return self.progressWidget.isError()
