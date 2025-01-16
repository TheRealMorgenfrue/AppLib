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
from .....module.tools.types.gui_settings import AnyBoolSetting, AnySetting


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
        card_name: str,
        icon: Union[str, QIcon, FluentIconBase],
        title: str,
        content: Optional[str],
        has_disable_button: bool,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(
            card_name=card_name,
            icon=icon,
            title=title,
            content=content,
            has_disable_button=has_disable_button,
            parent=parent,
        )
        self.expandButton = ExpandButton(self)
        self.hBoxLayout.addWidget(self.expandButton, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(8)

        self.installEventFilter(self)
        self.titleLabel.installEventFilter(self)
        self.contentLabel.installEventFilter(self)

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
        elif (
            obj in [self.titleLabel, self.contentLabel]
            and e.type() == QEvent.Type.Resize
        ):
            self.resizeEvent(e)
            if self.parentWidget():
                self.parentWidget().resizeEvent(e)
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

        # Set the bottom border radius to 0 if parent is expanded
        if p.is_expand:
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
    def addToLayout(self, layout: QLayout) -> None:
        N = self.hBoxLayout.count()
        self.hBoxLayout.insertLayout(N - 2, layout)
        # self.buttonLayout.addSpacing(8)


class ExpandSettingCard(CardBase, QScrollArea):
    """Expandable setting card

    Courtesy of qfluentwidgets (with modification)
    """

    def __init__(
        self,
        card_name: str,
        icon: Union[str, QIcon, FluentIconBase],
        title: str,
        content: Optional[str],
        has_disable_button: bool,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(card_name=card_name, parent=parent)
        self.scrollWidget = QFrame(self)
        self._view = QFrame(self.scrollWidget)
        self.card = HeaderSettingCard(
            card_name=card_name,
            icon=icon,
            title=title,
            content=content,
            has_disable_button=has_disable_button,
            parent=self,
        )
        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.viewLayout = QVBoxLayout(self._view)
        self.spaceWidget = SpaceWidget(self.scrollWidget)
        self.borderWidget = ExpandBorderWidget(self)
        self.is_disabled = False
        self.is_expand = False
        self.resize_allowed = True
        self.expandAni = QPropertyAnimation(
            self.verticalScrollBar(), b"value", self
        )  # Expand animation

        self.__initWidget()
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initWidget(self) -> None:
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Initialize expand animation
        self.expandAni.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.expandAni.setDuration(200)

        self.__setQss()

    def __initLayout(self) -> None:
        self.scrollLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollLayout.setSpacing(0)
        self.scrollLayout.addWidget(self._view)
        self.scrollLayout.addWidget(self.spaceWidget)

    def __setQss(self) -> None:
        self._view.setObjectName("view")
        self.scrollWidget.setObjectName("scrollWidget")
        self.setProperty("isExpand", False)
        FluentStyleSheet.EXPAND_SETTING_CARD.apply(self.card)
        FluentStyleSheet.EXPAND_SETTING_CARD.apply(self)

    def __connectSignalToSlot(self) -> None:
        self.expandAni.finished.connect(self.__onExpandFinished)
        self.expandAni.valueChanged.connect(self.__onExpandValueChanged)
        self.card.expandButton.clicked.connect(self.toggleExpand)

    def __onExpandValueChanged(self) -> None:
        vh = self.viewLayout.sizeHint().height()
        h = self.viewportMargins().top()
        self.resize(self.width(), max(h + vh - self.verticalScrollBar().value(), h))

    def __onExpandFinished(self) -> None:
        self.resize_allowed = True

    def _adjustViewSize(self) -> None:
        h = self.viewLayout.sizeHint().height()
        self.spaceWidget.setFixedHeight(h)

    def wheelEvent(self, e: QWheelEvent) -> None:
        """
        Ensure scrolling is working on this widget
        by passing the wheelEvent to its parent if any
        """
        if self.parentWidget():
            self.parentWidget().wheelEvent(e)

    def resizeEvent(self, e: QResizeEvent) -> None:
        if not self.resize_allowed:
            return

        ch = self.card.height()
        sw = self.width()
        vlsh = self.viewLayout.sizeHint().height()
        sch = self.scrollWidget.height()
        if self.is_expand:
            self._adjustViewSize()
            self.resize(sw, ch + vlsh)
            self.setViewportMargins(0, ch, 0, 0)
        else:
            self.resize(sw, ch)
            self.setViewportMargins(0, ch, 0, 0)
        self.card.resize(sw, ch)
        self.scrollWidget.resize(sw, sch)

    def setExpand(self, is_expand: bool) -> None:
        """Set the expand status of card"""
        if self.is_expand == is_expand:
            return
        self.resize_allowed = False

        # Update style sheet
        self.is_expand = is_expand
        self.setProperty("isExpand", is_expand)
        self.setStyle(QApplication.style())

        # Start expand animation
        h = self.viewLayout.sizeHint().height()
        if is_expand:
            self.verticalScrollBar().setValue(h)
            self.expandAni.setStartValue(h)
            self.expandAni.setEndValue(0)
        else:
            self.expandAni.setStartValue(0)
            self.expandAni.setEndValue(h)
        self.expandAni.start()

    def toggleExpand(self) -> None:
        """Toggle expand status"""
        self.setExpand(not self.is_expand)

    def addWidget(self, widget: QWidget) -> None:
        """Add widget to tail"""
        self.card.addWidget(widget)


class ExpandGroupSettingCard(ExpandSettingCard):
    """Expand group setting card

    Courtesy of qfluentwidgets (with modification)
    """

    def addGroupWidget(self, widget: QWidget) -> None:
        # Add separator
        if self.viewLayout.count() >= 1:
            self.viewLayout.addWidget(GroupSeparator(self._view))

        widget.setParent(self._view)
        self.viewLayout.addWidget(widget)
        self._adjustViewSize()


class ExpandingSettingCard(ParentCardBase, ExpandGroupSettingCard):
    def __init__(
        self,
        card_name: str,
        icon: Union[str, QIcon, FluentIconBase],
        title: str,
        content: Optional[str],
        has_disable_button: bool,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Expanding setting card which holds child cards.

        Parameters
        ----------
        card_name : str
            The name of the template key which this card represents.

        icon : Union[str, QIcon, FluentIconBase]
            Display icon.

        title : str
            Card title.

        content : str, optional
            Card description. By default `None`.

        has_disable_button : bool
            Create a disable button for this card.

        parent : QWidget, optional
            The parent of this card. Defaults to `None`.
        """
        try:
            super().__init__(
                card_name=card_name,
                icon=icon,
                title=title,
                content=content,
                has_disable_button=has_disable_button,
                parent=parent,
            )
            self.__connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def __connectSignalToSlot(self) -> None:
        self.notifyCard.connect(self._onParentNotified)
        self.disableCard.connect(self.setDisableAll)
        self.card.disableCard.connect(self.disableCard.emit)

    def _onParentNotified(self, values: tuple[str, Any]) -> None:
        # Parent does not have an option directly attached and only needs "updateState"
        type, value = values
        if type == "updateState":
            self.disableChildren.emit(DisableWrapper(self.is_disabled))

    @override
    def addChild(self, child: QWidget) -> None:
        self.addGroupWidget(child)

    @override
    def getOption(self) -> AnySetting:
        return self.card.getOption()

    @override
    def setDisableAll(self, wrapper: DisableWrapper) -> None:
        is_disabled = wrapper.is_disabled
        if self.is_disabled != is_disabled:
            self.is_disabled = is_disabled
            self.disableChildren.emit(wrapper)

    @override
    def setOption(
        self,
        option: AnySetting,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignRight,
    ) -> None:
        if isinstance(option, AnyBoolSetting):
            # Take manual control of disable button
            self.card.has_disable_button = True
            self.card.hide_option = False
            option.setHidden(True)
        self.card.setOption(option, alignment)
