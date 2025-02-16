from typing import Any, Optional, override

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import QHBoxLayout, QWidget
from qfluentwidgets import CheckBox

from .....module.tools.types.gui_settings import AnyBoolSetting, AnySetting
from ....common.core_stylesheet import CoreStyleSheet
from ...fluent_label import FluentLabel
from ..card_base import CardBase, DisableWrapper


class SettingWidgetBase(CardBase, QWidget):
    def __init__(
        self,
        card_name: str,
        title: Optional[str],
        content: Optional[str],
        has_disable_button: bool,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(card_name=card_name, parent=parent)
        self._title = title
        self._content = content
        self.has_disable_button = has_disable_button
        self.is_disabled = False
        CoreStyleSheet.SETTING_WIDGET.apply(self)


class SettingWidget(SettingWidgetBase):
    def __init__(
        self,
        card_name: str,
        title: str,
        content: Optional[str],
        has_disable_button: bool,
        parent: Optional[QWidget] = None,
    ) -> None:
        try:
            super().__init__(
                card_name=card_name,
                title=title,
                content=content,
                has_disable_button=has_disable_button,
                parent=parent,
            )
            self.hBoxLayout = QHBoxLayout(self)
            self.titleLabel = FluentLabel(self._title)
            self.titleLabel.setWordWrap(True)
            self.option = None  # type: AnySetting | None
            self.disableButton = None  # type: CheckBox | None

            self.__initLayout()
            self.__connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def __initLayout(self) -> None:
        self.hBoxLayout.addWidget(self.titleLabel)

    def __connectSignalToSlot(self) -> None:
        self.disableCard.connect(self.setDisableAll)

    def __onParentNotified(self, values: tuple[str, Any]) -> None:
        type, value = values
        if type == "disable":
            self.disableCard.emit(DisableWrapper(value[0], save=value[1]))
        elif type == "disable_other":
            self.disableCard.emit(DisableWrapper(value[0], others_only=True))
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

    def resizeEvent(self, e: QResizeEvent | None) -> None:
        self.titleLabel.sizeHint()  # Recalculate size of wordwrapped text

    @override
    def setDisableAll(self, wrapper: DisableWrapper) -> None:
        is_disabled, others_only, save = (
            wrapper.is_disabled,
            wrapper.others_only,
            wrapper.save,
        )
        if self.is_disabled != is_disabled:
            self.is_disabled = is_disabled
            if self.option and not others_only:
                self.option.notify.emit(("disable", (is_disabled, save)))

            if self.disableButton:
                self.disableButton.setChecked(not is_disabled)
                self.disableButton.setToolTip(self._getDisableMsg())

    @override
    def get_option(self) -> AnySetting | None:
        return self.option

    @override
    def set_option(
        self,
        option: AnySetting,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignRight,
    ) -> None:
        # Delete old instances
        if self.option:
            self.hBoxLayout.removeWidget(self.option)
        self.option = option

        # Setup communication between option and card
        self.option.notifyParent.connect(self.__onParentNotified)
        self.option.notify.emit(("content", None))

        # The disable button contains the title as well
        if self.has_disable_button:
            self._createDisableButton()
            self.titleLabel.setHidden(True)

            # Hide bool option as the disable button does the same thing
            if isinstance(self.option, AnyBoolSetting):
                self.option.setHidden(True)

        self._createToolTip(self.titleLabel, self._content)
        self._createToolTip(self.option, self._content)

        self.hBoxLayout.addWidget(self.option, alignment=alignment)
        self.option.notify.emit(("updateState", None))
