from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QTextEdit, QVBoxLayout, QWidget
from qfluentwidgets import PrimaryPushButton

from ..common.core_stylesheet import CoreStyleSheet
from .smart_text_edit import SmartTextEdit


class ConsoleView(QWidget):
    terminate_process = pyqtSignal(int)
    activated = pyqtSignal(bool)

    def __init__(
        self,
        process_id: int,
        sizeHint: QSize | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._sizeHint = sizeHint if sizeHint is not None else QSize(400, 400)
        self.process_id = process_id
        self.consoleLabel = QLabel(self.tr(f"Thread {process_id}"))
        self.textEdit = SmartTextEdit(self)
        self.terminateButton = PrimaryPushButton(self.tr("Terminate"), self)
        self.vBoxLayout = QVBoxLayout(self)
        self.buttonLayout = QHBoxLayout()

        self._initWidget()
        self._initLayout()
        self.__connectSignalToSlot()

    def _initWidget(self) -> None:
        self.textEdit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.textEdit.setReadOnly(True)
        # Block count == Line count. NOTE: Also disables undo/redo history.
        self.textEdit.document().setMaximumBlockCount(1000)  # type: ignore
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

    def __connectSignalToSlot(self) -> None:
        self.terminateButton.clicked.connect(
            lambda: self.terminate_process.emit(self.process_id)
        )
        self.activated.connect(self._onActivated)

    def _onActivated(self, activated: bool):
        if self.terminateButton.isEnabled() != activated:
            self.terminateButton.setEnabled(activated)

    def insert(self, text: str) -> None:
        self.textEdit.insertPlainText(text)

    def append(
        self, text: str, color: QColor | None = None, bold: bool = False
    ) -> None:
        if color:
            self.textEdit.setTextColor(color)
        if bold:
            self.textEdit.setFontWeight(QFont.Weight.Bold)

        self.textEdit.append(text.strip())

    def clear(self) -> None:
        self.textEdit.clear()

    def updateSizeHint(self, size: QSize) -> None:
        self._sizeHint = size
        self.updateGeometry()

    def minimumSizeHint(self) -> QSize:
        return self._sizeHint
