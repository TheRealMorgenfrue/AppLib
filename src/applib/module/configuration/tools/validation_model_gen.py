from collections.abc import Callable
from typing import Any, Literal, Self

from pydantic import BaseModel, Field, create_model, field_validator

from applib.module.configuration.tools.search import SEARCH_SEP

from ...tools.types.templates import AnyTemplate
from .template_parser import TemplateParser
from .template_utils.validation_info import ValidationInfo


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
    ):
        """
        Create field validators for all settings that have a validator callable attached to them.

        Parameters
        ----------
        validation_info : ValidationInfo
            The object containing all the information necessary to create field validators.
        mode : Literal['before', 'after', 'plain'], optional
            Specify the order the field_validator is applied in relation to standard Pydantic validation.
            By default 'after'.
        check_fields : bool, optional
            Whether to check that the fields actually exist on the model.
            By default True.

        Returns
        -------
        dict[str, dict[str, Callable]]
            The field validators.

            Structure:
            ```
            {path: {
                validator_name: field_validator
                }
            }
            ```
        """
        field_validators: dict[str, dict[str, Callable]] = {}
        for path, pre_validators in validation_info.raw_validators.items():
            for validator_name, pre_validator in pre_validators.items():
                # Creating a field validator requires a separate first field
                fv = field_validator(
                    pre_validator.get_first_field(),
                    *pre_validator.get_other_fields(),
                    mode=mode,
                    check_fields=check_fields,
                )(pre_validator.validator)

                try:
                    field_validators[path][validator_name] = fv
                except KeyError:
                    field_validators[path] = {validator_name: fv}

        return field_validators

    def _generate_model(
        self,
        model_name: str,
        fields: dict[str, Any],
        field_validators: dict[str, dict[str, Callable]],
    ) -> type[BaseModel]:
        """Generate a Pydantic validation model.

         Recursively constructs submodels for each nested dict in `fields`.

        Parameters
        ----------
        model_name : str
            The name of the model.
        fields : dict[str, Any]
            The fields of the model.
        field_validators : dict[str, dict[str, Callable]]
            The validators of the fields.

        Returns
        -------
        type[BaseModel]
            A Pydantic validation model.
        """
        stack = [(fields, [])]
        visited = set()
        path = []
        while stack:
            current_path = stack[-1][1]
            str_path = f"{SEARCH_SEP}".join(current_path)
            if current_path:
                str_path += SEARCH_SEP
            # Depth-first search until we reach the innermost dict
            for k, v in stack[-1][0].items():
                if visited and f"{str_path}{k}" in visited:
                    continue

                if isinstance(v, dict):
                    stack.append((v, [*current_path, k]))
                    break
            # We've reached the innermost dict. A submodel is created
            else:
                submodel_fields, path = stack.pop()
                if not path:
                    break

                parent_key = path[-1]
                model = create_model(
                    parent_key,
                    __validators__=field_validators.get(
                        f"{SEARCH_SEP}".join(path), None
                    ),
                    **submodel_fields,
                ).model_construct()
                field = (type(model), Field(default=model))
                stack[-1][0][parent_key] = field  # Mutate the input
                visited.add(f"{SEARCH_SEP}".join(path))
        return create_model(
            model_name,
            __validators__=field_validators.get(f"{SEARCH_SEP}".join(path), None),
            **fields,
        )

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
            self._model_cache["generic"] = {}

        if model_name not in self._model_cache["generic"]:
            self.template_parser = TemplateParser()
            self.template_parser.parse(template)
            validation_info = self.template_parser.get_validation_info(model_name)
            model = self._generate_model(
                model_name=model_name,
                fields=validation_info.fields,
                field_validators=self._create_field_validators(
                    validation_info=validation_info
                ),
            )
            self._model_cache["generic"][model_name] = model
        return self._model_cache["generic"][model_name]
