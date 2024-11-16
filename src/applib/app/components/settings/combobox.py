from __future__ import annotations
from qfluentwidgets import ComboBox
from PyQt6.QtWidgets import QWidget

from typing import Optional, Union, override

from .base_setting import BaseSetting
from ....module.tools.types.config import AnyConfig


class CoreComboBox(BaseSetting):
    def __init__(
        self,
        config: AnyConfig,
        configkey: str,
        configname: str,
        options: dict,
        texts: Union[list[str], dict[str, str]],
        parent: Optional[QWidget] = None,
    ) -> None:
        """Combobox widget connected to a config key.

        Parameters
        ----------
        config : ConfigBase
            Config from which to get values used for this setting.

        configkey : str
            The option key in the config which should be associated with this setting.

        configname : str
            The name of the config.

        options : dict
            The options associated with the `configkey`.

        texts : list | dict
            All possible values this option can have.

        parent : QWidget, optional
            Parent of this class, by default `None`.
        """
        super().__init__(
            config=config,
            configkey=configkey,
            configname=configname,
            options=options,
            currentValue=config.getValue(configkey, configname),
            defaultValue=config.getValue(
                configkey, configname, use_template_config=True
            ),
            backupValue=None,
            isDisabled=False,
            notifyDisabled=True,
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

            self.setting.setCurrentText(self.currentValue)
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
