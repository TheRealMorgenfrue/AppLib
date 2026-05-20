from PyQt6.QtCore import QEvent, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QColor
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import BodyLabel, FluentStyleSheet, PrimaryPushButton, TextWrap
from qfluentwidgets.components.dialog_box.mask_dialog_base import MaskDialogBase
from qframelesswindow import FramelessDialog


class Ui_MessageBox:
    """Ui of message box"""

    yesSignal = pyqtSignal()
    cancelSignal = pyqtSignal()

    def _setUpUI(self, title: str, content: str, parent: QWidget | None = None):
        self.content = content
        self.titleLabel = QLabel(title, parent)
        self.contentLabel = BodyLabel(content, parent)

        self.buttonGroup = QFrame(parent)
        self.yesButton = PrimaryPushButton(self.tr("OK"), self.buttonGroup)
        self.cancelButton = QPushButton(self.tr("Cancel"), self.buttonGroup)

        self.vBoxLayout = QVBoxLayout(parent)
        self.textLayout = QVBoxLayout()
        self.widgetLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout(self.buttonGroup)

        self._initWidget()

    def _initWidget(self):
        self._setQss()
        self._initLayout()

        # fixes https://github.com/zhiyiYo/PyQt-Fluent-Widgets/issues/19
        self.yesButton.setAttribute(Qt.WidgetAttribute.WA_LayoutUsesWidgetRect)
        self.cancelButton.setAttribute(Qt.WidgetAttribute.WA_LayoutUsesWidgetRect)

        self.yesButton.setFocus()
        self.buttonGroup.setFixedHeight(81)

        self.contentLabel.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.contentLabel.setHidden(not bool(self.content))
        self._adjustText()

        self.yesButton.clicked.connect(self._onYesButtonClicked)
        self.cancelButton.clicked.connect(self._onCancelButtonClicked)

    def _adjustText(self):
        if self.content:
            if self.isWindow():
                if self.parent():
                    w = max(self.titleLabel.width(), self.parent().width())
                    chars = max(min(w / 9, 140), 30)
                else:
                    chars = 100
            else:
                w = max(self.titleLabel.width(), self.window().width())
                chars = max(min(w / 9, 100), 30)

            self.contentLabel.setText(TextWrap.wrap(self.content, chars, False)[0])

    def _initLayout(self):
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addLayout(self.textLayout)
        self.vBoxLayout.addLayout(self.widgetLayout)
        self.vBoxLayout.addWidget(self.buttonGroup, 0, Qt.AlignmentFlag.AlignBottom)
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)

        self.textLayout.setSpacing(12)
        self.textLayout.setContentsMargins(24, 24, 24, 24)
        self.textLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignTop)
        self.textLayout.addWidget(self.contentLabel, 0, Qt.AlignmentFlag.AlignTop)

        self.buttonLayout.setSpacing(12)
        self.buttonLayout.setContentsMargins(24, 24, 24, 24)
        self.buttonLayout.addWidget(self.yesButton, 1, Qt.AlignmentFlag.AlignVCenter)
        self.buttonLayout.addWidget(self.cancelButton, 1, Qt.AlignmentFlag.AlignVCenter)

    def _onCancelButtonClicked(self):
        self.reject()
        self.cancelSignal.emit()

    def _onYesButtonClicked(self):
        self.accept()
        self.yesSignal.emit()

    def _setQss(self):
        self.titleLabel.setObjectName("titleLabel")
        self.contentLabel.setObjectName("contentLabel")
        self.buttonGroup.setObjectName("buttonGroup")
        self.cancelButton.setObjectName("cancelButton")

        FluentStyleSheet.DIALOG.apply(self)
        FluentStyleSheet.DIALOG.apply(self.contentLabel)

        self.yesButton.adjustSize()
        self.cancelButton.adjustSize()

    def setContentCopyable(self, isCopyable: bool):
        """set whether the content is copyable"""
        if isCopyable:
            self.contentLabel.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
        else:
            self.contentLabel.setTextInteractionFlags(
                Qt.TextInteractionFlag.NoTextInteraction
            )

    def addWidget(
        self,
        widget: QWidget | None,
        stretch: int | None = None,
        alignment: Qt.AlignmentFlag | None = None,
    ) -> None:
        if not self.widgetLayout.children():
            self.widgetLayout.setSpacing(12)
            self.widgetLayout.setContentsMargins(24, 0, 24, 24)

        if stretch is not None and alignment:
            self.widgetLayout.addWidget(widget, stretch, alignment)
        elif stretch:
            self.widgetLayout.addWidget(widget, stretch)
        elif alignment:
            self.widgetLayout.addWidget(widget, alignment=alignment)
        else:
            self.widgetLayout.addWidget(widget)


class Dialog(FramelessDialog, Ui_MessageBox):
    """Dialog box"""

    yesSignal = pyqtSignal()
    cancelSignal = pyqtSignal()

    def __init__(self, title: str, content: str, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._setUpUI(title, content, self)

        self.windowTitleLabel = QLabel(title, self)

        self.setResizeEnabled(False)
        self.resize(240, 192)
        self.titleBar.hide()

        self.vBoxLayout.insertWidget(
            0, self.windowTitleLabel, 0, Qt.AlignmentFlag.AlignTop
        )
        self.windowTitleLabel.setObjectName("windowTitleLabel")
        FluentStyleSheet.DIALOG.apply(self)
        self.setFixedSize(self.size())

    def setTitleBarVisible(self, isVisible: bool):
        self.windowTitleLabel.setVisible(isVisible)


class MessageBoxBase(MaskDialogBase, Ui_MessageBox):
    """Message box base"""

    yesSignal = pyqtSignal()
    cancelSignal = pyqtSignal()

    def __init__(
        self,
        title: str,
        content: str,
        yesButtonText: str | None = None,
        noButtonText: str | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent=parent)
        self._setUpUI(title, content, self.widget)

        self.setShadowEffect(60, (0, 10), QColor(0, 0, 0, 50))
        self.setMaskColor(QColor(0, 0, 0, 76))
        self._hBoxLayout.removeWidget(self.widget)
        self._hBoxLayout.addWidget(self.widget, alignment=Qt.AlignmentFlag.AlignCenter)

        self.buttonGroup.setMinimumWidth(280)
        # self.widget.setFixedSize(
        #     max(self.contentLabel.width(), self.titleLabel.width()) + 48,self.contentLabel.y() + self.contentLabel.height() + 105
        # )

        self.yesButton.setText(yesButtonText) if yesButtonText else None
        self.yesAction = QAction(self)
        self.yesAction.setShortcuts([Qt.Key.Key_Enter, Qt.Key.Key_Return])
        self.addAction(self.yesAction)
        self.yesAction.triggered.connect(lambda checked: self.yesButton.click())

        self.cancelButton.setText(noButtonText) if noButtonText else None
        self.cancelButton.setShortcut(Qt.Key.Key_Cancel)

    def eventFilter(self, obj, event: QEvent):
        if obj is self.window():
            if event.type() == QEvent.Type.Resize:
                self._adjustText()

        return super().eventFilter(obj, event)
