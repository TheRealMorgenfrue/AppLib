from abc import abstractmethod
from typing import Any


class Converter:
    """The converter base class"""

    @abstractmethod
    def convert(self, value: Any, to_gui: bool = False) -> Any:
        """
        Convert `value` between types.
        For instance, converting a string "0" to the number 0.

        Parameters
        ----------
        value : Any
            The value to convert.

        to_gui : bool, optional
            Whether to return the converted value.
            By default False.

        Returns
        -------
        Any
            If `to_gui` is True:
                return `value` converted to the GUI type
            else:
                return `value`
        """
        ...
