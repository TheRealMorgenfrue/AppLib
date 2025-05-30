from qfluentwidgets import PushButton, TextEdit
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import Qt

from typing import Optional

from ..common.core_stylesheet import CoreStyleSheet


class InputView(QWidget):
    def __init__(self, label: str, parent: Optional[QWidget] = None) -> None:
        """Text editor where user can input multi-line text.

        Parameters
        ----------
        label : str
            Title label

        parent : Optional[QWidget], optional
            Parent widget. By default None
        """
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.buttonLayout = QHBoxLayout()
        self.label = QLabel(label)
        self.textEdit = TextEdit(parent=self)
        self.clearButton = None

        self._initWidget()
        self._initLayout()

    def _initWidget(self) -> None:
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.label.setWordWrap(True)
        self.textEdit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.textEdit.setReadOnly(False)
        self.textEdit.setUndoRedoEnabled(True)
        self._setQss()

    def _initLayout(self) -> None:
        self.buttonLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.buttonLayout.setSpacing(20)

        self.vBoxLayout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.textEdit, stretch=2)
        self.vBoxLayout.addLayout(self.buttonLayout)
        self.vBoxLayout.addStretch(1)

    def _setQss(self) -> None:
        self.label.setObjectName("Label")
        self.setObjectName("inputView")
        CoreStyleSheet.INPUT_VIEW.apply(self)

    def disableText(self, disable: bool) -> None:
        self.textEdit.setDisabled(disable)

    def addButton(self, button: QWidget) -> None:
        self.buttonLayout.addWidget(button)

    def enableClearButton(self) -> None:
        if self.clearButton is None:
            self.clearButton = PushButton(self.tr("Clear"), self)
            self.clearButton.clicked.connect(self.textEdit.clear)
            self.buttonLayout.addWidget(self.clearButton)

    def setReadOnly(self, value: bool) -> None:
        self.textEdit.setReadOnly(value)

    def setText(self, text: str) -> None:
        self.textEdit.setText(text)

    def text(self) -> str:
        return self.textEdit.toPlainText()
