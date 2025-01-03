from qfluentwidgets import ComboBox
from PyQt6.QtWidgets import QWidget

from typing import Optional, Union, override

from .base_setting import BaseSetting

from ....module.tools.types.config import AnyConfig


class CoreComboBox(BaseSetting):
    def __init__(
        self,
        config: AnyConfig,
        config_key: str,
        options: dict,
        texts: Union[list[str], dict[str, str]],
        parent_key: Optional[str] = None,
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

        options : dict
            The options associated with `config_key`.

        texts : list | dict
            All possible values this option can have.

        parent_key : str, optional
            Search for `config_key` within the scope of a parent key.

        parent : QWidget, optional
            Parent of this class
            By default `None`.
        """
        super().__init__(
            config=config,
            config_key=config_key,
            options=options,
            current_value=config.getValue(key=config_key, parent_key=parent_key),
            default_value=config.getValue(
                key=config_key, parent_key=parent_key, use_template_model=True
            ),
            parent_key=parent_key,
            parent=parent,
        )
        try:
            self.setting = ComboBox(self)

            # Populate combobox with values
            if isinstance(texts, dict):
                for k, v in texts.items():
                    self.setting.addItem(k, userData=v)
            else:
                for text, option in zip(texts, texts):
                    self.setting.addItem(text, userData=option)

            self.setting.setCurrentText(self.current_value)
            self.buttonlayout.addWidget(self.setting)
            self._connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def _connectSignalToSlot(self) -> None:
        self.setting.currentIndexChanged.connect(
            lambda index: self.setValue(self.setting.itemData(index))
        )

    def setValue(self, value: str) -> None:
        if super().setValue(value):
            self.setWidgetValue(value)

    @override
    def setWidgetValue(self, value: str) -> None:
        self.setting.setCurrentIndex(self.setting.findData(value))
