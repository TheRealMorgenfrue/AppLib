from typing import Optional, Union, override

from PyQt6.QtWidgets import QWidget
from qfluentwidgets import ComboBox

from ....module.configuration.tools.template_options.options import GUIOption
from ....module.tools.types.config import AnyConfig
from .base_setting import BaseSetting


class CoreComboBox(BaseSetting):
    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        option: GUIOption,
        texts: Union[list[str], dict[str, str]],
        parent_keys: list[str] = [],
        parent: Optional[QWidget] = None,
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

        parent_keys : list[str]
            The parents of `key`. Used for lookup in the config.

        parent : QWidget, optional
            Parent of this class
            By default None.
        """
        super().__init__(
            config=config,
            config_key=config_key,
            option=option,
            current_value=config.get_value(key=config_key, parents=parent_keys),
            default_value=config.template.get_value(
                key=config_key, parents=parent_keys
            ).default,
            parent_keys=parent_keys,
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
            self.setting.setCurrentText(self.current_value)
            self.buttonlayout.addWidget(self.setting)
            self._connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def _connectSignalToSlot(self) -> None:
        self.setting.currentIndexChanged.connect(
            lambda index: self.set_config_value(self.setting.itemData(index))
        )

    def set_config_value(self, value: str) -> None:
        if super().set_config_value(value):
            self.setWidgetValue(value)

    @override
    def setWidgetValue(self, value: str) -> None:
        self.setting.setCurrentIndex(self.setting.findData(value))
