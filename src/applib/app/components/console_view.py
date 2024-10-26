from qfluentwidgets import PrimaryPushButton, TextEdit
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QSize, Qt, pyqtSignal

from typing import Optional

from ..common.core_stylesheet import CoreStyleSheet


class ConsoleView(QWidget):
    terminationRequest = pyqtSignal(int)
    activated = pyqtSignal(bool)

    def __init__(
        self,
        processID: int,
        sizeHint: Optional[QSize] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._sizeHint = sizeHint if sizeHint else QSize(400, 400)
        self.processID = processID
        self.consoleLabel = QLabel(self.tr(f"Thread {processID}"))
        self.textEdit = TextEdit(self)
        self.terminateButton = PrimaryPushButton(self.tr("Terminate"), self)
        self.vBoxLayout = QVBoxLayout(self)
        self.buttonLayout = QHBoxLayout()

        self._initWidget()
        self._initLayout()
        self._connectSignalToSlot()

    def _initWidget(self) -> None:
        self.textEdit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.textEdit.setReadOnly(True)
        # Block count == Line count. NOTE: Also disables undo/redo history.
        self.textEdit.document().setMaximumBlockCount(1000)
        self.terminateButton.setDisabled(True)
        self._setQss()

    def _initLayout(self) -> None:
        self.buttonLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.buttonLayout.setSpacing(20)
        self.buttonLayout.addWidget(self.terminateButton)

        self.vBoxLayout.addWidget(
            self.consoleLabel, alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.vBoxLayout.addWidget(self.textEdit, stretch=1)
        self.vBoxLayout.addLayout(self.buttonLayout)

    def _setQss(self) -> None:
        self.consoleLabel.setObjectName("Label")
        self.setObjectName("console")
        CoreStyleSheet.CONSOLE_VIEW.apply(self)

    def _connectSignalToSlot(self) -> None:
        self.terminateButton.clicked.connect(
            lambda: self.terminationRequest.emit(self.processID)
        )
        self.activated.connect(self.terminateButton.setEnabled)

    def insert(self, text: str) -> None:
        self.textEdit.insertPlainText(text)

    def append(self, text: str, color: Optional[QColor] = None) -> None:
        if color:
            self.textEdit.setTextColor(color)
        self.textEdit.append(text.strip())

    def clear(self) -> None:
        self.textEdit.clear()

    def updateSizeHint(self, size: QSize) -> None:
        self._sizeHint = size
        self.updateGeometry()

    def minimumSizeHint(self) -> QSize:
        return self._sizeHint
