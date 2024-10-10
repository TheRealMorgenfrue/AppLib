from abc import abstractmethod
from typing import Any, Optional
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtGui import QHideEvent
from PyQt6.QtCore import pyqtSignal


from applib.app.common.core_signalbus import core_signalbus

from app.components.infobar_test import InfoBar, InfoBarPosition
from module.config.templates.template_enums import UIFlags
from module.tools.types.config import AnyConfig


class BaseSetting(QWidget):
    notify = pyqtSignal(tuple)  # isDisabled, saveValue
    notifyParent = pyqtSignal(tuple)  # notifyType, value

    def __init__(
        self,
        config: AnyConfig,
        configkey: str,
        configname: str,
        options: dict,
        currentValue: Any,
        defaultValue: Any,
        backupValue: Any = None,
        isDisabled: bool = False,
        notifyDisabled: bool = True,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.config = config
        self.configkey = configkey
        self.configname = configname
        self.options = options
        self.currentValue = currentValue
        self.defaultValue = defaultValue
        self.disableSelfValue = (
            options["ui_disable_self"] if "ui_disable_self" in options else None
        )  # The value which disables this setting.
        self.disableOtherValue = (
            options["ui_disable_other"] if "ui_disable_other" in options else None
        )  # The value which disables children of this setting
        self.backupValue = backupValue
        self.isDisabled = isDisabled
        self.notifyDisabled = notifyDisabled
        self.reload_required = (
            "ui_flags" in options and UIFlags.REQUIRES_RELOAD in options["ui_flags"]
        )

        self.buttonlayout = QHBoxLayout(self)
        self.buttonlayout.setContentsMargins(0, 0, 0, 0)

        self.setting = False

        self.__connectSignalToSlot()
        core_signalbus.configUpdated.emit(
            self.configname, self.configkey, (self.currentValue,)
        )

    def hideEvent(self, e: QHideEvent | None) -> None:
        super().hideEvent(e)
        self.config.saveConfig()

    def __connectSignalToSlot(self) -> None:
        self.notify.connect(self.__onParentNotification)
        core_signalbus.updateConfigSettings.connect(self.__onUpdateConfigSettings)
        core_signalbus.configNameUpdated.connect(self.__onConfigNameUpdated)
        core_signalbus.configUpdated.connect(self.__onConfigUpdated)

    def __onConfigUpdated(
        self, config_name: str, configkey: str, value: tuple[Any,]
    ) -> None:
        if (
            self.setting
            and config_name == self.configname
            and configkey == self.configkey
        ):
            self.setWidgetValue(value[0])

    def __onUpdateConfigSettings(self, configkey: str, value: tuple[Any,]) -> None:
        if self.setting and self.configkey == configkey:
            self.setValue(value[0])

    def __onConfigNameUpdated(self, old_name: str, new_name: str) -> None:
        if old_name == self.configname:
            self.configname = new_name

    def __onParentNotification(self, values: tuple) -> None:
        type, value = values
        if type == "disable":
            self.notifyDisabled = False
            self._setDisableWidget(value[0], value[1])
            self.notifyDisabled = True
        elif type == "updateState":
            self.updateDisabledStatus()

    def __onReloadRequired(self) -> None:
        title = "Change requires reload to take effect"
        content = ""
        InfoBar.info(
            title=title,
            content=content,
            duration=5000,
            position=InfoBarPosition.TOP,
            parent=self._getDisplayParent(),
        )

    def _getDisplayParent(self) -> QWidget:
        parent = self.parentWidget()
        prevParent = None
        while parent:
            prevParent = parent
            parent = parent.parentWidget()

        if prevParent:
            # Last ancestor - 1
            return prevParent
        elif parent:
            # Last ancestor
            return parent
        else:
            # No ancestor found
            return self

    def _setDisableWidget(self, isDisabled: bool, save: bool) -> None:
        if self.isDisabled != isDisabled:
            self.isDisabled = isDisabled
            self.setting.setDisabled(self.isDisabled)

            if self.isDisabled:
                self.backupValue = self.currentValue
                value = self.disableSelfValue
            else:
                value = self.backupValue

            if self._canGetDisabled() and save:
                self.setValue(value)

    def _canGetDisabled(self) -> bool:
        return self.disableSelfValue is not None

    def _canDisableOther(self) -> bool:
        return self.disableOtherValue is not None

    def updateDisabledStatus(self) -> None:
        self.maybeDisableParent(self.currentValue, save=False)

    def maybeDisableParent(self, value: Any, save: bool = True) -> None:
        if self.notifyDisabled:
            if self._canGetDisabled():
                self.notifyParent.emit(
                    ("disable", (self.disableSelfValue == value, save))
                )
            elif self._canDisableOther():
                self.notifyParent.emit(
                    ("disable_other", (self.disableOtherValue == value, save))
                )

    def setValue(self, value: Any) -> bool:
        success = None
        # print(
        #     f"key: {self.configkey} | val: {value} | curVal: {self.currentValue} | bakVal: {self.backupValue}"
        # )
        if self.currentValue != value or self.backupValue == value:
            if self.config.setValue(self.configkey, value, self.configname):
                self.currentValue = value
                self.maybeDisableParent(value)
                success = True
            else:
                success = False
        else:
            success = True  # The value is already present in config
        if success and self.reload_required:
            self.__onReloadRequired()
        return success

    def resetValue(self) -> None:
        self.setValue(self.defaultValue)

    @abstractmethod
    def setWidgetValue(self, value: Any) -> None: ...
