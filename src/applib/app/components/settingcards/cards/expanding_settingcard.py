from qfluentwidgets import (
    FluentIconBase,
    FluentStyleSheet,
    isDarkTheme,
)
from qfluentwidgets.components.settings.expand_setting_card import (
    ExpandButton,
    ExpandBorderWidget,
    SpaceWidget,
)
from PyQt6.QtGui import (
    QIcon,
    QPainter,
    QColor,
    QPainterPath,
    QPaintEvent,
    QWheelEvent,
    QResizeEvent,
)
from PyQt6.QtWidgets import (
    QWidget,
    QLayout,
    QScrollArea,
    QFrame,
    QVBoxLayout,
    QApplication,
)
from PyQt6.QtCore import (
    Qt,
    QObject,
    QPropertyAnimation,
    QEasingCurve,
    QEvent,
    QRectF,
    QSize,
)

from typing import Any, Optional, Union, override

from ..card_base import (
    CardBase,
    DisableWrapper,
    ParentCardBase,
)
from .settingcard import FluentSettingCard
from module.tools.types.gui_settings import AnyBoolSetting, AnySetting


class GroupSeparator(QWidget):
    """Group separator

    Courtesy of qfluentwidgets (with modification)
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        if isDarkTheme():
            painter.setPen(QColor(0, 0, 0, 50))
        else:
            painter.setPen(QColor(0, 0, 0, 19))

        painter.drawLine(0, 1, self.width(), 1)

    def minimumSizeHint(self) -> QSize:
        return QSize(self.width(), 3)

    def sizeHint(self) -> QSize:
        return self.minimumSizeHint()


class HeaderSettingCard(FluentSettingCard):
    """Header setting card

    Courtesy of qfluentwidgets (with modification)
    """

    def __init__(
        self,
        setting: str,
        icon: Union[str, QIcon, FluentIconBase],
        title: str,
        content: Optional[str],
        hasDisableButton: bool,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(
            setting=setting,
            icon=icon,
            title=title,
            content=content,
            hasDisableButton=hasDisableButton,
            parent=parent,
        )
        self.expandButton = ExpandButton(self)

        self.hBoxLayout.addWidget(self.expandButton, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(8)

        self.installEventFilter(self)

    def eventFilter(self, obj: QObject, e: QEvent) -> None:
        if obj is self:
            if e.type() == QEvent.Type.Enter:
                self.expandButton.setHover(True)
            elif e.type() == QEvent.Type.Leave:
                self.expandButton.setHover(False)
            elif (
                e.type() == QEvent.Type.MouseButtonPress
                and e.button() == Qt.MouseButton.LeftButton
            ):
                self.expandButton.setPressed(True)
            elif (
                e.type() == QEvent.Type.MouseButtonRelease
                and e.button() == Qt.MouseButton.LeftButton
            ):
                self.expandButton.setPressed(False)
                self.expandButton.click()

        return super().eventFilter(obj, e)

    def paintEvent(self, e: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        if isDarkTheme():
            painter.setBrush(QColor(255, 255, 255, 13))
        else:
            painter.setBrush(QColor(255, 255, 255, 170))

        p = self.parent()  # type: ExpandSettingCard
        path = QPainterPath()
        path.setFillRule(Qt.FillRule.WindingFill)
        path.addRoundedRect(QRectF(self.rect().adjusted(1, 1, -1, -1)), 6, 6)

        # set the bottom border radius to 0 if parent is expanded
        if p.isExpand:
            path.addRect(1, self.height() - 8, self.width() - 2, 8)

        painter.drawPath(path.simplified())

    def addWidget(self, widget: QWidget) -> None:
        """add widget to tail"""
        N = self.hBoxLayout.count()
        self.hBoxLayout.removeItem(self.hBoxLayout.itemAt(N - 1))
        self.hBoxLayout.addWidget(widget, 0, Qt.AlignmentFlag.AlignRight)
        # self.hBoxLayout.addSpacing(19)
        self.hBoxLayout.addWidget(self.expandButton, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(8)

    @override
    def addToLayout(self, buttonLayout: QLayout) -> None:
        N = self.hBoxLayout.count()
        self.hBoxLayout.insertLayout(N - 2, buttonLayout)
        self.buttonLayout.addSpacing(8)


class ExpandSettingCard(CardBase, QScrollArea):
    """Expandable setting card

    Courtesy of qfluentwidgets (with modification)
    """

    def __init__(
        self,
        setting: str,
        icon: Union[str, QIcon, FluentIconBase],
        title: str,
        content: Optional[str],
        hasDisableButton: bool,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(cardName=setting, parent=parent)
        self.scrollWidget = QFrame(self)
        self.view = QFrame(self.scrollWidget)
        self.card = HeaderSettingCard(
            setting=setting,
            icon=icon,
            title=title,
            content=content,
            hasDisableButton=hasDisableButton,
            parent=self,
        )

        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.viewLayout = QVBoxLayout(self.view)
        self.spaceWidget = SpaceWidget(self.scrollWidget)
        self.borderWidget = ExpandBorderWidget(self)

        self.isDisabled = False
        self.isExpand = False

        # Expand animation
        self.expandAni = QPropertyAnimation(self.verticalScrollBar(), b"value", self)

        self.__initWidget()
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initWidget(self) -> None:
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        sh = self.card.sizeHint().height()
        self.resize(self.width(), sh)
        self.setViewportMargins(0, sh, 0, 0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Initialize expand animation
        self.expandAni.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.expandAni.setDuration(200)

        self.__setQss()
        self.card.installEventFilter(self)

    def __initLayout(self) -> None:
        self.scrollLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollLayout.setSpacing(0)
        self.scrollLayout.addWidget(self.view)
        self.scrollLayout.addWidget(self.spaceWidget)

    def __setQss(self) -> None:
        self.view.setObjectName("view")
        self.scrollWidget.setObjectName("scrollWidget")
        self.setProperty("isExpand", False)
        FluentStyleSheet.EXPAND_SETTING_CARD.apply(self.card)
        FluentStyleSheet.EXPAND_SETTING_CARD.apply(self)

    def __connectSignalToSlot(self) -> None:
        self.expandAni.valueChanged.connect(self._onExpandValueChanged)
        self.card.expandButton.clicked.connect(self.toggleExpand)

    def _onExpandValueChanged(self) -> None:
        vh = self.viewLayout.sizeHint().height()
        h = self.viewportMargins().top()
        self.resize(self.width(), max(h + vh - self.verticalScrollBar().value(), h))
        # self.setFixedHeight(max(h + vh - self.verticalScrollBar().value(), h))

    def _adjustViewSize(self) -> None:
        h = self.viewLayout.sizeHint().height()
        self.spaceWidget.setFixedHeight(h)

        if self.isExpand:
            self.resize(self.width(), self.card.height() + h)

    def wheelEvent(self, e: QWheelEvent) -> None:
        """
        Ensure scrolling is working on this widget
        by passing the wheelEvent to its parent if any
        """
        if self.parentWidget():
            self.parentWidget().wheelEvent(e)

    def resizeEvent(self, e: QResizeEvent) -> None:
        if self.isExpand:
            self._adjustViewSize()
        else:
            ch = self.card.height()
            self.resize(self.width(), ch)
            self.setViewportMargins(0, ch, 0, 0)
        self.card.resize(self.width(), self.card.height())
        self.scrollWidget.resize(self.width(), self.scrollWidget.height())
        # print(f"card: {self.card.size()} | self: {self.size()}")

    # FIXME: The retract animation is instant
    def setExpand(self, isExpand: bool) -> None:
        """set the expand status of card"""
        if self.isExpand == isExpand:
            return

        # update style sheet
        self.isExpand = isExpand
        self.setProperty("isExpand", isExpand)
        self.setStyle(QApplication.style())

        # start expand animation
        if isExpand:
            h = self.viewLayout.sizeHint().height()
            self.verticalScrollBar().setValue(h)
            self.expandAni.setStartValue(h)
            self.expandAni.setEndValue(0)
        else:
            self.expandAni.setStartValue(0)
            self.expandAni.setEndValue(self.verticalScrollBar().maximum())

        self.expandAni.start()
        self.card.expandButton.setExpand(isExpand)

    def toggleExpand(self) -> None:
        """toggle expand status"""
        self.setExpand(not self.isExpand)

    def addWidget(self, widget: QWidget) -> None:
        """add widget to tail"""
        self.card.addWidget(widget)


class ExpandGroupSettingCard(ExpandSettingCard):
    """Expand group setting card

    Courtesy of qfluentwidgets
    """

    def addGroupWidget(self, widget: QWidget) -> None:
        # Add separator
        if self.viewLayout.count() >= 1:
            self.viewLayout.addWidget(GroupSeparator(self.view))

        widget.setParent(self.view)
        self.viewLayout.addWidget(widget)
        self._adjustViewSize()


class ExpandingSettingCard(ParentCardBase, ExpandGroupSettingCard):
    def __init__(
        self,
        setting: str,
        icon: Union[str, QIcon, FluentIconBase],
        title: str,
        content: Optional[str],
        hasDisableButton: bool,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Expanding Setting card which holds child cards

        Parameters
        ----------
        setting : str
            The name used for this card in the template

        icon : Union[str, QIcon, FluentIconBase]
            Display icon

        title : str
            Title of this card

        content : str, optional
            Extra text. Sort of a description. Defaults to None.

        hasDisableButton : bool
            Create a disable button for this card.

        parent : QWidget, optional
            The parent of this card. Defaults to None.
        """
        try:
            super().__init__(
                setting=setting,
                icon=icon,
                title=title,
                content=content,
                hasDisableButton=hasDisableButton,
                parent=parent,
            )
            self.__connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def __connectSignalToSlot(self) -> None:
        self.notifyCard.connect(self.__onParentNotified)
        self.disableCard.connect(self.setDisableAll)
        self.card.disableCard.connect(self.disableCard.emit)

    def __onParentNotified(self, values: tuple[str, Any]) -> None:
        # Parent does not have an option directly attached and only needs "updateState"
        type, value = values
        if type == "updateState":
            self.disableChildren.emit(DisableWrapper(self.isDisabled))

    @override
    def addChild(self, child: QWidget) -> None:
        self.addGroupWidget(child)

    @override
    def getOption(self) -> AnySetting:
        return self.card.getOption()

    @override
    def setDisableAll(self, wrapper: DisableWrapper) -> None:
        isDisabled = wrapper.isDisabled
        if self.isDisabled != isDisabled:
            self.isDisabled = isDisabled
            self.disableChildren.emit(wrapper)

    @override
    def setOption(
        self,
        option: AnySetting,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignRight,
    ) -> None:
        if isinstance(option, AnyBoolSetting):
            # Take manual control of disable button
            self.card.hasDisableButton = True
            self.card.hideOption = False
            option.setHidden(True)

        self.card.setOption(option, alignment)
