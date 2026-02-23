from collections.abc import Callable
from typing import Any, Self, TypeAlias, final

from ....types.general import floatOrInt
from ...runners.converters.converter import Converter


@final
class AppLibUndefinedType:
    """A type used as a sentinel for undefined values."""

    def __copy__(self) -> Self: ...
    def __deepcopy__(self, memo: Any) -> Self: ...


AppLibUndefined: TypeAlias = AppLibUndefinedType


class Option:
    def __init__(
        self,
        default,
        actions: Callable | list[Callable] = AppLibUndefined,
        converter: Converter = AppLibUndefined,
        disable_self: bool = AppLibUndefined,
        max: floatOrInt | None = AppLibUndefined,
        min: floatOrInt | None = AppLibUndefined,
        type: type = AppLibUndefined,
        validators: Callable | list[Callable] = AppLibUndefined,
    ):
        """
        Create an option instance usable in a non-GUI environment.

        An Option is the value of a setting, as defined in the template specification.

        Parameters
        ----------
        default : Any
            The default value for this setting.
        actions : Callable | list[Callable], optional
            Functions to call when this setting changes value.
            Each function must take one argument, which is the new value of this setting.
        converter : Converter, optional
            The value converter used to convert values between config and GUI representation.
            ##### Applicable settings: All
        disable_self : bool, optional
            The value that disables this setting.
            Disabled settings are excluded from command line arguments.
        max : floatOrInt, optional
            The maximum value for this setting.
            If None, there is no limit.
        min : floatOrInt, optional
            The minimum value for this setting.
            If None, there is no limit.
        type : type, optional
            The Python type for the value of this setting. For instance, 3 has type 'int'.

            The final type is a union of:
            - default
            - type
        validators : Callable | list[Callable], optional
            Functions used to validate the value of this setting (in addition to default Pydantic validation).
            Each function must take one argument, which is the value of this setting.
            If the value is invalid, they must raise either ValueError or AssertionError.
        """
        self.default = default
        self.actions = actions
        self.converter = converter
        self.disable_self = disable_self
        self.max = max
        self.min = min
        self.type = type
        self.validators = validators

    def __getattr__(self, name):
        """
        Called when the default attribute access fails with an AttributeError (either __getattribute__()
        raises an AttributeError because `name` is not an instance attribute or an attribute in the class tree
        for self; or __get__() of a `name` property raises AttributeError)
        """
        return AppLibUndefined

    def defined(self, attr_value) -> bool:
        """Returns True if the given attribute is defined."""
        return attr_value != AppLibUndefined
