from typing import Self

from modules.config.templates.process_template import ProcessTemplate
from modules.config.templates.test_template import TestTemplate
from modules.config.test_args import TestArgs

from applib.module.configuration.config.config_base import ConfigBase
from applib.module.configuration.tools.validation_model_gen import (
    CoreValidationModelGenerator,
)


class TestConfig(ConfigBase):
    _instance = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._created = False
        return cls._instance

    def __init__(self) -> None:
        if not self._created:
            template = TestTemplate() | ProcessTemplate()
            template.name = TestArgs.main_config_name
            validation_model = CoreValidationModelGenerator().get_generic_model(
                model_name=TestArgs.main_config_name,
                template=template,
            )
            super().__init__(
                name=TestArgs.main_config_name,
                template=template,
                validation_model=validation_model,
                file_path=TestArgs.main_config_path,
            )
            self._created = True
