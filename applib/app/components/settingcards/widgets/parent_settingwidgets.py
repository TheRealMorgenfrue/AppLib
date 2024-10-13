from qfluentwidgets import CardWidget
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt

from typing import Any, Optional, override

from app.components.settingcards.card_base import DisableWrapper, ParentCardBase
from app.components.settingcards.widgets.settingwidget import (
    SettingWidget,
    SettingWidgetBase,
)
from module.tools.types.gui_settings import AnySetting


class CardWidget_(CardWidget):
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
        self._cardWidget = CardWidget_()

        self.settingWidget = SettingWidget(
            setting=setting,
            title=self._title,
            content=self._content,
            hasDisableButton=hasDisableButton,
            parent=self,
        )

        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self) -> None:
        self.vGeneralLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vGeneralLayout.setContentsMargins(0, 0, 0, 0)
        self.vGeneralLayout.addWidget(self._cardWidget)

    def __connectSignalToSlot(self) -> None:
        self.notifyCard.connect(self.__onParentNotified)
        self.disableCard.connect(self.setDisableAll)
        self.settingWidget.disableCard.connect(self.disableCard.emit)

    def __onParentNotified(self, values: tuple[str, Any]) -> None:
        type, value = values
        if type == "updateState":
            self.disableChildren.emit(DisableWrapper(self.isDisabled))

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

        self.__initLayout()

    def __initLayout(self) -> None:
        self.settingWidget.titleLabel.setObjectName("nestedTitleLabel")

        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.hBoxLayout.addWidget(self.settingWidget)
        self.hBoxLayout.addStretch(1)  # Push option widget to the left in the layout
        self.vGeneralLayout.insertLayout(0, self.hBoxLayout)

    @override
    def setDisableAll(self, wrapper: DisableWrapper) -> None:
        isDisabled = wrapper.isDisabled
        if self.isDisabled != isDisabled:
            self.isDisabled = isDisabled
            self._cardWidget.setDisabled(isDisabled)
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

        self.__connectSignalToSlot()
        self.addChild(self.settingWidget)

    def __connectSignalToSlot(self) -> None:
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