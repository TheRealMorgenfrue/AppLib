from typing import Literal, Self

from pydantic import BaseModel, Field, create_model, field_validator

from ...tools.types.templates import AnyTemplate
from .template_options.validation_info import FieldTree, ValidationInfo
from .template_parser import TemplateParser


class CoreValidationModelGenerator:
    _instance = None
    # Cache of all created models. Models of the same type are cached only once
    _model_cache = {}

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _create_field_validators(
        self,
        validation_info: ValidationInfo,
        mode: Literal["before", "after", "plain"] = "after",
        check_fields: bool = True,
    ) -> dict[str, dict[str, field_validator]]:
        """
        Create field validators for all settings that have a validator callable attached to them.

        Parameters
        ----------
        validation_info : ValidationInfo
            The object containing all the information necessary to create field validators.

        mode : Literal['before', 'after', 'plain'], optional
            Specify the order the field_validator is applied in relation to standard Pydantic validation.
            By default `after`.

        check_fields : bool, optional
            Whether to check that the fields actually exist on the model.
            By default `True`.

        Returns
        -------
        dict[str, field_validator]
            The field validators.
        """
        field_validators = {}
        for node in validation_info.validators:
            validator = node.validator
            section_id = f"{node.parents[0]}"
            if section_id not in field_validators:
                field_validators[section_id] = {}

            # Creating a field validator requires a separate first field
            first_field = node.keys[0]
            subsequent_fields = node.keys[1:] if len(node.keys) > 1 else []
            fv = field_validator(
                first_field,
                *subsequent_fields,
                mode=mode,
                check_fields=check_fields,
            )(validator)
            field_validators[section_id] |= {f"{validator}": fv}
        return field_validators

    def _generate_model(
        self,
        model_name: str,
        field_tree: FieldTree,
        field_validators: dict[str, dict[str, field_validator]],
    ) -> type[BaseModel]:
        for setting, fields, position, parents in reversed(field_tree):
            section_id = f"{parents}"
            validators = (
                field_validators[section_id] if section_id in field_validators else None
            )
            model = create_model(
                section_id, __validators__=validators, **fields
            ).model_construct()
            field = {parents[-1]: (type(model), Field(default=model))}
            field_tree.merge(setting, field, position, parents)
        return create_model(model_name, **field_tree.dump_fields())

    def get_generic_model(
        self, model_name: str, template: AnyTemplate
    ) -> type[BaseModel]:
        """
        Generate a generic validation model of the supplied template.\n
        This type of model can be used to validate all templates not requiring special care.

        Parameters
        ----------
        model_name : str
            The name of the generated model.

        template : AnyTemplate
            Generate a model of this template.

        Returns
        -------
        type[BaseModel]
            A validation model of the template.
        """
        if "generic" not in self._model_cache:
            self._model_cache |= {"generic": {}}

        if model_name not in self._model_cache["generic"]:
            self.template_parser = TemplateParser()
            self.template_parser.parse(template)
            validation_info = self.template_parser.get_validation_info(model_name)
            model = self._generate_model(
                model_name=model_name,
                field_tree=validation_info.fields,
                field_validators=self._create_field_validators(
                    validation_info=validation_info
                ),
            )
            self._model_cache["generic"] |= {model_name: model}
        return self._model_cache["generic"][model_name]
