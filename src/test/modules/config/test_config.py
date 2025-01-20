from typing import Self

from applib.module.configuration.tools.validation_model_gen import (
    CoreValidationModelGenerator,
)
from applib.module.configuration.config.config_base import ConfigBase
from test.modules.config.templates.process_template import ProcessTemplate
from test.modules.config.test_args import TestArgs
from test.modules.config.templates.test_template import TestTemplate


class TestConfig(ConfigBase):
    _instance = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._created = False
        return cls._instance

    def __init__(self) -> None:
        if not self._created:
            validation_model = CoreValidationModelGenerator().getGenericModel(
                model_name=f"{TestArgs.main_config_name}_val",
                template=self.makeTemplate(),
            )
            super().__init__(
                template_model=validation_model.model_construct().model_dump(),
                validation_model=validation_model,
                config_name=TestArgs.main_config_name,
                config_path=TestArgs.main_config_path,
            )
            self._created = True

    def makeTemplate(self) -> dict:
        return (TestTemplate() | ProcessTemplate()).tree_dump()
