from qfluentwidgets import CheckBox, ToolTipFilter, ToolTipPosition, TextWrap
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtCore import Qt

from typing import Any, Optional, override

from ....common.core_stylesheet import CoreStyleSheet
from ...fluent_label import FluentLabel
from ..card_base import CardBase, DisableWrapper
from .....module.tools.types.gui_settings import AnyBoolSetting, AnySetting


class SettingWidgetBase(CardBase, QWidget):
    def __init__(
        self,
        setting: str,
        title: Optional[str],
        content: Optional[str],
        hasDisableButton: bool,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(cardName=setting, parent=parent)
        self._title = title
        self._content = content
        self.hasDisableButton = hasDisableButton
        self.is_disabled = False

        CoreStyleSheet.SETTING_WIDGET.apply(self)

    def _createToolTip(
        self,
        widget: QWidget | None,
        content: str | None,
        duration: int = 10000,
        showDelay: int = 300,
        position: ToolTipPosition = ToolTipPosition.TOP,
    ) -> None:
        if content and widget:
            widget.setToolTip(TextWrap.wrap(content, 70, False)[0])
            widget.setToolTipDuration(duration)
            widget.installEventFilter(
                ToolTipFilter(parent=widget, showDelay=showDelay, position=position)
            )


class SettingWidget(SettingWidgetBase):
    def __init__(
        self,
        setting: str,
        title: str,
        content: Optional[str],
        hasDisableButton: bool,
        parent: Optional[QWidget] = None,
    ) -> None:
        try:
            super().__init__(
                setting=setting,
                title=title,
                content=content,
                hasDisableButton=hasDisableButton,
                parent=parent,
            )
            self.hBoxLayout = QHBoxLayout(self)
            self.titleLabel = FluentLabel(self._title)
            self.titleLabel.setWordWrap(True)
            self.option = None  # type: AnySetting | None
            self.disableButton = None  # type: CheckBox | None

            self._initLayout()
            self._connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def _initLayout(self) -> None:
        self.hBoxLayout.addWidget(self.titleLabel)

    def _connectSignalToSlot(self) -> None:
        self.disableCard.connect(self.setDisableAll)

    def _onParentNotified(self, values: tuple[str, Any]) -> None:
        type, value = values
        if type == "disable":
            self.disableCard.emit(DisableWrapper(value[0], save=value[1]))
        elif type == "disable_other":
            self.disableCard.emit(DisableWrapper(value[0], othersOnly=True))
        elif type == "content":
            self._createToolTip(self.titleLabel, value)
            self._createToolTip(self.option, value)
        elif type == "updateState":
            self.disableChildren.emit(DisableWrapper(self.is_disabled))

    def _createDisableButton(self) -> None:
        self.disableButton = CheckBox(self._title)
        self.disableButton.setObjectName("ui_disable")
        self.disableButton.setChecked(not self.is_disabled)
        self.hBoxLayout.insertWidget(
            0, self.disableButton, alignment=Qt.AlignmentFlag.AlignLeft
        )

        self._createToolTip(self.disableButton, self._getDisableMsg(), 5000)
        self.disableButton.stateChanged.connect(
            lambda state: self.disableCard.emit(DisableWrapper(not state))
        )

    def _getDisableMsg(self) -> str:
        return (
            self.tr(f"{self._title} is disabled")
            if self.is_disabled
            else self.tr(f"{self._title} is enabled")
        )

    @override
    def setDisableAll(self, wrapper: DisableWrapper) -> None:
        is_disabled, othersOnly, save = (
            wrapper.is_disabled,
            wrapper.othersOnly,
            wrapper.save,
        )
        if self.is_disabled != is_disabled:
            self.is_disabled = is_disabled
            if self.option and not othersOnly:
                self.option.notify.emit(("disable", (is_disabled, save)))

            if self.disableButton:
                self.disableButton.setChecked(not is_disabled)
                self.disableButton.setToolTip(self._getDisableMsg())

    @override
    def getOption(self) -> AnySetting | None:
        return self.option

    @override
    def setOption(
        self,
        option: AnySetting,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignRight,
    ) -> None:
        # Delete old instances
        if self.option:
            self.hBoxLayout.removeWidget(self.option)
        self.option = option

        # Setup communication between option and card
        self.option.notifyParent.connect(self._onParentNotified)
        self.option.notify.emit(("content", None))

        if self.hasDisableButton:
            # The disable button contains the title as well
            self._createDisableButton()
            self.titleLabel.setHidden(True)

            # The disable button does the same thing as a bool setting
            if isinstance(self.option, AnyBoolSetting):
                self.option.setHidden(True)

        self._createToolTip(self.titleLabel, self._content)
        self._createToolTip(self.option, self._content)

        self.hBoxLayout.addWidget(self.option, alignment=alignment)
        self.option.notify.emit(("updateState", None))
