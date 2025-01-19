from typing import Self

from applib.module.configuration.templates.core_template import CoreTemplate

from ..internal.core_args import CoreArgs
from .config_base import ConfigBase
from ..tools.validation_model_gen import CoreValidationModelGenerator


class CoreConfig(ConfigBase):
    _instance = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._created = False
        return cls._instance

    def __init__(
        self,
    ) -> None:
        """
        The default class for creating configs from templates and loading the created config from disk.
        The config is validation using the generic validation model.

        NOTE: To create your own custom config class, please inherit from `ConfigBase`.
        """
        template = CoreTemplate()
        if not self._created:
            validation_model = CoreValidationModelGenerator().getGenericModel(
                model_name=template.getName(),
                template=template.getTemplate(),
            )
            super().__init__(
                template=validation_model.model_construct().model_dump(),
                validation_model=validation_model,
                name=CoreArgs._core_main_config_name,
                file_path=CoreArgs._core_main_config_path,
            )
            self._created = True
