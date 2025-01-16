from abc import abstractmethod
from qfluentwidgets import (
    FluentIconBase,
    isDarkTheme,
    PillPushButton,
    PrimaryPushButton,
    FlowLayout,
)
from qfluentwidgets.components.settings.setting_card import SettingIconWidget
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QIcon, QPainter, QPaintEvent, QResizeEvent
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QFormLayout,
    QLayout,
)
from typing import Any, Optional, Union, override

from ....common.core_stylesheet import CoreStyleSheet
from ...fluent_label import FluentLabel
from ..card_base import CardBase, DisableWrapper
from .....module.tools.types.gui_settings import AnySetting


class SettingCardBase(CardBase, QFrame):
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
        self.iconLabel = SettingIconWidget(icon)
        self.titleLabel = FluentLabel(title)
        self.contentLabel = FluentLabel(content)
        self.hBoxLayout = QHBoxLayout()
        self.vBoxLayout = QVBoxLayout()

        self.has_disable_button = has_disable_button
        self.hide_option = True
        self.is_disabled = False

        self.__initLayout()
        self._setQss()

    def __initLayout(self) -> None:
        if not self.contentLabel.text():
            self.contentLabel.setHidden(True)

        self.iconLabel.setFixedSize(16, 16)

        margin = 16
        self.hBoxLayout.setContentsMargins(margin, margin, margin, margin)
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.hBoxLayout.addWidget(self.iconLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.hBoxLayout.addSpacing(16)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.vBoxLayout.addWidget(self.contentLabel, 0, Qt.AlignmentFlag.AlignLeft)

        self.hBoxLayout.addSpacing(16)
        self.hBoxLayout.addStretch(1)

    def _setQss(self) -> None:
        self.contentLabel.setObjectName("contentLabel")
        CoreStyleSheet.SETTING_CARD.apply(self)


class SettingCardMixin:
    def __init__(self, is_frameless: bool = False, **kwargs) -> None:
        """
        Setting card mixin class.

        Parameters
        ----------
        is_frameless : bool
            Whether to draw a frame around the card. Defaults to `False`.
        """
        super().__init__(**kwargs)
        self.is_frameless = is_frameless
        self.current_height = 0

        self.buttonLayout = QHBoxLayout()
        self.option = None  # type: AnySetting | None
        self.disableButton = None  # type: PillPushButton | None
        self.resetbutton = None  # type: PrimaryPushButton | None

        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self) -> None:
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout.setSpacing(20)

    def _connectSignalToSlot(self) -> None:
        self.notifyCard.connect(self._onParentNotified)
        self.disableCard.connect(self.setDisableAll)

    def _onParentNotified(self, values: tuple[str, Any]) -> None:
        type, value = values
        if type == "disable":
            self.disableCard.emit(DisableWrapper(value[0], save=value[1]))
        elif type == "disable_other":
            self.disableCard.emit(DisableWrapper(value[0], others_only=True))
        elif type == "content":
            self.contentLabel.setText(value)
            self.contentLabel.setHidden(not bool(value))
        elif type == "updateState":
            self.disableChildren.emit(DisableWrapper(self.is_disabled))

    def _createDisableButton(self, alignment: Qt.AlignmentFlag) -> None:
        if self.disableButton is None:
            disableButton = PillPushButton(self.tr("Enabled"))
            disableButton.clicked.connect(
                lambda: self.disableCard.emit(DisableWrapper(not self.is_disabled))
            )
            self.buttonLayout.addWidget(disableButton, 0, alignment)
            self.disableButton = disableButton

    def resizeEvent(self, e: QResizeEvent | None) -> None:
        tlbl = self.titleLabel.sizeHint().height()
        clbl = self.contentLabel.sizeHint().height()
        sizes = [tlbl + clbl]

        for i in range(self.buttonLayout.count()):
            item = self.buttonLayout.itemAt(i)
            w = item.widget()
            if w:
                sizes.append(w.sizeHint().height())

        m = self.hBoxLayout.contentsMargins()
        h = max(sizes) + m.top() + m.bottom()

        if self.current_height != h:
            self.current_height = h
            self.resize(self.width(), h)

    def paintEvent(self, e: QPaintEvent) -> None:
        if not self.is_frameless:
            painter = QPainter(self)
            painter.setRenderHints(QPainter.RenderHint.Antialiasing)

            if isDarkTheme():
                painter.setBrush(QColor(255, 255, 255, 13))
                painter.setPen(QColor(0, 0, 0, 50))
            else:
                painter.setBrush(QColor(255, 255, 255, 170))
                painter.setPen(QColor(0, 0, 0, 19))

            painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 6, 6)

    @override
    def setDisableAll(self, wrapper: DisableWrapper) -> None:
        is_disabled, others_only, save = (
            wrapper.is_disabled,
            wrapper.others_only,
            wrapper.save,
        )
        if self.is_disabled != is_disabled:
            self.is_disabled = is_disabled
            self.disableChildren.emit(wrapper)
            if self.option and not others_only:
                self.option.notify.emit(("disable", (is_disabled, save)))
                if self.has_disable_button and self.hide_option:
                    self.option.setHidden(is_disabled)

            if self.disableButton:
                self.disableButton.setChecked(is_disabled)
                self.disableButton.setText(
                    self.tr("Disabled") if is_disabled else self.tr("Enabled")
                )

            if self.resetbutton:
                self.resetbutton.setDisabled(self.is_disabled)

    @override
    def getOption(self) -> AnySetting:
        return self.option

    @override
    def setOption(
        self,
        option: AnySetting,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignRight,
    ) -> None:
        # Delete old instances
        if self.option:
            self.option.deleteLater()
        if self.resetbutton:
            self.resetbutton.deleteLater()
        self.option = option
        self.buttonLayout.addWidget(self.option, 0, alignment)

        # Disable button
        if self.has_disable_button:
            self._createDisableButton(alignment)

        # Reset button
        self.resetbutton = PrimaryPushButton(self.tr("Reset"))
        self.resetbutton.clicked.connect(self.option.resetValue)
        self.buttonLayout.addWidget(self.resetbutton, 0, alignment)

        # Setup communication between option and card
        self.option.notifyParent.connect(self._onParentNotified)
        self.option.notify.emit(("content", None))
        self.option.notify.emit(("updateState", None))

        self.addToLayout(self.buttonLayout)

    @abstractmethod
    def addToLayout(self, layout: QLayout) -> None: ...


class GenericSettingCard(SettingCardMixin, SettingCardBase):
    def __init__(
        self,
        card_name: str,
        icon: Union[str, QIcon, FluentIconBase],
        title: str,
        content: Optional[str],
        has_disable_button: bool,
        is_frameless: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        try:
            super().__init__(
                card_name=card_name,
                icon=icon,
                title=title,
                content=content,
                has_disable_button=has_disable_button,
                is_frameless=is_frameless,
                parent=parent,
            )
            self.title_size_nocontent = 60
            self.content_size = 70
            self.setLayout(self.hBoxLayout)
            self.adjustSize()
        except Exception:
            self.deleteLater()
            raise

    def _onParentNotified(self, values: tuple[str, Any]) -> None:
        super()._onParentNotified(values)
        type, value = values
        if type == "content":
            self.adjustSize()

    @override
    def addToLayout(self, layout: QLayout) -> None:
        self.hBoxLayout.addLayout(layout)

    def adjustSize(self) -> None:
        content = self.contentLabel.text()
        n = content.count("\n")
        self.setFixedHeight(
            self.content_size + 15 * n if content else self.title_size_nocontent
        )


class FluentSettingCard(SettingCardMixin, SettingCardBase):
    def __init__(
        self,
        card_name: str,
        icon: Union[str, QIcon, FluentIconBase],
        title: str,
        content: Optional[str],
        has_disable_button: bool,
        is_frameless: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        try:
            super().__init__(
                card_name=card_name,
                icon=icon,
                title=title,
                content=content,
                has_disable_button=has_disable_button,
                is_frameless=is_frameless,
                parent=parent,
            )
            self.setLayout(self.hBoxLayout)
            self.titleLabel.setWordWrap(True)
            self.contentLabel.setWordWrap(True)
        except Exception:
            self.deleteLater()
            raise

    @override
    def addToLayout(self, layout: QLayout) -> None:
        self.hBoxLayout.addLayout(layout)


class FormSettingCard(SettingCardMixin, SettingCardBase):
    def __init__(
        self,
        card_name: str,
        icon: Union[str, QIcon, FluentIconBase],
        title: str,
        content: Optional[str],
        has_disable_button: bool,
        is_frameless: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        try:
            super().__init__(
                card_name=card_name,
                icon=icon,
                title=title,
                content=content,
                has_disable_button=has_disable_button,
                is_frameless=is_frameless,
                parent=parent,
            )
            self.formLayout = QFormLayout(self)
        except Exception:
            self.deleteLater()
            raise

        self._initLayout()

    def _initLayout(self) -> None:
        self.titleLabel.setWordWrap(True)
        self.contentLabel.setWordWrap(True)

        # Fluent layout
        self.formLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        self.formLayout.setFormAlignment(Qt.AlignmentFlag.AlignRight)
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.formLayout.setLayout(0, QFormLayout.ItemRole.LabelRole, self.hBoxLayout)

    @override
    def addToLayout(self, buttonView: QWidget) -> None:
        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, buttonView)

    def minimumSizeHint(self) -> QSize:
        h_title = max(self.titleLabel.heightForWidth(self.titleLabel.width()), 0)
        h_content = max(self.contentLabel.heightForWidth(self.contentLabel.width()), 0)
        h_form = max(self.formLayout.heightForWidth(self.width()), 0)

        m_vbox = self.vBoxLayout.contentsMargins()
        h_vbox = m_vbox.top() + m_vbox.bottom()
        m_hbox = self.hBoxLayout.contentsMargins()
        h_hbox = m_hbox.top() + m_hbox.bottom()
        m_form = self.formLayout.contentsMargins()
        h_m_form = m_form.top() + m_form.bottom()

        h = max((h_title + h_content), (h_form)) + h_m_form + h_vbox + h_hbox
        # print(f"h: {h} | tit: {h_title} | con: {h_content} | for: {h_form}")
        return QSize(self.width(), h)


class FlowSettingCard(SettingCardMixin, SettingCardBase):
    def __init__(
        self,
        card_name: str,
        icon: Union[str, QIcon, FluentIconBase],
        title: str,
        content: Optional[str],
        has_disable_button: bool,
        is_frameless: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        try:
            super().__init__(
                card_name=card_name,
                icon=icon,
                title=title,
                content=content,
                has_disable_button=has_disable_button,
                is_frameless=is_frameless,
                parent=parent,
            )
            self.flowLayout = FlowLayout(self)
        except Exception:
            self.deleteLater()
            raise

        self._initLayout()

    def _initLayout(self) -> None:
        self.titleLabel.setWordWrap(True)
        self.contentLabel.setWordWrap(True)

        # Fluent layout
        self.flowLayout.setContentsMargins(0, 0, 0, 0)
        self.flowLayout.setVerticalSpacing(0)
        self.flowLayout.setHorizontalSpacing(0)
        self.flowLayout.addChildLayout(self.hBoxLayout)
        self.flowLayout.addItem(self.hBoxLayout)

    @override
    def addToLayout(self, buttonView: QWidget) -> None:
        self.flowLayout.addWidget(buttonView)

    def minimumSizeHint(self) -> QSize:
        h_title = self.titleLabel.heightForWidth(self.titleLabel.width())
        h_content = self.contentLabel.heightForWidth(self.contentLabel.width())
        h_flow = self.flowLayout.heightForWidth(self.width())
        # h_widget = self._currentWidget.size().height()

        m_vbox = self.vBoxLayout.contentsMargins()
        h_vbox = m_vbox.top() + m_vbox.bottom()
        m_hbox = self.hBoxLayout.contentsMargins()
        h_hbox = m_hbox.top() + m_hbox.bottom()
        m_form = self.flowLayout.contentsMargins()
        h_m_form = m_form.top() + m_form.bottom()

        h = max((h_title + h_content + h_vbox), (h_flow + h_hbox)) + h_m_form
        # print(f"h: {h} | tit: {h_title} | con: {h_content} | flo: {h_flow}")
        return QSize(self.width(), h)
