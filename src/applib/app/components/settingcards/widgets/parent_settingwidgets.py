from qfluentwidgets import CardWidget
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt

from typing import Any, Optional, override

from ..card_base import DisableWrapper, ParentCardBase
from .settingwidget import (
    SettingWidget,
    SettingWidgetBase,
)
from .....module.tools.types.gui_settings import AnySetting


class WidgetFrame(CardWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.vCardLayout = QVBoxLayout(self)

    def addChild(self, child: QWidget) -> None:
        self.vCardLayout.addWidget(child, 0, alignment=Qt.AlignmentFlag.AlignTop)

    def removeChild(self, child: QWidget) -> None:
        self.vCardLayout.removeWidget(child)


class ParentSettingWidget(ParentCardBase, SettingWidgetBase):
    """Base class for parent setting widgets"""

    def __init__(
        self,
        card_name: str,
        title: str,
        content: Optional[str],
        has_disable_button: bool,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(
            card_name=card_name,
            title=title,
            content=content,
            has_disable_button=has_disable_button,
            parent=parent,
        )
        self.vGeneralLayout = QVBoxLayout(self)
        self._widgetView = WidgetFrame()
        self.widget = SettingWidget(
            card_name=card_name,
            title=self._title,
            content=self._content,
            has_disable_button=has_disable_button,
        )
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self) -> None:
        self.vGeneralLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vGeneralLayout.setContentsMargins(0, 0, 0, 0)
        self.vGeneralLayout.addWidget(self._widgetView)

    def __connectSignalToSlot(self) -> None:
        self.notifyCard.connect(self._onParentNotified)
        self.disableCard.connect(self.setDisableAll)
        self.widget.disableCard.connect(self.disableCard.emit)

    def _onParentNotified(self, values: tuple[str, Any]) -> None:
        type, value = values
        if type == "updateState":
            self.disableChildren.emit(DisableWrapper(self.is_disabled))

    @override
    def getOption(self) -> AnySetting:
        return self.widget.getOption()

    @override
    def addChild(self, child: QWidget) -> None:
        self._widgetView.addChild(child)


class NestedSettingWidget(ParentSettingWidget):
    def __init__(
        self,
        card_name: str,
        title: str,
        content: Optional[str],
        has_disable_button: bool,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(
            card_name=card_name,
            title=title,
            content=content,
            has_disable_button=has_disable_button,
            parent=parent,
        )
        self.hBoxLayout = QHBoxLayout()
        self.__initLayout()

    def __initLayout(self) -> None:
        self.widget.titleLabel.setObjectName("nestedTitleLabel")
        self.hBoxLayout.addWidget(self.widget)
        self.vGeneralLayout.insertLayout(0, self.hBoxLayout)

    @override
    def setDisableAll(self, wrapper: DisableWrapper) -> None:
        is_disabled = wrapper.is_disabled
        if self.is_disabled != is_disabled:
            self.is_disabled = is_disabled
            self._widgetView.setDisabled(is_disabled)
            self.disableChildren.emit(wrapper)

    @override
    def setOption(
        self,
        option: AnySetting,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
    ) -> None:
        self.widget.setOption(option, alignment)


class ClusteredSettingWidget(ParentSettingWidget):
    def __init__(
        self,
        card_name: str,
        title: str,
        content: Optional[str],
        has_disable_button: bool,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(
            card_name=card_name,
            title=title,
            content=content,
            has_disable_button=has_disable_button,
            parent=parent,
        )
        self.__connectSignalToSlot()
        self.addChild(self.widget)

    def __connectSignalToSlot(self) -> None:
        self.notifyCard.connect(self.widget.notifyCard.emit)

    @override
    def addChild(self, child: QWidget):
        child.hBoxLayout.setSpacing(10)
        super().addChild(child)

    @override
    def setDisableAll(self, wrapper: DisableWrapper) -> None:
        self.widget.setDisableAll(wrapper)

    @override
    def setOption(
        self,
        option: AnySetting,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignRight,
    ) -> None:
        self.widget.setOption(option, alignment)
