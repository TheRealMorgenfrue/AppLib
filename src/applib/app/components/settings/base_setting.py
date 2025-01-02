from abc import abstractmethod
from typing import Any, Optional
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtGui import QHideEvent
from PyQt6.QtCore import pyqtSignal


from ...common.core_signalbus import core_signalbus

from ..infobar_test import InfoBar, InfoBarPosition

from ....module.config.templates.template_enums import UIFlags
from ....module.tools.types.config import AnyConfig


class BaseSetting(QWidget):
    notify = pyqtSignal(tuple)  # is_disabled, save_value
    notifyParent = pyqtSignal(tuple)  # notify_type, value

    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        options: dict,
        current_value: Any,
        default_value: Any,
        notify_disabled: bool = True,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        The base class for all GUI settings.

        Required Attributes
        -------------------
        Child classes must define the following attributes.

        self.setting : QWidget
            The widget defining some setting, e.g., a checkbox.

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting.

        config_key : str
            The option key in the config which should be associated with this setting.

        options : dict
            The options associated with `config_key`.

        current_value : Any
            The current value of the setting.

        default_value : Any
            The default value of the setting.

        notify_disabled : bool, optional
            Notify the associated Setting Card if this setting is disabled.
            By default `True`.

        parent : QWidget, optional
            Parent of this class.
            By default `None`.
        """
        super().__init__(parent=parent)
        self.config = config
        self.config_key = config_key
        self.config_name = config.getConfigName()
        self.current_value = current_value
        self.default_value = default_value
        self.backup_value = None
        self.is_disabled = False
        self.notify_disabled = notify_disabled

        # The value which disables this setting.
        self.disable_self_value = (
            options["ui_disable_self"] if "ui_disable_self" in options else None
        )
        # The value which disables children of this setting
        self.disable_other_value = (
            options["ui_disable_other"] if "ui_disable_other" in options else None
        )

        # Notify user that the application must be reloaded for the setting to apply.
        self.reload_required = (
            "ui_flags" in options and UIFlags.REQUIRES_RELOAD in options["ui_flags"]
        )

        self.buttonlayout = QHBoxLayout(self)
        self.buttonlayout.setContentsMargins(0, 0, 0, 0)
        core_signalbus.configUpdated.emit(
            self.config_name, self.config_key, (self.current_value,)
        )
        # Connect after emitting as we only want to notify others, not self
        self.__connectSignalToSlot()

    def hideEvent(self, e: QHideEvent | None) -> None:
        super().hideEvent(e)
        self.config.saveConfig()

    def __connectSignalToSlot(self) -> None:
        self.notify.connect(self._onParentNotification)
        core_signalbus.updateConfigSettings.connect(self._onUpdateConfigSettings)
        core_signalbus.configNameUpdated.connect(self._onConfigNameUpdated)
        core_signalbus.configUpdated.connect(self._onConfigUpdated)

    def _onConfigUpdated(
        self, config_name: str, config_key: str, value: tuple[Any,]
    ) -> None:
        if (
            self.setting
            and config_name == self.config_name
            and config_key == self.config_key
        ):
            self.setWidgetValue(value[0])

    def _onUpdateConfigSettings(self, config_key: str, value: tuple[Any,]) -> None:
        if self.setting and self.config_key == config_key:
            self.setValue(value[0])

    def _onConfigNameUpdated(self, old_name: str, new_name: str) -> None:
        if old_name == self.config_name:
            self.config_name = new_name

    def _onParentNotification(self, values: tuple) -> None:
        type, value = values
        if type == "disable":
            self.notify_disabled = False
            self._setDisableWidget(value[0], value[1])
            self.notify_disabled = True
        elif type == "updateState":
            self.updateDisabledStatus()

    def _onReloadRequired(self) -> None:
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

    def _setDisableWidget(self, is_disabled: bool, save: bool) -> None:
        if self.is_disabled != is_disabled:
            self.is_disabled = is_disabled
            self.setting.setDisabled(self.is_disabled)

            if self.is_disabled:
                self.backup_value = self.current_value
                value = self.disable_self_value
            else:
                value = self.backup_value

            if self._canGetDisabled() and save:
                self.setValue(value)

    def _canGetDisabled(self) -> bool:
        return self.disable_self_value is not None

    def _canDisableOther(self) -> bool:
        return self.disable_other_value is not None

    def updateDisabledStatus(self) -> None:
        self.maybeDisableParent(self.current_value, save=False)

    def maybeDisableParent(self, value: Any, save: bool = True) -> None:
        if self.notify_disabled:
            if self._canGetDisabled():
                self.notifyParent.emit(
                    ("disable", (self.disable_self_value == value, save))
                )
            elif self._canDisableOther():
                self.notifyParent.emit(
                    ("disable_other", (self.disable_other_value == value, save))
                )

    def setValue(self, value: Any) -> bool:
        success = None
        if self.current_value != value or self.backup_value == value:
            if self.config.setValue(self.config_key, value, self.config_name):
                self.current_value = value
                self.maybeDisableParent(value)
                success = True
            else:
                success = False
        else:
            success = True  # The value is already present in config
        if success and self.reload_required:
            self._onReloadRequired()
        return success

    def resetValue(self) -> None:
        self.setValue(self.default_value)

    @abstractmethod
    def setWidgetValue(self, value: Any) -> None: ...
