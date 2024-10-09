from typing import Any, Literal, Self
from pydantic import BaseModel, Field, field_validator, create_model

from module.config.internal.pixivutil_args import PixivUtilArgs
from module.config.templates.pixivutil_template import PixivUtilTemplate
from module.config.tools.template_options.validation_info import ValidationInfo
from module.config.tools.template_parser import TemplateParser


class ValidationModelGenerator:
    _instance = None
    # Cache of all created models. Models of the same type are cached only once
    _model_cache = {"generic": {}, "batch_job": {}}

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def getGenericModel(self, model_name: str, template: dict) -> type[BaseModel]:
        """Generate a generic validation model of the supplied template.\n
        This type of model can be used to validate all templates not requiring special care

        Parameters
        ----------
        model_name : str
            The name of the generated model.

        template : dict
            The template from which the model is generated from.

        Returns
        -------
        type[BaseModel]
            A validation model of the template.
        """
        if model_name not in self._model_cache["generic"]:
            self.templateParser = TemplateParser()
            self.templateParser.parse(model_name, template)
            validation_info = self.templateParser.getValidationInfo(model_name)

            field_validators = self._createFieldValidators(
                validation_info=validation_info
            )
            model = self._generateModel(
                model_name=model_name,
                fields=validation_info.getFields(),
                field_validators=field_validators,
            )
            self._model_cache["generic"] |= {model_name: model}
        return self._model_cache["generic"][model_name]

    def getBatchJobModel(
        self,
        model_name: str,
        job_template: dict[str, Any],
        options_template: PixivUtilTemplate,
    ) -> type[BaseModel]:
        """Generate a batchjob validation model of the supplied templates.

        Parameters
        ----------
        model_name : str
            The name of the generated model.

        job_template : dict[str, Any]
            The template for settings specific to batch jobs.

        options_template : PixivUtilTemplate
            The template class containing settings which overrides the settings
            defined in the global PixivUtil2 Config.

        Returns
        -------
        type[BaseModel]
            A validation model of the templates.
        """
        if model_name not in self._model_cache["batch_job"]:
            # Remove options' section_names from the validation model
            _options_template_ = {"nosection": {}}
            for section_name, settings in options_template.getTemplate().items():
                _options_template_["nosection"] |= settings

            options_template_name = options_template.getName()
            self.templateParser = TemplateParser()
            self.templateParser.parse(model_name, job_template)
            self.templateParser.parse(options_template_name, _options_template_)

            job_validation_info = self.templateParser.getValidationInfo(model_name)
            options_validation_info = self.templateParser.getValidationInfo(
                options_template_name
            )

            job_field_validators = self._createFieldValidators(
                validation_info=job_validation_info
            )
            options_field_validators = self._createFieldValidators(
                validation_info=options_validation_info
            )
            options_model = self._generateModel(
                model_name=options_template_name,
                fields=options_validation_info.getFields(),
                field_validators=options_field_validators,
            )

            # Convert the options model to a field
            constructed_options_model = options_model.model_construct()
            options_field = {
                PixivUtilArgs.options_key: (
                    type(constructed_options_model),
                    Field(default=constructed_options_model),
                )
            }

            # Add the field to the job model
            job_validation_info.addField(section_name="nosection", field=options_field)
            job_model = self._generateModel(
                model_name=model_name,
                fields=job_validation_info.getFields(),
                field_validators=job_field_validators,
            )
            self._model_cache["batch_job"] |= {model_name: job_model}
        return self._model_cache["batch_job"][model_name]

    def _createFieldValidators(
        self,
        validation_info: ValidationInfo,
        mode: Literal["before", "after", "plain"] = "after",
        check_fields: bool = True,
    ) -> dict[str, dict[str, field_validator]]:
        """Create field validators for all settings that have a validator callable attached to them.

        Parameters
        ----------
        validation_info : ValidationInfo
            The object containing all the information necessary to create field validators.

        mode : Literal['before', 'after', 'plain'], optional
            Specify the order the field_validator is applied
            in relation to standard Pydantic validation.
            Defaults to "after".

        Returns
        -------
        dict[str, field_validator]
            All field validators possible to create from the supplied ValidationInfo object.
        """
        field_validators = {}
        for section_name, validator_names in validation_info.getValidators().items():
            for validator_name, validator_options in validator_names.items():

                # Get the validator callable
                validator = validator_options["validator"]

                # Creating a field validator requires a separate first field
                first_field = validator_options["settings"][0]
                subsequent_fields = (
                    validator_options["settings"][1:]
                    if len(validator_options["settings"]) > 1
                    else []
                )
                fv = field_validator(
                    first_field,
                    *subsequent_fields,
                    mode=mode,
                    check_fields=check_fields
                )(validator)
                if section_name in field_validators:
                    field_validators[section_name] |= {validator_name: fv}
                else:
                    field_validators |= {section_name: {validator_name: fv}}
        return field_validators

    def _generateModel(
        self,
        model_name: str,
        fields: dict[str, dict[str, tuple]],
        field_validators: dict[str, dict[str, field_validator]],
    ) -> type[BaseModel]:
        nosection_name = iter(fields.keys()).__next__()
        if nosection_name == "nosection":
            # This model has no section. As such, it is composed of a single model
            return create_model(
                model_name,
                **iter(fields.values()).__next__(),
                __validators__=(
                    field_validators[nosection_name]
                    if nosection_name in field_validators
                    else None
                )
            )
        else:
            # Each submodel is tied to a section of the template
            # The full model has each submodel as a field
            full_model_fields = {}
            for section_name, section_fields in fields.items():
                sub_model = create_model(
                    section_name,
                    **section_fields,
                    __validators__=(
                        field_validators[section_name]
                        if section_name in field_validators
                        else None
                    )
                )
                constructed_model = sub_model.model_construct()
                full_model_fields |= {
                    section_name: (
                        type(constructed_model),
                        Field(default=constructed_model),
                    )
                }

            return create_model(model_name, **full_model_fields)
