from abc import abstractmethod
from typing import Any, Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QHideEvent
from PyQt6.QtWidgets import QHBoxLayout, QWidget

from ....module.configuration.runners.converters.converter import Converter
from ....module.configuration.tools.template_utils.options import GUIOption
from ....module.configuration.tools.template_utils.template_enums import UIFlags
from ....module.tools.types.config import AnyConfig
from ...common.core_signalbus import core_signalbus
from ..infobar import InfoBar, InfoBarPosition


class BaseSetting(QWidget):
    notify = pyqtSignal(tuple)  # is_disabled, save_value
    notifyParent = pyqtSignal(tuple)  # notify_type, value

    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        option: GUIOption,
        converter: Optional[Converter] = None,
        notify_disabled: bool = True,
        parent_keys: list[str] = [],
        parent: Optional[QWidget] = None,
    ):
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

        option : GUIOption
            The options associated with `config_key`.

        converter : Converter | None, optional
            The value converter used to convert values between config and GUI representation.

        notify_disabled : bool, optional
            Notify the associated Setting Card if this setting is disabled.
            By default True.

        parent_keys : list[str]
            The parents of `key`. Used for lookup in the config.

        parent : QWidget, optional
            Parent of this class.
            By default None.
        """
        super().__init__(parent=parent)
        self.config = config
        self.config_key = config_key
        self.current_value = config.get_value(key=config_key, parents=parent_keys)
        self.default_value = option.default
        self.backup_value = None
        self.converter = converter
        self.is_disabled = False
        self.notify_disabled = notify_disabled
        self.parent_keys = parent_keys

        # The value which disables this setting.
        self.disable_self_value = (
            option.ui_disable_self if option.defined(option.ui_disable_self) else None
        )
        # The value which disables children of this setting
        self.disable_other_value = (
            option.ui_disable_other if option.defined(option.ui_disable_other) else None
        )

        # Notify user that the application must be reloaded for the setting to apply.
        self.reload_required = (
            option.defined(option.ui_flags)
            and UIFlags.REQUIRES_RELOAD in option.ui_flags
        )

        self.buttonlayout = QHBoxLayout(self)
        self.buttonlayout.setContentsMargins(0, 0, 0, 0)
        self.__connectSignalToSlot()

    def hideEvent(self, e: QHideEvent | None):
        super().hideEvent(e)
        self.config.save_config()

    def __connectSignalToSlot(self):
        self.notify.connect(self._onParentNotification)
        core_signalbus.updateConfigSettings.connect(self._onUpdateConfigSettings)
        core_signalbus.configUpdated.connect(self._onConfigUpdated)

    def _validateKey(self, name: str, key: str, parent_keys: list[str]) -> bool:
        if self.config.name == name and self.config_key == key:
            if self.parent_keys == parent_keys:
                return True
            else:
                try:
                    self.config.get_value(self.config_key, parent_keys, errors="raise")
                    return True
                except Exception:
                    return False

    def _convert_value(self, value, to_gui: bool = False) -> Any:
        if self.converter:
            return self.converter.convert(value, to_gui)
        return value

    def _onConfigUpdated(
        self,
        names: tuple[str, str],
        key: str,
        value_tuple: tuple[Any,],
        parent_keys: list[str],
    ):
        if self._validateKey(names[0], key, parent_keys):
            self.setWidgetValue(value_tuple[0])

    def _onUpdateConfigSettings(
        self,
        name: str,
        key: str,
        value_tuple: tuple[Any,],
        parent_keys: list[str],
    ):
        if self._validateKey(name, key, parent_keys):
            self.setConfigValue(value_tuple[0])

    def _onParentNotification(self, values: tuple):
        type, value = values
        if type == "disable":
            self.notify_disabled = False
            self._setDisableWidget(value[0], value[1])
            self.notify_disabled = True
        elif type == "updateState":
            self.updateDisabledStatus()

    def _onReloadRequired(self):
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

    @abstractmethod
    def _setWidgetValue(self, value: Any): ...

    def _setDisableWidget(self, is_disabled: bool, save: bool):
        if self.is_disabled != is_disabled:
            self.is_disabled = is_disabled
            self.setting.setDisabled(self.is_disabled)

            if self.is_disabled:
                self.backup_value = self.current_value
                value = self.disable_self_value
            else:
                value = self.backup_value

            if self._canGetDisabled() and save:
                self.setConfigValue(value)

    def _canGetDisabled(self) -> bool:
        return self.disable_self_value is not None

    def _canDisableOther(self) -> bool:
        return self.disable_other_value is not None

    def updateDisabledStatus(self):
        self.maybeDisableParent(self.current_value, save=False)

    def maybeDisableParent(self, value: Any, save: bool = True):
        if self.notify_disabled:
            if self._canGetDisabled():
                self.notifyParent.emit(
                    ("disable", (self.disable_self_value == value, save))
                )
            elif self._canDisableOther():
                self.notifyParent.emit(
                    ("disable_other", (self.disable_other_value == value, save))
                )

    def setConfigValue(self, value: Any) -> bool:
        if self.current_value != value or self.backup_value == value:
            error = self.config.set_value(
                key=self.config_key,
                value=self._convert_value(value),
                parents=self.parent_keys,
            )
            success = not error
        else:
            success = True  # The value is already present in the config

        if success:
            self.current_value = value
            self.setWidgetValue(value)
            self.maybeDisableParent(value)
            if self.reload_required:
                self._onReloadRequired()
        return success

    def resetValue(self):
        self.setConfigValue(self.default_value)

    def setWidgetValue(self, value: Any):
        self._setWidgetValue(self._convert_value(value, to_gui=True))
