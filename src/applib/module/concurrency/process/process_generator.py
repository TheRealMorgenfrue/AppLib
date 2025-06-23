from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Any

from ..process.process_base import ProcessBase


class ProcessGenerator(ABC):

    @abstractmethod
    def program(self) -> str:
        """
        Returns
        -------
        str
            The absolute path of the program to run.
        """
        ...

    @abstractmethod
    def args(self) -> Generator[list[str], Any, Any]:
        """Generator that creates arguments to be consumed by a process.

        Yields
        ------
        Generator[list[str], Any, Any]
            All created arguments must be a list of strings.
        """
        ...

    @abstractmethod
    def process(self) -> type[ProcessBase]:
        """The Process class in which the code is run.

        Must be a subclass of `ProcessBase` in order
        to be handled properly by the thread manager.

        Returns
        -------
        type[ProcessBase]
            A reference to the process class.
        """
        ...

    @abstractmethod
    def can_start(self) -> bool:
        """Whether any arguments can be created by the generator.

        Returns
        -------
        bool
            Returns True if the Generator is non-empty.
        """
        ...

    @abstractmethod
    def get_total_progress(self) -> int:
        """Calculates the total amount of processes that can be created by the generator.

        Returns
        -------
        int
            The total amount of processes that can be created by the generator.
        """
        ...
