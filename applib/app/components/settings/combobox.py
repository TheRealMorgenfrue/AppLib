from typing import Any, override

from PyQt6.QtWidgets import QWidget
from qfluentwidgets import ComboBox

from ....module.configuration.runners.converters.converter import Converter
from ....module.configuration.tools.template_utils.options import Option
from ....module.tools.types.config import AnyConfig
from .base_setting import BaseSetting


class CoreComboBox(BaseSetting):
    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        option: Option,
        texts: list[str] | dict[str, Any],
        converter: Converter | None = None,
        path="",
        parent: QWidget | None = None,
    ) -> None:
        """
        Combobox widget connected to a config key.

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting.

        config_key : str
            The option key in the config which should be associated with this setting.

        option : Option
            The option associated with `config_key`.

        texts : list[str] | dict[str, Any]
            All possible values this option can have.

        converter : Converter | None, optional
            The value converter used to convert values between config and GUI representation.

        path : str
            The path of `key`. Used for lookup in the config.

        parent : QWidget, optional
            Parent of this setting.
            By default None.
        """
        super().__init__(
            config=config,
            config_key=config_key,
            option=option,
            converter=converter,
            path=path,
            parent=parent,
        )
        try:
            self.setting = ComboBox(self)
            # Populate combobox with values
            if isinstance(texts, dict):
                for k, v in texts.items():
                    self.setting.addItem(k, userData=v)
            else:
                for text, value in zip(texts, texts, strict=False):
                    self.setting.addItem(f"{text}", userData=value)
            self.setWidgetValue(self.current_value)
            self.buttonlayout.addWidget(self.setting)
            self._connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def _connectSignalToSlot(self) -> None:
        self.setting.currentIndexChanged.connect(
            lambda index: self.setConfigValue(self.setting.itemData(index))
        )

    @override
    def _setWidgetValue(self, value: str) -> None:
        self.setting.setCurrentIndex(self.setting.findData(value))
