from qfluentwidgets import (
    IconWidget,
    FlowLayout,
    CardWidget,
    TeachingTip,
    TeachingTipTailPosition,
)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect

from ..common.core_stylesheet import CoreStyleSheet
from .infobar_test import InfoBarIcon


class SampleCard(CardWidget):
    def __init__(self, icon, title, action, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.action = action

        self.iconWidget = IconWidget(icon, self)
        self.iconOpacityEffect = QGraphicsOpacityEffect(self)
        self.iconOpacityEffect.setOpacity(1)  # Set the initial semi-transparency
        self.iconWidget.setGraphicsEffect(self.iconOpacityEffect)

        self.titleLabel = QLabel(title, self)
        self.titleLabel.setStyleSheet("font-size: 16px; font-weight: 500;")
        self.titleOpacityEffect = QGraphicsOpacityEffect(self)
        self.titleOpacityEffect.setOpacity(1)  # Set the initial semi-transparency
        self.titleLabel.setGraphicsEffect(self.titleOpacityEffect)
        # self.contentLabel = QLabel(TextWrap.wrap(content, 45, False)[0], self)

        self.hBoxLayout = QVBoxLayout(self)
        self.vbox_layout = QVBoxLayout()

        self.setFixedSize(130, 160)
        self.iconWidget.setFixedSize(110, 110)

        # self.hBoxLayout.setSpacing(28)
        # self.hBoxLayout.setContentsMargins(20, 0, 0, 0)
        self.vbox_layout.setSpacing(2)
        # self.vbox_layout.setContentsMargins(0, 0, 0, 0)
        self.vbox_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.hBoxLayout.addWidget(
            self.iconWidget, alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.hBoxLayout.addLayout(self.vbox_layout)
        self.vbox_layout.addStretch(1)
        self.vbox_layout.addWidget(
            self.titleLabel, alignment=Qt.AlignmentFlag.AlignCenter
        )
        # self.vbox_layout.addWidget(self.contentLabel)
        self.vbox_layout.addStretch(1)

        self.titleLabel.setObjectName("titleLabel")
        # self.contentLabel.setObjectName('contentLabel')

    def showBottomTeachingTip(self):
        TeachingTip.create(
            target=self.iconWidget,
            icon=InfoBarIcon.SUCCESS,
            title="Startup successful",
            content="",
            isClosable=False,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self,
        )

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.showBottomTeachingTip()
        # start_task(self.action)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.iconOpacityEffect.setOpacity(0.75)
        self.titleOpacityEffect.setOpacity(0.75)
        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )  # Set the mouse pointer to hand shape

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.iconOpacityEffect.setOpacity(1)
        self.titleOpacityEffect.setOpacity(1)
        self.setCursor(
            Qt.CursorShape.ArrowCursor
        )  # Restore the default shape of the mouse pointer


class SampleCardView1(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        self.titleLabel = QLabel(title, self)
        self.vbox_layout = QVBoxLayout(self)
        self.flowLayout = FlowLayout()

        self.vbox_layout.setContentsMargins(20, 0, 20, 0)
        self.vbox_layout.setSpacing(10)
        self.flowLayout.setContentsMargins(0, 0, 0, 0)
        self.flowLayout.setHorizontalSpacing(12)
        self.flowLayout.setVerticalSpacing(12)

        self.vbox_layout.addWidget(self.titleLabel)
        self.vbox_layout.addLayout(self.flowLayout, 1)

        self.titleLabel.setObjectName("viewTitleLabel")
        CoreStyleSheet.SAMPLE_CARD.apply(self)

    def addSampleCard(self, icon, title, action):
        card = SampleCard(icon, title, action, self)
        self.flowLayout.addWidget(card)
