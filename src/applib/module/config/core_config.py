from typing import Self

from .config_base import ConfigBase
from .internal.core_args import CoreArgs
from .tools.validation_model_gen import ValidationModelGenerator
from .templates.core_template import CoreTemplate


class CoreConfig(ConfigBase):
    _instance = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._created = False
        return cls._instance

    def __init__(self) -> None:
        if not self._created:
            validation_model = ValidationModelGenerator().getGenericModel(
                model_name=CoreTemplate().getName(),
                template=CoreTemplate().getTemplate(),
            )
            super().__init__(
                template_config=validation_model.model_construct().model_dump(),
                validation_model=validation_model,
                config_name=CoreArgs.app_config_name,
                config_path=CoreArgs.app_config_path,
            )
            self._setConfig(self._initConfig())
            self._created = True
