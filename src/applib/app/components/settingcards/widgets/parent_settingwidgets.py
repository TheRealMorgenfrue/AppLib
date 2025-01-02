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


class AppLibCardWidget(CardWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.vCardLayout = QVBoxLayout(self)

    def addChild(self, child: QWidget) -> None:
        self.vCardLayout.addWidget(child)

    def removeChild(self, child: QWidget) -> None:
        self.vCardLayout.removeWidget(child)


class ParentSettingWidget(ParentCardBase, SettingWidgetBase):
    """Base class for parent setting widgets"""

    def __init__(
        self,
        setting: str,
        title: str,
        content: Optional[str],
        hasDisableButton: bool,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(
            setting=setting,
            title=title,
            content=content,
            hasDisableButton=hasDisableButton,
            parent=parent,
        )
        self.vGeneralLayout = QVBoxLayout(self)
        self._cardWidget = AppLibCardWidget()

        self.settingWidget = SettingWidget(
            setting=setting,
            title=self._title,
            content=self._content,
            hasDisableButton=hasDisableButton,
            parent=self,
        )

        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self) -> None:
        self.vGeneralLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vGeneralLayout.setContentsMargins(0, 0, 0, 0)
        self.vGeneralLayout.addWidget(self._cardWidget)

    def _connectSignalToSlot(self) -> None:
        self.notifyCard.connect(self._onParentNotified)
        self.disableCard.connect(self.setDisableAll)
        self.settingWidget.disableCard.connect(self.disableCard.emit)

    def _onParentNotified(self, values: tuple[str, Any]) -> None:
        type, value = values
        if type == "updateState":
            self.disableChildren.emit(DisableWrapper(self.is_disabled))

    @override
    def getOption(self) -> AnySetting:
        return self.settingWidget.getOption()

    @override
    def addChild(self, child: QWidget) -> None:
        self._cardWidget.addChild(child)


class NestedSettingWidget(ParentSettingWidget):
    def __init__(
        self,
        setting: str,
        title: str,
        content: Optional[str],
        hasDisableButton: bool,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(
            setting=setting,
            title=title,
            content=content,
            hasDisableButton=hasDisableButton,
            parent=parent,
        )
        self.hBoxLayout = QHBoxLayout()

        self._initLayout()

    def _initLayout(self) -> None:
        self.settingWidget.titleLabel.setObjectName("nestedTitleLabel")

        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.hBoxLayout.addWidget(self.settingWidget)
        self.hBoxLayout.addStretch(1)  # Push option widget to the left in the layout
        self.vGeneralLayout.insertLayout(0, self.hBoxLayout)

    @override
    def setDisableAll(self, wrapper: DisableWrapper) -> None:
        is_disabled = wrapper.is_disabled
        if self.is_disabled != is_disabled:
            self.is_disabled = is_disabled
            self._cardWidget.setDisabled(is_disabled)
            self.disableChildren.emit(wrapper)

    @override
    def setOption(
        self,
        option: AnySetting,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
    ) -> None:
        self.settingWidget.setOption(option, alignment)


class ClusteredSettingWidget(ParentSettingWidget):
    def __init__(
        self,
        setting: str,
        title: str,
        content: Optional[str],
        hasDisableButton: bool,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(
            setting=setting,
            title=title,
            content=content,
            hasDisableButton=hasDisableButton,
            parent=parent,
        )

        self._connectSignalToSlot()
        self.addChild(self.settingWidget)

    def _connectSignalToSlot(self) -> None:
        self.notifyCard.connect(self.settingWidget.notifyCard.emit)

    def addChild(self, child: QWidget):
        child.hBoxLayout.setSpacing(20)
        super().addChild(child)

    @override
    def setDisableAll(self, wrapper: DisableWrapper) -> None:
        self.settingWidget.setDisableAll(wrapper)

    @override
    def setOption(
        self,
        option: AnySetting,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignRight,
    ) -> None:
        self.settingWidget.setOption(option, alignment)
