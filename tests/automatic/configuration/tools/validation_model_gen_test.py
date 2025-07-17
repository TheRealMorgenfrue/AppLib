from applib.module.configuration.tools.validation_model_gen import (
    CoreValidationModelGenerator,
)
from applib.module.tools.types.templates import AnyTemplate
from tests.automatic.configuration.tools.util import AutoTestingTemplate, setup_logger


class TestValidationModelGen:

    def get_template(self) -> AnyTemplate:
        return AutoTestingTemplate()

    def test_model_building(self):
        setup_logger()
        template = self.get_template()
        model = CoreValidationModelGenerator().get_generic_model(
            template.name, template
        )
        model.model_validate(model.model_construct().model_dump())
