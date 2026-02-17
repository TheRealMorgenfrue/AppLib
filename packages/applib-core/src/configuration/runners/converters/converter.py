from abc import abstractmethod
from typing import Any


class Converter:
    """The converter base class"""

    @abstractmethod
    def convert(self, value: Any, to_gui: bool = False) -> Any:
        """
        Convert `value` between config and GUI representation.

        Parameters
        ----------
        value : Any
            The value to convert to an appropriate type.

        to_gui : bool, optional
            Convert value to a type suitable for the GUI.
            By default False.

        Returns
        -------
        Any
            `value` converted to a suitable type.
        """
        ...
