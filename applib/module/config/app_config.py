from typing import Self

from module.config.config_base import ConfigBase
from module.config.internal.app_args import AppArgs
from module.config.internal.names import ConfigNames
from module.config.tools.validation_model_gen import ValidationModelGenerator
from module.config.templates.app_template import AppTemplate


class AppConfig(ConfigBase):
    _instance = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._created = False
        return cls._instance

    def __init__(self) -> None:
        if not self._created:
            validation_model = ValidationModelGenerator().getGenericModel(
                model_name=AppTemplate().getName(),
                template=AppTemplate().getTemplate(),
            )
            super().__init__(
                template_config=validation_model.model_construct().model_dump(),
                validation_model=validation_model,
                config_name=ConfigNames.app_config_name,
                config_path=AppArgs.app_config_path,
            )
            self._setConfig(self._initConfig())
            self._created = True
