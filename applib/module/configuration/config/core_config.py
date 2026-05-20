from typing import Self

from ..internal.core_args import CoreArgs
from ..templates.core_template import CoreTemplate
from ..tools.validation_model_gen import CoreValidationModelGenerator
from .config_base import ConfigBase


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
        if not self._created:
            template = CoreTemplate()
            super().__init__(
                name=CoreArgs._core_main_config_name,
                template=template,
                validation_model=CoreValidationModelGenerator().get_generic_model(
                    model_name=template.name,
                    template=template,
                ),
                file_path=CoreArgs._core_main_config_path,
            )
            self._created = True
