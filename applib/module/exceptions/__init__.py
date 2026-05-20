from typing import Any, TypedDict


class MissingFieldError(ValueError):
    pass


class InvalidMasterKeyError(KeyError):
    pass


class IniParseError(ValueError):
    pass


class OrphanGroupWarning(RuntimeWarning):
    pass


class CoreValidationErrorDetails(TypedDict):
    type: str
    """
    The type of error that occurred, this is an identifier designed for
    programmatic use that will change rarely or never.

    `type` is unique for each error message, and can hence be used as an identifier to build custom error messages.
    """
    loc: tuple[int | str, ...]
    """Tuple of strings and ints identifying where in the schema the error occurred."""
    msg: str
    """A human readable error message."""
    input: Any
    """The input data at this `loc` that caused the error."""


class CoreValidationError(ValueError):
    def __init__(self, title: str, errors: list[CoreValidationErrorDetails]) -> None:
        self._title = title
        self._errors = errors
        super().__init__()

    @property
    def title(self) -> str:
        """
        The title of the error, as used in the heading of `str(validation_error)`.
        """
        return self._title

    def error_count(self) -> int:
        """Returns the number of errors in the validation error."""
        return len(self._errors)

    def errors(self) -> list[CoreValidationErrorDetails]:
        """
        Details about each error in the validation error.

        Returns:
            A list of [`CoreValidationErrorDetails`][applib.CoreValidationErrorDetails] for each error in the validation error.
        """
        return self._errors

    def __repr__(self) -> str:
        error_count = self.error_count()
        msg = f"{error_count} validation error{'s' if error_count > 1 else ''} for {self.title!r}\n"
        for error in self._errors:
            section = error.get("loc")[0]
            setting = error.get("loc")[1]
            msg += f"{section}.{setting}\n"

            error_type = f"type={error.get('type')}"
            input_value = f"input_value={error.get('input')}"
            input_type = f"input_type={type(error.get('input')).__name__}"
            details = [error_type, input_value, input_type]

            msg += f"  {error.get('msg')} [{', '.join(details)}]\n"
        return msg

    def __str__(self) -> str:
        return repr(self)
