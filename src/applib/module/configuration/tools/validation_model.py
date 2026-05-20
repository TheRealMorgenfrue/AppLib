from typing import Any, Literal, Mapping, Self

from pydantic import BaseModel, ValidationError
from pydantic_core import InitErrorDetails, PydanticCustomError

from ...exceptions import MissingFieldError
from ..mapping_base import MappingBase
from ..tools.template_utils.validation_info import ModelValidationInfo


class CoreValidationModel(BaseModel):
    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

    def _core_check_missing_fields(
        self, raw: Mapping, model: Mapping, error_prefix: str = ""
    ) -> None:
        """
        Compares the raw config object against an instance of Self,
        with default values, for missing sections/settings and vice versa.

        Parameters
        ----------
        raw : Mapping
            The config loaded from a file.

        model : Mapping
            The model associated with `config`.

        error_prefix : str
            Prefix error messages with this string.
            By default `""`.

        Raises
        ------
        MissingFieldError
            If any missing or unknown sections/settings are found.
        """
        all_errors, section_errors, field_errors = [], [], []
        parents = []

        def search_fields(
            config: Mapping,
            model: Mapping,
            search_mode: Literal["missing", "unknown"],
        ) -> None:
            """
            Helper function to keep track of parents while traversing.
            Use `search_mode` to select which type of field to search for.

            Parameters
            ----------
            config : Mapping
                The config loaded from a file.

            model : Mapping
                The model associated with `config`.

            search_mode : Literal["missing", "unknown"]
                Specify which type of field to search for.
            """
            # The mapping to search depth-first in. Should be opposite of validation mapping
            search_dict = model if search_mode == "missing" else config
            # The mapping to compare the search dict against. Should be opposite of search mapping
            validation_dict = config if search_mode == "missing" else model
            for key, value in search_dict.items():
                # The model is still nested (mapping key/value pairs, i.e., sections)
                if isinstance(value, Mapping):
                    if key in validation_dict:  # section exists
                        parents.append(key)
                        next_search = (
                            (config[key], value)
                            if search_mode == "missing"
                            else (value, model[key])
                        )
                        search_fields(*next_search, search_mode=search_mode)
                    else:
                        section_errors.append(
                            f"{search_mode.capitalize()} {f"subsection '{'.'.join(parents)}.{key}'" if parents else f"section '{key}'"}"
                        )
                # We've reached the bottom of the nesting (non-mapping key/value pairs)
                elif key not in validation_dict:
                    if parents:
                        field_errors.append(
                            f"{search_mode.capitalize()} setting '{key}' in {f"section '{parents[0]}'" if len(parents) == 1 else f"subsection '{'.'.join(parents)}'"}"
                        )
                    else:
                        field_errors.append(
                            f"{search_mode.capitalize()} setting '{key}'"
                        )
            else:
                if parents:
                    parents.pop()

        search_fields(raw, model, search_mode="missing")
        search_fields(raw, model, search_mode="unknown")

        # Ensure all section errors are displayed first
        all_errors.extend(section_errors)
        all_errors.extend(field_errors)
        if len(all_errors) > 0:
            if error_prefix:
                all_errors = [f"{error_prefix}: {error}" for error in all_errors]
            raise MissingFieldError(all_errors)

    def _core_validate_compatibility(
        self, model_dump: dict, validation_info: ModelValidationInfo
    ):
        """Performs post-validation validation, ensuring all model Option/value
        pairs are compatible with eachother.

        Parameters
        ----------
        model_dump:
            A validated Stage 3 dict of this model.
        validation_info : ModelValidationInfo
            Validation information required to perform model validation.

        Raises
        ------
        ValidationError
            If the model has incompatible Option/value pairs.
        """
        model_map = MappingBase(model_dump)
        errors: list[InitErrorDetails] = []

        for validator, fields in validation_info.validators.items():
            for field_tuple in fields:
                field_map = {}
                for field in field_tuple:
                    try:
                        field_map[field] = model_map.get_value(field)
                    except KeyError as e:
                        error = PydanticCustomError(
                            "key_error",
                            "Failed to create field map: {e}",
                            {"e": e.args},
                        )
                        details = InitErrorDetails(type=error, input=field)
                        errors.append(details)
                try:
                    validator(**field_map)
                except ValueError as e:
                    details = InitErrorDetails(type=f"{e}", input=field_map)
                    errors.append(details)

        err_len = len(errors)
        if err_len > 0:
            title = f"{err_len} validation error{'' if err_len == 0 else 's'}"
            # TODO: Make applib validation error
            raise ValidationError(errors)

    def core_model_validate(
        self, obj: Any, validation_info: ModelValidationInfo
    ) -> Self:
        """
        Validates an AppLib Pydantic model instance.

        Parameters
        ----------
        obj : Any
            The object to validate.
        validation_info : ModelValidationInfo
            Validation information required to perform model validation.
            Gathered by the template parser.

        Returns
        -------
        Self
            The validated model instance.

        Raises
        ------
        ValidationError
            If the model fails standard Pydantic validation (incl. field validators).

            If the model has incompatible Option/value pairs.
        MissingFieldError
            If any missing or unknown sections/settings are found.
        """
        # Stage 1 & 2: Standard Pydantic validation with field validators
        out = self.model_validate(obj)
        # Stage 3: Missing or superfluous Options
        self._core_check_missing_fields(obj, self.model_dump())
        # Stage 4: Option compatibility validation
        self._core_validate_compatibility(out.model_dump(), validation_info)

        return out
