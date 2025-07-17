from typing import override

from PyQt6.QtWidgets import QWidget
from qfluentwidgets import ComboBox

from ....module.configuration.runners.converters.converter import Converter
from ....module.configuration.tools.template_utils.options import GUIOption
from ....module.tools.types.config import AnyConfig
from .base_setting import BaseSetting


class CoreComboBox(BaseSetting):
    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        option: GUIOption,
        texts: list[str] | dict[str, str],
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

        option : GUIOption
            The options associated with `config_key`.

        texts : list | dict
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
                for text, value in zip(texts, texts):
                    self.setting.addItem(text, userData=value)
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
